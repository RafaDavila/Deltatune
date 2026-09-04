from datetime import (
    datetime,
    timezone,
)
from uuid import UUID

from sqlalchemy import (
    select,
    update,
)
from sqlalchemy.orm import Session

from app.models.password_reset_token import (
    PasswordResetTokenModel,
)

from app.models.user import UserModel


def create_password_reset_token(
    db: Session,
    user_id: UUID,
    token_hash: str,
    expires_at: datetime,
) -> PasswordResetTokenModel:
    now = datetime.now(
        timezone.utc,
    )

    db.execute(
        update(PasswordResetTokenModel)
        .where(
            PasswordResetTokenModel.user_id
            == user_id,
            PasswordResetTokenModel.used_at
            .is_(None),
        )
        .values(
            used_at=now,
        )
    )

    reset_token = PasswordResetTokenModel(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    db.add(reset_token)
    db.commit()
    db.refresh(reset_token)

    return reset_token


def get_active_password_reset_token(
    db: Session,
    token_hash: str,
    now: datetime | None = None,
) -> PasswordResetTokenModel | None:
    current_time = now or datetime.now(
        timezone.utc,
    )

    statement = (
        select(PasswordResetTokenModel)
        .where(
            PasswordResetTokenModel.token_hash
            == token_hash,
            PasswordResetTokenModel.used_at
            .is_(None),
            PasswordResetTokenModel.expires_at
            > current_time,
        )
    )

    return db.scalar(statement)

def reset_password_with_token(
    db: Session,
    token_hash: str,
    new_password_hash: str,
    now: datetime | None = None,
) -> bool:
    current_time = now or datetime.now(
        timezone.utc,
    )

    statement = (
        select(PasswordResetTokenModel)
        .where(
            PasswordResetTokenModel.token_hash
            == token_hash,
            PasswordResetTokenModel.used_at
            .is_(None),
            PasswordResetTokenModel.expires_at
            > current_time,
        )
        .with_for_update()
    )

    reset_token = db.scalar(statement)

    if reset_token is None:
        return False

    user = db.get(
        UserModel,
        reset_token.user_id,
    )

    if user is None or not user.is_active:
        reset_token.used_at = current_time
        db.commit()

        return False

    user.password_hash = new_password_hash
    reset_token.used_at = current_time

    db.add(user)
    db.add(reset_token)
    db.commit()

    return True