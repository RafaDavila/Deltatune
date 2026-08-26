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

from app.repositories.infinite_games import (
    add_infinite_attempt,
    create_infinite_run,
    get_infinite_round,
    get_infinite_run,
)
from app.schemas.infinite_game import (
    InfiniteGuessRequest,
    InfiniteGuessResponse,
    InfiniteNextRequest,
    InfiniteSkipRequest,
    InfiniteSkipResponse,
    InfiniteAttemptResponse,
    ResumeInfiniteGameResponse,
    StartInfiniteGameResponse,
)
from app.services.answer_normalization import (
    normalize_answer,
)
from app.models.infinite_game import (
    InfiniteRoundModel,
    InfiniteRunModel,
)

from app.repositories.infinite_games import (
    add_infinite_attempt,
    create_infinite_run,
    create_next_infinite_round,
    get_infinite_round,
    get_infinite_run,
    get_latest_infinite_round,
)

router = APIRouter(
    prefix="/infinite",
    tags=["Infinite Game"],
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]

def get_validated_infinite_round(
    db: Session,
    run_id: UUID,
    round_id: UUID,
) -> tuple[
    InfiniteRunModel,
    InfiniteRoundModel,
]:
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

    return game_run, game_round

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
    _, game_round = get_validated_infinite_round(
        db,
        run_id,
        round_id,
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

@router.post(
    "/guess",
    response_model=InfiniteGuessResponse,
)
def submit_infinite_guess(
    guess: InfiniteGuessRequest,
    db: DatabaseSession,
) -> InfiniteGuessResponse:
    game_run, game_round = (
        get_validated_infinite_round(
            db,
            guess.run_id,
            guess.round_id,
        )
    )

    if game_round.finished:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Esta rodada já foi finalizada."
            ),
        )

    normalized_guess = normalize_answer(
        guess.answer,
    )

    already_guessed = any(
        attempt.status != "skipped"
        and normalize_answer(attempt.answer)
        == normalized_guess
        for attempt in game_round.attempts
    )

    if already_guessed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Você já tentou essa música."
            ),
        )

    accepted_answers = (
        game_round.song.title,
        *(
            song_alias.alias
            for song_alias
            in game_round.song.aliases
        ),
    )

    is_correct = any(
        normalized_guess
        == normalize_answer(answer)
        for answer in accepted_answers
    )

    add_infinite_attempt(
        db,
        game_run,
        game_round,
        answer=guess.answer,
        status=(
            "correct"
            if is_correct
            else "wrong"
        ),
    )

    return InfiniteGuessResponse(
        run_id=game_run.id,
        round_id=game_round.id,
        correct=is_correct,
        won=game_round.won,
        game_finished=game_round.finished,
        attempts_used=len(game_round.attempts),
        remaining_lives=(
            game_round.remaining_lives
        ),
        current_streak=(
            game_run.current_streak
        ),
        song_title=(
            game_round.song.title
            if game_round.finished
            else None
        ),
    )

@router.post(
    "/skip",
    response_model=InfiniteSkipResponse,
)
def skip_infinite_guess(
    skip: InfiniteSkipRequest,
    db: DatabaseSession,
) -> InfiniteSkipResponse:
    game_run, game_round = (
        get_validated_infinite_round(
            db,
            skip.run_id,
            skip.round_id,
        )
    )

    if game_round.finished:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Esta rodada já foi finalizada."
            ),
        )

    add_infinite_attempt(
        db,
        game_run,
        game_round,
        answer="Pulou",
        status="skipped",
    )

    return InfiniteSkipResponse(
        run_id=game_run.id,
        round_id=game_round.id,
        skipped=True,
        won=game_round.won,
        game_finished=game_round.finished,
        attempts_used=len(game_round.attempts),
        remaining_lives=(
            game_round.remaining_lives
        ),
        current_streak=(
            game_run.current_streak
        ),
        song_title=(
            game_round.song.title
            if game_round.finished
            else None
        ),
    )

@router.post(
    "/next",
    response_model=StartInfiniteGameResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_next_infinite_round(
    request: InfiniteNextRequest,
    db: DatabaseSession,
) -> StartInfiniteGameResponse:
    game_run, current_round = (
        get_validated_infinite_round(
            db,
            request.run_id,
            request.round_id,
        )
    )

    if not current_round.finished:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A rodada atual ainda não "
                "foi finalizada."
            ),
        )

    latest_round = get_latest_infinite_round(
        db,
        game_run.id,
    )

    if (
        latest_round is None
        or latest_round.id != current_round.id
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Esta não é a rodada atual "
                "da sessão."
            ),
        )

    try:
        next_round = create_next_infinite_round(
            db,
            game_run,
            current_round,
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
        round_id=next_round.id,
        round_number=next_round.round_number,
        attempt_durations=ATTEMPT_DURATIONS,
        remaining_lives=(
            next_round.remaining_lives
        ),
        maximum_attempts=MAX_ATTEMPTS,
        current_streak=game_run.current_streak,
    )

@router.get(
    "/{run_id}",
    response_model=ResumeInfiniteGameResponse,
)
def resume_infinite_game(
    run_id: UUID,
    db: DatabaseSession,
) -> ResumeInfiniteGameResponse:
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

    game_round = get_latest_infinite_round(
        db,
        game_run.id,
    )

    if game_round is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "A sessão não possui rodadas."
            ),
        )

    return ResumeInfiniteGameResponse(
        run_id=game_run.id,
        round_id=game_round.id,
        round_number=game_round.round_number,
        attempt_durations=ATTEMPT_DURATIONS,
        remaining_lives=(
            game_round.remaining_lives
        ),
        maximum_attempts=MAX_ATTEMPTS,
        current_streak=game_run.current_streak,
        attempts=[
            InfiniteAttemptResponse(
                answer=attempt.answer,
                status=attempt.status,
            )
            for attempt in game_round.attempts
        ],
        won=game_round.won,
        game_finished=game_round.finished,
        song_title=(
            game_round.song.title
            if game_round.finished
            else None
        ),
    )