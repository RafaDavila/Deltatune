from fastapi import APIRouter, HTTPException, status

from app.schemas.challenge import DailyChallengeResponse, GuessRequest, GuessResponse
from app.services.daily_challenge import (
    get_daily_challenge as get_daily_challenge_service,
)


router = APIRouter(
    prefix="/challenges",
    tags=["Challenges"],
)

ATTEMPT_DURATIONS = [0.5, 1, 2, 4, 8, 16]


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
    return " ".join(
        answer.casefold().split()
    )

@router.post(
    "/daily/guess",
    response_model=GuessResponse,
)
def submit_daily_guess(
    guess:GuessRequest,
) -> GuessResponse:
    daily_challenge = get_daily_challenge_service()

    if guess.challenge_id != daily_challenge.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este desafio não é mais o desafio atual.",
        )
    accepted_answers = (
        daily_challenge.song.title,
        *daily_challenge.song.aliases,
    )

    normalized_guess = normalize_answer(guess.answer)

    is_correct = any(
        normalized_guess == normalize_answer(answer)
        for answer in accepted_answers
    )

    return GuessResponse(
        challenge_id=daily_challenge.id,
        correct=is_correct,
        song_title=(
            daily_challenge.song.title
            if is_correct
            else None
        ),
    )