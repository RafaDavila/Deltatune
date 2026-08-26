from typing import Literal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.infinite_game import (
    InfiniteAttemptModel,
    InfiniteRoundModel,
    InfiniteRunModel,
)
from app.models.song import SongModel

InfiniteAttemptStatus = Literal[
    "skipped",
    "wrong",
    "correct",
]


def create_infinite_run(
    db: Session,
) -> tuple[
    InfiniteRunModel,
    InfiniteRoundModel,
]:
    song = db.scalar(
        select(SongModel)
        .where(
            SongModel.audio_key.is_not(None),
        )
        .order_by(func.random())
        .limit(1),
    )

    if song is None:
        raise LookupError(
            "Nenhuma música disponível.",
        )

    game_run = InfiniteRunModel(
        current_streak=0,
    )

    db.add(game_run)
    db.flush()

    first_round = InfiniteRoundModel(
        game_run=game_run,
        song=song,
        round_number=1,
        cycle_number=1,
    )

    db.add(first_round)
    db.commit()

    db.refresh(game_run)
    db.refresh(first_round)

    return game_run, first_round


def get_infinite_run(
    db: Session,
    run_id: UUID,
) -> InfiniteRunModel | None:
    return db.get(
        InfiniteRunModel,
        run_id,
    )


def get_infinite_round(
    db: Session,
    round_id: UUID,
) -> InfiniteRoundModel | None:
    return db.get(
        InfiniteRoundModel,
        round_id,
    )

def get_latest_infinite_round(
        db:Session,
        run_id: UUID,
) -> InfiniteRoundModel | None:
    statement = (
        select(InfiniteRoundModel)
        .where(
            InfiniteRoundModel.run_id == run_id,
        )
        .order_by(
            InfiniteRoundModel.round_number.desc(),
        )
        .limit(1)
    )

    return db.scalar(statement)

def add_infinite_attempt(
    db: Session,
    game_run: InfiniteRunModel,
    game_round: InfiniteRoundModel,
    answer: str,
    status: InfiniteAttemptStatus,
) -> InfiniteAttemptModel:
    attempt = InfiniteAttemptModel(
        attempt_number=(
            len(game_round.attempts) + 1
        ),
        answer=answer,
        status=status,
    )

    game_round.attempts.append(attempt)

    if status == "correct":
        game_run.current_streak += 1
    elif game_round.remaining_lives == 0:
        game_run.current_streak = 0

    db.add(attempt)
    db.commit()

    db.refresh(attempt)
    db.refresh(game_run)
    db.refresh(game_round)

    return attempt

def create_next_infinite_round(
    db: Session,
    game_run: InfiniteRunModel,
    current_round: InfiniteRoundModel,
) -> InfiniteRoundModel:
    cycle_number = current_round.cycle_number

    used_song_ids = (
        select(InfiniteRoundModel.song_id)
        .where(
            InfiniteRoundModel.run_id
            == game_run.id,
            InfiniteRoundModel.cycle_number
            == cycle_number,
        )
    )

    song = db.scalar(
        select(SongModel)
        .where(
            SongModel.audio_key.is_not(None),
            SongModel.id.not_in(
                used_song_ids,
            ),
        )
        .order_by(func.random())
        .limit(1),
    )

    if song is None:
        cycle_number += 1

        song = db.scalar(
            select(SongModel)
            .where(
                SongModel.audio_key.is_not(None),
            )
            .order_by(func.random())
            .limit(1),
        )

    if song is None:
        raise LookupError(
            "Nenhuma música disponível.",
        )

    next_round = InfiniteRoundModel(
        game_run=game_run,
        song=song,
        round_number=(
            current_round.round_number + 1
        ),
        cycle_number=cycle_number,
    )

    db.add(next_round)
    db.commit()
    db.refresh(next_round)

    return next_round