from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import UserModel


def get_user_by_email(
    db: Session,
    email: str,
) -> UserModel | None:
    statement = select(
        UserModel,
    ).where(
        UserModel.email == email,
    )

    return db.scalar(statement)


def create_user(
    db: Session,
    display_name: str,
    email: str,
    password_hash: str,
) -> UserModel:
    user = UserModel(
        display_name=display_name,
        email=email,
        password_hash=password_hash,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user