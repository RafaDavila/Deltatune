from datetime import (
    datetime,
    timedelta,
    timezone,
)

from sqlalchemy.orm import Session

from app.models.rate_limit import RateLimitModel
from app.repositories.rate_limits import (
    increment_rate_limit,
)

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from sqlalchemy import Engine


def test_creates_first_attempt(
    db_session: Session,
) -> None:
    now = datetime(
        2026, 9, 14, 12, 0,
        tzinfo=timezone.utc,
    )

    attempts, expires_at = increment_rate_limit(
        db_session,
        key_hash="a" * 64,
        window_seconds=60,
        now=now,
    )

    assert attempts == 1
    assert expires_at == now + timedelta(seconds=60)

    db_session.expire_all()

    saved = db_session.get(
        RateLimitModel,
        "a" * 64,
    )

    assert saved is not None
    assert saved.attempts == 1
    assert saved.expires_at == expires_at


def test_increments_without_extending_expiration(
    db_session: Session,
) -> None:
    now = datetime(
        2026, 9, 14, 12, 0,
        tzinfo=timezone.utc,
    )

    increment_rate_limit(
        db_session,
        key_hash="a" * 64,
        window_seconds=60,
        now=now,
    )

    attempts, expires_at = increment_rate_limit(
        db_session,
        key_hash="a" * 64,
        window_seconds=60,
        now=now + timedelta(seconds=10),
    )

    assert attempts == 2
    assert expires_at == now + timedelta(seconds=60)


def test_restarts_at_expiration(
    db_session: Session,
) -> None:
    now = datetime(
        2026, 9, 14, 12, 0,
        tzinfo=timezone.utc,
    )

    increment_rate_limit(
        db_session,
        key_hash="a" * 64,
        window_seconds=60,
        now=now,
    )

    attempts, expires_at = increment_rate_limit(
        db_session,
        key_hash="a" * 64,
        window_seconds=60,
        now=now + timedelta(seconds=60),
    )

    assert attempts == 1
    assert expires_at == now + timedelta(seconds=120)


def test_keeps_different_keys_independent(
    db_session: Session,
) -> None:
    now = datetime(
        2026, 9, 14, 12, 0,
        tzinfo=timezone.utc,
    )

    increment_rate_limit(
        db_session,
        key_hash="a" * 64,
        window_seconds=60,
        now=now,
    )

    attempts_a, _ = increment_rate_limit(
        db_session,
        key_hash="a" * 64,
        window_seconds=60,
        now=now,
    )

    attempts_b, _ = increment_rate_limit(
        db_session,
        key_hash="b" * 64,
        window_seconds=60,
        now=now,
    )

    assert attempts_a == 2
    assert attempts_b == 1

def test_counts_concurrent_requests(
    db_session: Session,
) -> None:
    now = datetime(
        2026, 9, 14, 12, 0,
        tzinfo=timezone.utc,
    )

    engine = db_session.get_bind()
    assert isinstance(engine, Engine)

    barrier = Barrier(2)

    def register_attempt() -> int:
        with Session(engine) as session:
            barrier.wait(timeout=10)

            attempts, _ = increment_rate_limit(
                session,
                key_hash="c" * 64,
                window_seconds=60,
                now=now,
            )

            return attempts

    with ThreadPoolExecutor(
        max_workers=2,
    ) as executor:
        first = executor.submit(register_attempt)
        second = executor.submit(register_attempt)

        results = [
            first.result(timeout=20),
            second.result(timeout=20),
        ]

    assert sorted(results) == [1, 2]

    db_session.expire_all()

    saved = db_session.get(
        RateLimitModel,
        "c" * 64,
    )

    assert saved is not None
    assert saved.attempts == 2