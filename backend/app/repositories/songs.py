from sqlalchemy import select
from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.models.song import SongModel


def get_song_by_id(
    db: Session,
    song_id: int,
) -> SongModel | None:
    statement = (
        select(SongModel)
        .options(
            selectinload(SongModel.aliases),
        )
        .where(SongModel.id == song_id)
    )

    return db.scalar(statement)