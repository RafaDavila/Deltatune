from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.challenge import (
    DailyChallengeResponse,
    GuessRequest,
    GuessResponse,
    SkipRequest,
    SkipResponse,
    StartDailyChallengeResponse,
    DailyWeekDayResponse,
    DailyWeekResponse,
)
from app.services.daily_challenge import (
    CHALLENGE_START_DATE,
    GAME_TIME_ZONE,
    get_daily_challenge as get_daily_challenge_service,
    get_week_dates,
)

from typing import Annotated

from sqlalchemy.orm import Session
from app.database import get_db
from app.models.game_session import MAX_ATTEMPTS
from app.repositories.game_sessions import (
    add_attempt,
    create_game_session,
    get_game_session,
    get_game_session_by_user_and_challenge,
    list_game_sessions_by_user_and_period,
)
from fastapi.responses import FileResponse
from app.services.audio_files import (
    find_audio_file,
)
from app.services.answer_normalization import(
    normalize_answer,
)
from app.dependencies.authentication import (
    get_current_user,
    get_optional_current_user,
)
from app.models.user import UserModel

router = APIRouter(
    prefix="/challenges",
    tags=["Challenges"],
)

ATTEMPT_DURATIONS = [0.5, 1, 2, 4, 8, 16]

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]

OptionalCurrentUser = Annotated[
    UserModel | None,
    Depends(get_optional_current_user),
]

CurrentUser = Annotated[
    UserModel,
    Depends(get_current_user),
]



class SessionAttemptResponse(BaseModel):
    answer: str
    status: str


class ResumeDailyChallengeResponse(DailyChallengeResponse):
    session_id: str = Field(serialization_alias="sessionId")
    attempts: list[SessionAttemptResponse]
    remaining_lives: int = Field(serialization_alias="remainingLives")
    maximum_attempts: int = Field(serialization_alias="maximumAttempts")
    won: bool
    game_finished: bool = Field(serialization_alias="gameFinished")
    song_title: str | None = Field(
        default=None,
        serialization_alias="songTitle",
    )


@router.get(
    "/daily",
    response_model=DailyChallengeResponse,
)
def read_daily_challenge(
    db: DatabaseSession,
) -> DailyChallengeResponse:
    daily_challenge = get_daily_challenge_service(db)

    return DailyChallengeResponse(
        challenge_id=daily_challenge.id,
        challenge_number=daily_challenge.number,
        attempt_durations=ATTEMPT_DURATIONS,
        next_reset_at=daily_challenge.next_reset_at,
    )

@router.get(
    "/daily/week",
    response_model=DailyWeekResponse,
)
def read_daily_week(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> DailyWeekResponse:
    today = datetime.now(
        GAME_TIME_ZONE,
    ).date()

    week_dates = get_week_dates(today)

    sessions = (
        list_game_sessions_by_user_and_period(
            db,
            current_user.id,
            week_dates[0],
            week_dates[-1],
        )
    )

    sessions_by_challenge = {
        session.challenge_id: session
        for session in sessions
    }

    days: list[DailyWeekDayResponse] = []

    for challenge_date in week_dates:
        challenge_id = challenge_date.isoformat()

        game_session = sessions_by_challenge.get(
            challenge_id,
        )

        if (
            challenge_date < CHALLENGE_START_DATE
            or challenge_date > today
        ):
            day_status = "unavailable"
        elif game_session is None:
            day_status = "not_played"
        elif game_session.won:
            day_status = "won"
        elif game_session.finished:
            day_status = "lost"
        else:
            day_status = "in_progress"

        challenge_number = max(
            (
                challenge_date
                - CHALLENGE_START_DATE
            ).days + 1,
            1,
        )

        days.append(
            DailyWeekDayResponse(
                challenge_id=challenge_id,
                challenge_number=challenge_number,
                status=day_status,
                attempts_used=(
                    len(game_session.attempts)
                    if game_session is not None
                    else 0
                ),
                session_id=(
                    str(game_session.id)
                    if game_session is not None
                    else None
                ),
            )
        )

    return DailyWeekResponse(
        days=days,
    )

@router.get(
    "/daily/audio",
    response_class=FileResponse,
)
def read_daily_audio(
    db: DatabaseSession,
) -> FileResponse:
    daily_challenge = get_daily_challenge_service(db)

    audio_key = daily_challenge.song.audio_key

    if audio_key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=("O desafio atual não possui " "um áudio disponível."),
        )

    audio_path = find_audio_file(audio_key)

    if audio_path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo de áudio não encontrado.",
        )

    return FileResponse(
        path=audio_path,
        media_type="audio/mpeg",
    )

