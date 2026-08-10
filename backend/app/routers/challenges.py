from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from fastapi import APIRouter
from app.schemas.challenge import DailyChallengeResponse

router = APIRouter(
    prefix="/challenges",
    tags=["Challenges"],
)

GAME_TIME_ZONE = ZoneInfo("America/Sao_Paulo")
ATTEMPT_DURATIONS = [0.5, 1,2,4,8,16]

def calculate_next_reset() -> datetime:
    now = datetime.now(GAME_TIME_ZONE)
    tomorrow = now.date() + timedelta(days=1)

    return datetime.combine(
        tomorrow,
        time.min,
        tzinfo=GAME_TIME_ZONE,
    )

@router.get(
    "/daily",
    response_model=DailyChallengeResponse,
)
def get_daily_challenge() -> DailyChallengeResponse:
    return DailyChallengeResponse(
        challenge_id="001",
        challenge_number=1,
        attempt_durations=ATTEMPT_DURATIONS,
        next_reset_at=calculate_next_reset(),
    )

