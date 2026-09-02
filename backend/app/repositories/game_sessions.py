from typing import Literal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.game_session import (
    AttemptModel,
    GameSessionModel,
)
from datetime import date

AttemptStatus = Literal[
    "skipped",
    "wrong",
    "correct",
]


def create_game_session(
    db: Session,
    challenge_id: str,
    user_id: UUID | None = None,
) -> GameSessionModel:
    game_session = GameSessionModel(
        challenge_id=challenge_id,
        user_id=user_id,
    )

    db.add(game_session)
    db.commit()
    db.refresh(game_session)

    return game_session


def get_game_session_by_user_and_challenge(
    db: Session,
    user_id: UUID,
    challenge_id: str,
) -> GameSessionModel | None:
    statement = (
        select(GameSessionModel)
        .options(
            selectinload(GameSessionModel.attempts),
        )
        .where(
            GameSessionModel.user_id == user_id,
            GameSessionModel.challenge_id == challenge_id,
        )
    )

    return db.scalar(statement)


def get_game_session(
    db: Session,
    session_id: str,
) -> GameSessionModel | None:
    try:
        parsed_session_id = UUID(session_id)
    except ValueError:
        return None

    statement = (
        select(GameSessionModel)
        .options(
            selectinload(GameSessionModel.attempts),
        )
        .where(
            GameSessionModel.id == parsed_session_id,
        )
    )

    return db.scalar(statement)


def list_game_sessions_by_user_and_period(
    db: Session,
    user_id: UUID,
    start_date: date,
    end_date: date,
) -> list[GameSessionModel]:
    statement = (
        select(GameSessionModel)
        .options(
            selectinload(GameSessionModel.attempts),
        )
        .where(
            GameSessionModel.user_id == user_id,
            GameSessionModel.challenge_id >= start_date.isoformat(),
            GameSessionModel.challenge_id <= end_date.isoformat(),
        )
        .order_by(GameSessionModel.challenge_id)
    )

    return list(
        db.scalars(statement).all(),
    )


def add_attempt(
    db: Session,
    game_session: GameSessionModel,
    answer: str,
    status: AttemptStatus,
) -> AttemptModel:
    attempt = AttemptModel(
        attempt_number=len(game_session.attempts) + 1,
        answer=answer,
        status=status,
    )

    game_session.attempts.append(attempt)

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return attempt
