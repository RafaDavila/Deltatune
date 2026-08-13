from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.schemas.challenge import (
    DailyChallengeResponse,
    GuessRequest,
    GuessResponse,
    SkipRequest,
    SkipResponse,
    StartDailyChallengeResponse,
)
from app.services.daily_challenge import (
    get_daily_challenge as get_daily_challenge_service,
)

from app.data.game_sessions import (
    MAX_ATTEMPTS,
    SessionAttempt,
    create_game_session,
    get_game_session,
)

router = APIRouter(
    prefix="/challenges",
    tags=["Challenges"],
)

ATTEMPT_DURATIONS = [0.5, 1, 2, 4, 8, 16]


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
def read_daily_challenge() -> DailyChallengeResponse:
    daily_challenge = get_daily_challenge_service()

    return DailyChallengeResponse(
        challenge_id=daily_challenge.id,
        challenge_number=daily_challenge.number,
        attempt_durations=ATTEMPT_DURATIONS,
        next_reset_at=daily_challenge.next_reset_at,
    )


def normalize_answer(answer: str) -> str:
    return " ".join(answer.casefold().split())


@router.post(
    "/daily/start",
    response_model=StartDailyChallengeResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_daily_challenge() -> StartDailyChallengeResponse:
    daily_challenge = get_daily_challenge_service()

    game_session = create_game_session(
        daily_challenge.id,
    )

    return StartDailyChallengeResponse(
        challenge_id=daily_challenge.id,
        challenge_number=daily_challenge.number,
        attempt_durations=ATTEMPT_DURATIONS,
        next_reset_at=daily_challenge.next_reset_at,
        session_id=game_session.id,
        remaining_lives=game_session.remaining_lives,
        maximum_attempts=MAX_ATTEMPTS,
    )


@router.get(
    "/daily/session/{session_id}",
    response_model=ResumeDailyChallengeResponse,
)
def resume_daily_challenge(
    session_id: str,
) -> ResumeDailyChallengeResponse:
    daily_challenge = get_daily_challenge_service()

    game_session = get_game_session(session_id)

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
        session_id=game_session.id,
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
) -> GuessResponse:
    daily_challenge = get_daily_challenge_service()

    if guess.challenge_id != daily_challenge.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("Este desafio não é mais " "o desafio atual."),
        )

    game_session = get_game_session(
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
        *daily_challenge.song.aliases,
    )

    normalized_guess = normalize_answer(
        guess.answer,
    )

    is_correct = any(
        normalized_guess == normalize_answer(answer) for answer in accepted_answers
    )

    game_session.attempts.append(
        SessionAttempt(
            answer=guess.answer,
            status=("correct" if is_correct else "wrong"),
        )
    )

    if is_correct:
        game_session.won = True
        game_session.finished = True
    else:
        game_session.failed_attempts += 1

        if game_session.remaining_lives == 0:
            game_session.finished = True

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
) -> SkipResponse:
    daily_challenge = get_daily_challenge_service()

    if skip.challenge_id != daily_challenge.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("Este desafio não é mais " "o desafio atual."),
        )

    game_session = get_game_session(
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

    game_session.attempts.append(
        SessionAttempt(
            answer="Pulou",
            status="skipped",
        )
    )
    game_session.failed_attempts += 1

    if game_session.remaining_lives == 0:
        game_session.finished = True

    return SkipResponse(
        challenge_id=daily_challenge.id,
        skipped=True,
        won=False,
        game_finished=game_session.finished,
        attempts_used=len(game_session.attempts),
        remaining_lives=(game_session.remaining_lives),
        song_title=(daily_challenge.song.title if game_session.finished else None),
    )
