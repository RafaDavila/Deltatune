import hashlib
import hmac
import json

from datetime import datetime, timezone
from math import ceil

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.repositories.rate_limits import (
    increment_rate_limit,
)


def enforce_rate_limit(
    db: Session,
    scope: str,
    identifier: str,
    limit: int,
    window_seconds: int,
    now: datetime | None = None,
) -> None:
    if limit <= 0:
        raise ValueError(
            "O limite deve ser maior que zero.",
        )

    current_time = now or datetime.now(
        timezone.utc,
    )

    key_data = json.dumps(
        ["rate-limit", scope, identifier],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")

    secret = (
        settings.jwt_secret_key
        .get_secret_value()
        .encode("utf-8")
    )

    key_hash = hmac.new(
        secret,
        key_data,
        hashlib.sha256,
    ).hexdigest()

    attempts, expires_at = increment_rate_limit(
        db,
        key_hash=key_hash,
        window_seconds=window_seconds,
        now=current_time,
    )

    if attempts <= limit:
        return

    retry_after = max(
        1,
        ceil(
            (
                expires_at - current_time
            ).total_seconds()
        ),
    )

    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=(
            "Muitas solicitações. "
            "Aguarde e tente novamente."
        ),
        headers={
            "Retry-After": str(retry_after),
        },
    )