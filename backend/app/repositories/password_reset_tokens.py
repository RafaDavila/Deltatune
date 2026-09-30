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


def reset_password_with_token(
    db: Session,
    token_hash: str,
    new_password_hash: str,
    now: datetime | None = None,
) -> bool:
    # Consulta apenas para identificar a conta.
    # A validade será verificada após bloquear o usuário.
    user_id = db.scalar(
        select(PasswordResetTokenModel.user_id)
        .where(
            PasswordResetTokenModel.token_hash == token_hash,
        )
    )

    if user_id is None:
        db.rollback()
        return False

    user = db.scalar(
        select(UserModel)
        .where(UserModel.id == user_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )

    if user is None:
        db.rollback()
        return False

    # Calculado após a espera pelo bloqueio para não
    # aceitar um token que expirou durante essa espera.
    current_time = now or datetime.now(timezone.utc)

    reset_token = db.scalar(
        select(PasswordResetTokenModel)
        .where(
            PasswordResetTokenModel.token_hash == token_hash,
            PasswordResetTokenModel.user_id == user_id,
            PasswordResetTokenModel.used_at.is_(None),
            PasswordResetTokenModel.expires_at > current_time,
        )
        .with_for_update()
        .execution_options(populate_existing=True)
    )

    if reset_token is None:
        db.rollback()
        return False

    if not user.is_active:
        db.execute(
            update(PasswordResetTokenModel)
            .where(
                PasswordResetTokenModel.user_id == user_id,
                PasswordResetTokenModel.used_at.is_(None),
            )
            .values(used_at=current_time)
        )
        db.commit()
        return False

    user.password_hash = new_password_hash

    db.execute(
        update(UserModel)
        .where(UserModel.id == user_id)
        .values(
            token_version=UserModel.token_version + 1,
        )
    )

    # Invalida todos os links pendentes na mesma
    # transação da senha e da revogação dos JWTs.
    db.execute(
        update(PasswordResetTokenModel)
        .where(
            PasswordResetTokenModel.user_id == user_id,
            PasswordResetTokenModel.used_at.is_(None),
        )
        .values(used_at=current_time)
    )

    db.commit()

    return True

def create_password_reset_token(
    db: Session,
    user_id: UUID,
    token_hash: str,
    expires_at: datetime,
) -> PasswordResetTokenModel:
    locked_user_id = db.scalar(
        select(UserModel.id)
        .where(UserModel.id == user_id)
        .with_for_update()
    )

    if locked_user_id is None:
        db.rollback()
        raise ValueError("Usuário não encontrado.")

    now = datetime.now(timezone.utc)

    db.execute(
        update(PasswordResetTokenModel)
        .where(
            PasswordResetTokenModel.user_id == user_id,
            PasswordResetTokenModel.used_at.is_(None),
        )
        .values(used_at=now)
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
    current_time = now or datetime.now(timezone.utc)

    statement = (
        select(PasswordResetTokenModel)
        .where(
            PasswordResetTokenModel.token_hash == token_hash,
            PasswordResetTokenModel.used_at.is_(None),
            PasswordResetTokenModel.expires_at > current_time,
        )
    )

    return db.scalar(statement)