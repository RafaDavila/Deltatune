from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.users import (
    create_user,
    get_user_by_email,
)
from app.schemas.auth import (
    LoginRequest,
    RegisterUserRequest,
    TokenResponse,
    UserResponse,
)
from app.services.passwords import hash_password, verify_password
from app.services.tokens import create_access_token
from app.dependencies.authentication import (get_current_user)
from app.models.user import UserModel


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]

CurrentUser = Annotated[
    UserModel,
    Depends(get_current_user),
]

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    registration: RegisterUserRequest,
    db: DatabaseSession,
) -> UserResponse:
    normalized_email = str(
        registration.email,
    ).casefold()

    existing_user = get_user_by_email(
        db,
        normalized_email,
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Já existe uma conta com este e-mail."
            ),
        )

    password_hash = hash_password(
        registration.password,
    )

    try:
        user = create_user(
            db,
            display_name=registration.display_name,
            email=normalized_email,
            password_hash=password_hash,
        )
    except IntegrityError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Já existe uma conta com este e-mail."
            ),
        ) from error

    return UserResponse.model_validate(user)

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_user(
    credentials: LoginRequest,
    db: DatabaseSession,
) -> TokenResponse:
    normalized_email = str(
        credentials.email,
    ).casefold()

    user = get_user_by_email(
        db,
        normalized_email,
    )

    invalid_credentials = (
        user is None
        or not verify_password(
            credentials.password,
            user.password_hash,
        )
    )

    if invalid_credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta conta está desativada.",
        )

    access_token = create_access_token(
        subject=str(user.id),
    )

    return TokenResponse(
        access_token=access_token,
    )

@router.get(
    "/me",
    response_model=UserResponse,
)
def read_current_user(
    current_user: CurrentUser,
) -> UserResponse:
    return UserResponse.model_validate(
        current_user,
    )