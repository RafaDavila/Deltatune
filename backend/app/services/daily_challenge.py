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
CHALLENGE_START_DATE = date(2026, 8, 23)
DAILY_ROTATION = (
    # Capítulo 1
    7,  # Beginning
    8,  # The Legend
    9,  # Lancer
    1,  # Rude Buster
    10,  # Empty Town
    2,  # Field of Hopes and Dreams
    11,  # Scarlet Forest
    12,  # Vs. Susie
    13,  # Rouxls Kaard
    14,  # Chaos King
    3,  # The World Revolving
    15,  # A Town Called Hometown
    16,  # Don't Forget
    # Capítulo 2
    17,  # My Castle Town
    4,  # A Cyber's World?
    18,  # Cyber Battle
    19,  # Smart Race
    20,  # Spamton
    21,  # Pandora Palace
    22,  # Lost Girl
    5,  # Attack of the Killer Queen
    6,  # BIG SHOT
    23,  # sans.
    # Capítulo 3
    24,  # Flashback
    25,  # Ruder Buster
    26,  # Welcome to the Green Room
    27,  # Raise Up Your Bat
    28,  # Glowing Snow
    29,  # TV WORLD
    30,  # It's TV Time!
    31,  # Black Knife
    32,  # NORTHERNLIGHT
    33,  # GLACEIR
    34,  # BURNING EYES
    # Capítulo 4
    35,  # Another day in hometown
    36,  # Castle Funk
    37,  # Dark Sanctuary
    38,  # From Now On (Battle 2)
    39,  # Gyaa Ha ha!
    40,  # A DARK ZONE
    41,  # Ever Higher
    42,  # Hammer of Justice
    43,  # The Third Sanctuary
    44,  # GUARDIAN
    45,  # Need a hand!?
    46,  # The place where it rained
    47,  # Neverending Night
    48,  # Air Waves
)


@dataclass(frozen=True)
class DailyChallenge:
    id: str
    number: int
    song: SongModel
    next_reset_at: datetime


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
