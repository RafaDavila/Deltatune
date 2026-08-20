from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories.songs import list_songs
from app.schemas.song import SongResponse

router = APIRouter(
    prefix="/songs",
    tags=["Songs"],
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]

ChapterFilter = Annotated[
    int | None,
    Query(ge=1, le=7),
]

@router.get(
    "",
    response_model=list[SongResponse],
)
def read_songs(
    db: DatabaseSession,
    chapter: ChapterFilter = None,
) -> list[SongResponse]:
    songs = list_songs(
        db,
        chapter=chapter,
    )
    return [
        SongResponse.model_validate(song)
        for song in songs
    ]