@router.post(
    "/daily/start",
    response_model=StartDailyChallengeResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_daily_challenge(
    db: DatabaseSession,
    current_user: OptionalCurrentUser,
) -> StartDailyChallengeResponse:
    daily_challenge = get_daily_challenge_service(db)

    game_session = None

    if current_user is not None:
        game_session = (
            get_game_session_by_user_and_challenge(
                db,
                current_user.id,
                daily_challenge.id,
            )
        )

    if game_session is None:
        game_session = create_game_session(
            db,
            daily_challenge.id,
            user_id=(
                current_user.id
                if current_user is not None
                else None
            ),
        )

    return StartDailyChallengeResponse(
        challenge_id=daily_challenge.id,
        challenge_number=daily_challenge.number,
        attempt_durations=ATTEMPT_DURATIONS,
        next_reset_at=daily_challenge.next_reset_at,
        session_id=str(game_session.id),
        remaining_lives=game_session.remaining_lives,
        maximum_attempts=MAX_ATTEMPTS,
    )


@router.get(
    "/daily/session/{session_id}",
    response_model=ResumeDailyChallengeResponse,
)
def resume_daily_challenge(
    session_id: str,
    db: DatabaseSession,
) -> ResumeDailyChallengeResponse:
    daily_challenge = get_daily_challenge_service(db)

    game_session = get_game_session(db, session_id)

    if game_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão de partida não encontrada.",
        )

    if game_session.challenge_id != daily_challenge.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("A sessão pertence a outro desafio."),
        )

    return ResumeDailyChallengeResponse(
        challenge_id=daily_challenge.id,
        challenge_number=daily_challenge.number,
        attempt_durations=ATTEMPT_DURATIONS,
        next_reset_at=daily_challenge.next_reset_at,
        session_id=str(game_session.id),
        attempts=[
            SessionAttemptResponse(
                answer=attempt.answer,
                status=attempt.status,
            )
            for attempt in game_session.attempts
        ],
        remaining_lives=(game_session.remaining_lives),
        maximum_attempts=MAX_ATTEMPTS,
        won=game_session.won,
        game_finished=game_session.finished,
        song_title=(daily_challenge.song.title if game_session.finished else None),
    )


@router.post(
    "/daily/guess",
    response_model=GuessResponse,
)
def submit_daily_guess(
    guess: GuessRequest,
    db: DatabaseSession,
) -> GuessResponse:
    daily_challenge = get_daily_challenge_service(db)

    if guess.challenge_id != daily_challenge.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("Este desafio não é mais " "o desafio atual."),
        )

    game_session = get_game_session(
        db,
        guess.session_id,
    )

    if game_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão de partida não encontrada.",
        )

    if game_session.challenge_id != daily_challenge.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("A sessão pertence a outro desafio."),
        )

    if game_session.finished:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta partida já foi finalizada.",
        )

    accepted_answers = (
        daily_challenge.song.title,
        *(song_alias.alias for song_alias in daily_challenge.song.aliases),
    )

    normalized_guess = normalize_answer(
        guess.answer,
    )

    already_guessed = any(
        attempt.status != "skipped"
        and normalize_answer(attempt.answer) == normalized_guess
        for attempt in game_session.attempts
    )


    if already_guessed:
        raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Você já tentou essa música.",
    )

    is_correct = any(
        normalized_guess == normalize_answer(answer) for answer in accepted_answers
    )

    add_attempt(
        db,
        game_session,
        answer=guess.answer,
        status=("correct" if is_correct else "wrong"),
    )

    return GuessResponse(
        challenge_id=daily_challenge.id,
        correct=is_correct,
        won=game_session.won,
        game_finished=game_session.finished,
        attempts_used=len(game_session.attempts),
        remaining_lives=(game_session.remaining_lives),
        song_title=(daily_challenge.song.title if game_session.finished else None),
    )


@router.post(
    "/daily/skip",
    response_model=SkipResponse,
)
def skip_daily_guess(
    skip: SkipRequest,
    db: DatabaseSession,
) -> SkipResponse:
    daily_challenge = get_daily_challenge_service(db)

    if skip.challenge_id != daily_challenge.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("Este desafio não é mais " "o desafio atual."),
        )

    game_session = get_game_session(
        db,
        skip.session_id,
    )

    if game_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão de partida não encontrada.",
        )

    if game_session.challenge_id != daily_challenge.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("A sessão pertence a outro desafio."),
        )

    if game_session.finished:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta partida já foi finalizada.",
        )

    add_attempt(
        db,
        game_session,
        answer="Pulou",
        status="skipped",
    )

    return SkipResponse(
        challenge_id=daily_challenge.id,
        skipped=True,
        won=False,
        game_finished=game_session.finished,
        attempts_used=len(game_session.attempts),
        remaining_lives=(game_session.remaining_lives),
        song_title=(daily_challenge.song.title if game_session.finished else None),
    )
