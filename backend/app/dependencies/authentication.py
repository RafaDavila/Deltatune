from typing import Annotated
from uuid import UUID

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import UserModel
from app.repositories.users import (
    get_user_by_id,
)
from app.services.tokens import (
    decode_access_token,
)


bearer_scheme = HTTPBearer(
    auto_error=False,
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]

BearerCredentials = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(bearer_scheme),
]


def create_authentication_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=(
            "Não foi possível validar "
            "a autenticação."
        ),
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )


def get_current_user(
    credentials: BearerCredentials,
    db: DatabaseSession,
) -> UserModel:
    if credentials is None:
        raise create_authentication_error()

    try:
        subject = decode_access_token(
            credentials.credentials,
        )

        user_id = UUID(subject)
    except ValueError as error:
        raise create_authentication_error() from error

    user = get_user_by_id(
        db,
        user_id,
    )

    if user is None or not user.is_active:
        raise create_authentication_error()

    return user

def get_optional_current_user(
        credentials: BearerCredentials,
        db: DatabaseSession,
) -> UserModel | None:
    if credentials is None:
        return None

    return get_current_user(
        credentials,
        db,
    )

def get_optional_current_user(
        credentials: BearerCredentials,
        db: DatabaseSession,
) -> UserModel | None:
    if credentials is None:
        return None

    return get_current_user(
        credentials,
        db,
    )