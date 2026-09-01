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
    RegisterUserRequest,
    UserResponse,
)
from app.services.passwords import hash_password


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
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