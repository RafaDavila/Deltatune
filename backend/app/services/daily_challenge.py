from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo
from app.data.songs import DAILY_ROTATION, SONGS_BY_ID, Song

GAME_TIME_ZONE = ZoneInfo("America/Sao_Paulo")
CHALLENGE_START_DATE = date(2026, 8, 11)

@dataclass(frozen=True)
class DailyChallenge:
    id: str
    number: int
    song: Song
    next_reset_at: datetime

def get_daily_challenge() -> DailyChallenge:
    now = datetime.now(GAME_TIME_ZONE)

    elapsed_days = (
        now.date() - CHALLENGE_START_DATE
    ).days

    challenge_number = max(elapsed_days + 1, 1)

    rotation_index = (
        challenge_number - 1
    ) % len(DAILY_ROTATION)

    song_id = DAILY_ROTATION[rotation_index]
    daily_song = SONGS_BY_ID[song_id]

    tomorrow = now.date() + timedelta(days=1)

    next_reset_at = datetime.combine(
        tomorrow,
        time.min,
        tzinfo=GAME_TIME_ZONE,
    )

    return DailyChallenge(
        id=f"{challenge_number:03d}",
        number=challenge_number,
        song=daily_song,
        next_reset_at=next_reset_at,
    )