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

def list_songs(
        db:Session,
        chapter: int | None = None,
) -> list[SongModel]:
    statement = select(SongModel)

    if chapter is not None:
        statement = statement.where(
            SongModel.chapter == chapter,
        )

    statement = statement.order_by(
        SongModel.chapter,
        SongModel.id,
    )

    return list(db.scalars(statement))