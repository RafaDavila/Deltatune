from uuid import UUID

from fastapi import HTTPException, status

from app.dependencies.authentication import (
    create_authentication_error,
)
from app.models.user import UserModel
from app.services.guest_game_tokens import (
    verify_guest_game_token,
)


def authorize_game_owner(
    owner_id: UUID | None,
    current_user: UserModel | None,
    *,
    guest_token: str | None,
    guest_token_hash: str | None,
) -> None:
    if owner_id is None:
        if not verify_guest_game_token(
            guest_token,
            guest_token_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sessão de partida não encontrada.",
            )

        return

    if current_user is None:
        raise create_authentication_error()

    if owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão de partida não encontrada.",
        )