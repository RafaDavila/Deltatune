from typing import Literal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.game_session import (
    AttemptModel,
    GameSessionModel,
)


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