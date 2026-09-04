import logging

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from app.config import settings
from app.repositories.password_reset_tokens import (
    create_password_reset_token,
    reset_password_with_token,
)
from app.services.email_service import (
    EmailDeliveryError,
    send_password_reset_email,
)
from app.services.password_reset_tokens import (
    generate_password_reset_token,
    hash_password_reset_token,
)

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
    ForgotPasswordRequest,
    PasswordResetMessageResponse,
    ResetPasswordRequest,
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

logger = logging.getLogger(__name__)

PASSWORD_RESET_REQUEST_MESSAGE = (
    "Se existir uma conta com este e-mail, "
    "enviaremos as instruções de recuperação."
)

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

@router.post(
    "/forgot-password",
    response_model=PasswordResetMessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def forgot_password(
    request: ForgotPasswordRequest,
    db: DatabaseSession,
) -> PasswordResetMessageResponse:
    normalized_email = str(
        request.email,
    ).casefold()

    user = get_user_by_email(
        db,
        normalized_email,
    )

    if user is not None and user.is_active:
        reset_token = (
            generate_password_reset_token()
        )

        token_hash = hash_password_reset_token(
            reset_token,
        )

        expires_at = datetime.now(
            timezone.utc,
        ) + timedelta(
            minutes=(
                settings
                .password_reset_token_expire_minutes
            ),
        )

        create_password_reset_token(
            db,
            user.id,
            token_hash,
            expires_at,
        )

        try:
            send_password_reset_email(
                recipient_email=user.email,
                reset_token=reset_token,
            )
        except EmailDeliveryError:
            logger.exception(
                "Falha ao enviar recuperação "
                "para o usuário %s.",
                user.id,
            )

    return PasswordResetMessageResponse(
        message=PASSWORD_RESET_REQUEST_MESSAGE,
    )

@router.post(
    "/reset-password",
    response_model=PasswordResetMessageResponse,
)
def reset_password(
    request: ResetPasswordRequest,
    db: DatabaseSession,
) -> PasswordResetMessageResponse:
    token_hash = hash_password_reset_token(
        request.token,
    )

    new_password_hash = hash_password(
        request.new_password,
    )

    password_was_reset = (
        reset_password_with_token(
            db,
            token_hash=token_hash,
            new_password_hash=(
                new_password_hash
            ),
        )
    )

    if not password_was_reset:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "O link de recuperação é inválido "
                "ou expirou."
            ),
        )

    return PasswordResetMessageResponse(
        message=(
            "Senha redefinida com sucesso."
        ),
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