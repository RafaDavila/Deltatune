from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.rate_limits import (
    enforce_rate_limit,
)


def test_allows_limit_and_rejects_next_request(
    db_session: Session,
) -> None:
    now = datetime(
        2026, 9, 14, 12, 0,
        tzinfo=timezone.utc,
    )

    for _ in range(2):
        enforce_rate_limit(
            db_session,
            scope="login-ip",
            identifier="192.0.2.1",
            limit=2,
            window_seconds=60,
            now=now,
        )

    with pytest.raises(HTTPException) as captured:
        enforce_rate_limit(
            db_session,
            scope="login-ip",
            identifier="192.0.2.1",
            limit=2,
            window_seconds=60,
            now=now + timedelta(seconds=10),
        )

    assert captured.value.status_code == 429
    assert captured.value.headers == {
        "Retry-After": "50",
    }


def test_blocked_requests_do_not_extend_wait(
    db_session: Session,
) -> None:
    now = datetime(
        2026, 9, 14, 12, 0,
        tzinfo=timezone.utc,
    )

    enforce_rate_limit(
        db_session,
        scope="login-ip",
        identifier="192.0.2.1",
        limit=1,
        window_seconds=60,
        now=now,
    )

    for elapsed, expected_wait in [
        (10, "50"),
        (20, "40"),
    ]:
        with pytest.raises(HTTPException) as captured:
            enforce_rate_limit(
                db_session,
                scope="login-ip",
                identifier="192.0.2.1",
                limit=1,
                window_seconds=60,
                now=now + timedelta(seconds=elapsed),
            )

        assert captured.value.status_code == 429
        assert captured.value.headers == {
            "Retry-After": expected_wait,
        }

    enforce_rate_limit(
        db_session,
        scope="login-ip",
        identifier="192.0.2.1",
        limit=1,
        window_seconds=60,
        now=now + timedelta(seconds=60),
    )


def test_keeps_scopes_and_identifiers_independent(
    db_session: Session,
) -> None:
    now = datetime(
        2026, 9, 14, 12, 0,
        tzinfo=timezone.utc,
    )

    for scope, identifier in [
        ("login-ip", "192.0.2.1"),
        ("login-ip", "192.0.2.2"),
        ("forgot-password-ip", "192.0.2.1"),
    ]:
        enforce_rate_limit(
            db_session,
            scope=scope,
            identifier=identifier,
            limit=1,
            window_seconds=60,
            now=now,
        )