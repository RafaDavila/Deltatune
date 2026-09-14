from datetime import (
    datetime,
    timedelta,
    timezone,
)

from sqlalchemy import case
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.rate_limit import RateLimitModel


def increment_rate_limit(
    db: Session,
    key_hash: str,
    window_seconds: int,
    now: datetime | None = None,
) -> tuple[int, datetime]:
    if window_seconds <= 0:
        raise ValueError(
            "O período deve ser maior que zero.",
        )

    current_time = now or datetime.now(
        timezone.utc,
    )

    if current_time.utcoffset() is None:
        raise ValueError(
            "A data deve incluir o fuso horário.",
        )

    new_expiration = current_time + timedelta(
        seconds=window_seconds,
    )

    expired = (
        RateLimitModel.expires_at <= current_time
    )

    statement = (
        insert(RateLimitModel)
        .values(
            key_hash=key_hash,
            attempts=1,
            expires_at=new_expiration,
        )
        .on_conflict_do_update(
            index_elements=[
                RateLimitModel.key_hash,
            ],
            set_={
                "attempts": case(
                    (expired, 1),
                    else_=RateLimitModel.attempts + 1,
                ),
                "expires_at": case(
                    (expired, new_expiration),
                    else_=RateLimitModel.expires_at,
                ),
            },
        )
        .returning(
            RateLimitModel.attempts,
            RateLimitModel.expires_at,
        )
    )

    result = db.execute(statement).one()

    attempts = result.attempts
    expires_at = result.expires_at

    db.commit()

    return attempts, expires_at