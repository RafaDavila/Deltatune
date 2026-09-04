from app.services.password_reset_tokens import (
    generate_password_reset_token,
    hash_password_reset_token,
)
from datetime import (
    datetime,
    timedelta,
    timezone,
)

from sqlalchemy.orm import Session

from app.repositories.password_reset_tokens import (
    create_password_reset_token,
    get_active_password_reset_token,
)
from app.repositories.users import create_user


def test_generate_unique_password_reset_tokens() -> None:
    first_token = generate_password_reset_token()
    second_token = generate_password_reset_token()

    assert first_token != second_token
    assert len(first_token) >= 40
    assert len(second_token) >= 40


def test_hash_password_reset_token() -> None:
    token = "token-de-recuperacao"

    first_hash = hash_password_reset_token(
        token,
    )
    second_hash = hash_password_reset_token(
        token,
    )

    assert first_hash == second_hash
    assert first_hash != token
    assert len(first_hash) == 64

def test_replace_previous_password_reset_token(
    db_session: Session,
) -> None:
    user = create_user(
        db_session,
        display_name="Rafael",
        email="rafael@example.com",
        password_hash="hash-de-teste",
    )

    now = datetime.now(
        timezone.utc,
    )

    first_hash = hash_password_reset_token(
        "primeiro-token",
    )
    second_hash = hash_password_reset_token(
        "segundo-token",
    )

    first_token = create_password_reset_token(
        db_session,
        user.id,
        first_hash,
        now + timedelta(minutes=30),
    )

    second_token = create_password_reset_token(
        db_session,
        user.id,
        second_hash,
        now + timedelta(minutes=30),
    )

    db_session.refresh(first_token)

    assert first_token.used_at is not None

    assert get_active_password_reset_token(
        db_session,
        first_hash,
        now,
    ) is None

    active_token = get_active_password_reset_token(
        db_session,
        second_hash,
        now,
    )

    assert active_token is not None
    assert active_token.id == second_token.id


def test_reject_expired_password_reset_token(
    db_session: Session,
) -> None:
    user = create_user(
        db_session,
        display_name="Rafael",
        email="rafael@example.com",
        password_hash="hash-de-teste",
    )

    now = datetime.now(
        timezone.utc,
    )

    token_hash = hash_password_reset_token(
        "token-expirado",
    )

    create_password_reset_token(
        db_session,
        user.id,
        token_hash,
        now - timedelta(minutes=1),
    )

    assert get_active_password_reset_token(
        db_session,
        token_hash,
        now,
    ) is None