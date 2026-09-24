from uuid import UUID

from fastapi import HTTPException, status

from app.dependencies.authentication import (
    create_authentication_error,
)
from app.models.user import UserModel


def authorize_game_owner(
    owner_id: UUID | None,
    current_user: UserModel | None,
) -> None:
    # A proteção das partidas de visitantes
    # será acrescentada na próxima etapa.
    if owner_id is None:
        return

    if current_user is None:
        raise create_authentication_error()

    if owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão de partida não encontrada.",
        )