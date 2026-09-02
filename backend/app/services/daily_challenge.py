from dataclasses import dataclass
from datetime import (
    date,
    datetime,
    time,
    timedelta,
)
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.models.song import SongModel
from app.repositories.songs import get_song_by_id

GAME_TIME_ZONE = ZoneInfo("America/Sao_Paulo")
CHALLENGE_START_DATE = date(2026, 8, 24)
DAILY_ROTATION = (
    1, 11, 21, 20, 2, 40, 49, 7, 54, 10,
    25, 42, 51, 6, 26, 23, 43, 28, 34, 33,
    36, 37, 12, 9, 53, 16, 48, 35, 14, 55,
    18, 24, 17, 45, 19, 47, 41, 52, 56, 57,
    39, 5, 15, 58, 29, 13, 46, 38, 3, 32,
    50, 30, 8, 27, 4, 44, 22, 31,
)


@dataclass(frozen=True)
class DailyChallenge:
    id: str
    number: int
    song: SongModel
    next_reset_at: datetime

def get_week_dates (
        reference_date: date,
)-> tuple[date, ...]:
    days_since_sunday = (
        reference_date.weekday() + 1
    ) % 7

    week_start = reference_date - timedelta(days=days_since_sunday)

    return tuple(
        week_start + timedelta(days=offset)
        for offset in range(7)
    )

def get_daily_challenge(
    db: Session,
) -> DailyChallenge:
    now = datetime.now(GAME_TIME_ZONE)

    elapsed_days = (now.date() - CHALLENGE_START_DATE).days

    challenge_number = max(
        elapsed_days + 1,
        1,
    )

    rotation_index = (challenge_number - 1) % len(DAILY_ROTATION)

    song_id = DAILY_ROTATION[rotation_index]
    daily_song = get_song_by_id(db, song_id)

    if daily_song is None:
        raise RuntimeError(
            f"Música da rotação não encontrada: {song_id}",
        )

    tomorrow = now.date() + timedelta(days=1)

    next_reset_at = datetime.combine(
        tomorrow,
        time.min,
        tzinfo=GAME_TIME_ZONE,
    )

    return DailyChallenge(
        id=now.date().isoformat(),
        number=challenge_number,
        song=daily_song,
        next_reset_at=next_reset_at,
    )
