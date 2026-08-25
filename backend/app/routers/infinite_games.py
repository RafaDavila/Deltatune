from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.game_session import MAX_ATTEMPTS
from app.schemas.infinite_game import (
    StartInfiniteGameResponse,
)

from uuid import UUID
from fastapi.responses import FileResponse
from app.repositories.infinite_games import (
    create_infinite_run,
    get_infinite_round,
    get_infinite_run,
)
from app.services.audio_files import (
    find_audio_file,
)

router = APIRouter(
    prefix="/infinite",
    tags=["Infinite Game"],
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]

ATTEMPT_DURATIONS = [
    0.5,
    1,
    2,
    4,
    8,
    16,
]


@router.post(
    "/start",
    response_model=StartInfiniteGameResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_infinite_game(
    db: DatabaseSession,
) -> StartInfiniteGameResponse:
    try:
        game_run, first_round = (
            create_infinite_run(db)
        )
    except LookupError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=str(error),
        ) from error

    return StartInfiniteGameResponse(
        run_id=game_run.id,
        round_id=first_round.id,
        round_number=first_round.round_number,
        attempt_durations=ATTEMPT_DURATIONS,
        remaining_lives=(
            first_round.remaining_lives
        ),
        maximum_attempts=MAX_ATTEMPTS,
        current_streak=game_run.current_streak,
    )

@router.get(
    "/{run_id}/rounds/{round_id}/audio",
    response_class=FileResponse,
)
def read_infinite_round_audio(
    run_id: UUID,
    round_id: UUID,
    db: DatabaseSession,
) -> FileResponse:
    game_run = get_infinite_run(
        db,
        run_id,
    )

    if game_run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Sessão do modo infinito "
                "não encontrada."
            ),
        )

    game_round = get_infinite_round(
        db,
        round_id,
    )

    if game_round is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Rodada do modo infinito "
                "não encontrada."
            ),
        )

    if game_round.run_id != game_run.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A rodada não pertence "
                "a esta sessão."
            ),
        )

    audio_key = game_round.song.audio_key

    if audio_key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "A rodada atual não possui "
                "um áudio disponível."
            ),
        )

    audio_path = find_audio_file(audio_key)

    if audio_path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Arquivo de áudio "
                "não encontrado."
            ),
        )

    return FileResponse(
        path=audio_path,
        media_type="audio/mpeg",
    )