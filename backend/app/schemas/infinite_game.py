from uuid import UUID

from pydantic import BaseModel, Field


class StartInfiniteGameResponse(BaseModel):
    run_id: UUID = Field(
        serialization_alias="runId",
    )

    round_id: UUID = Field(
        serialization_alias="roundId",
    )

    round_number: int = Field(
        serialization_alias="roundNumber",
    )

    attempt_durations: list[float] = Field(
        serialization_alias="attemptDurations",
    )

    remaining_lives: int = Field(
        serialization_alias="remainingLives",
    )

    maximum_attempts: int = Field(
        serialization_alias="maximumAttempts",
    )

    current_streak: int = Field(
        serialization_alias="currentStreak",
    )