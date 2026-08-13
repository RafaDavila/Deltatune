from dataclasses import dataclass, field
from uuid import uuid4


MAX_ATTEMPTS = 6


@dataclass
class GameSession:
    id: str
    challenge_id: str
    failed_attempts: int = 0
    finished: bool = False
    won: bool = False
    answers: list[str] = field(
        default_factory=list,
    )

    @property
    def remaining_lives(self) -> int:
        return max(
            MAX_ATTEMPTS - self.failed_attempts,
            0,
        )


GAME_SESSIONS: dict[str, GameSession] = {}


def create_game_session(
    challenge_id: str,
) -> GameSession:
    session = GameSession(
        id=str(uuid4()),
        challenge_id=challenge_id,
    )

    GAME_SESSIONS[session.id] = session

    return session


def get_game_session(
    session_id: str,
) -> GameSession | None:
    return GAME_SESSIONS.get(session_id)