from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.infinite_game import (
    InfiniteRoundModel,
    InfiniteRunModel,
)
from app.models.song import SongModel


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