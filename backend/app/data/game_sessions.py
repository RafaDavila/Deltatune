from dataclasses import dataclass, field
from uuid import uuid4
from typing import Literal


MAX_ATTEMPTS = 6

AttemptStatus = Literal[
    "skipped",
    "wrong",
    "correct",
]

@dataclass(frozen=True)
class SessionAttempt:
    answer: str
    status: AttemptStatus

@dataclass
class GameSession:
    id: str
    challenge_id: str
    failed_attempts: int = 0
    finished: bool = False
    won: bool = False
    attempts: list[SessionAttempt] = field(
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
