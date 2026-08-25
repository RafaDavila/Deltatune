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
from app.repositories.infinite_games import (
    create_infinite_run,
)
from app.schemas.infinite_game import (
    StartInfiniteGameResponse,
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