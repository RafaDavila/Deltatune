from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator


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

class InfiniteRoundRequest(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    run_id: UUID = Field(
        alias="runId",
    )

    round_id: UUID = Field(
        alias="roundId",
    )


class InfiniteGuessRequest(
    InfiniteRoundRequest,
):
    answer: str = Field(
        min_length=1,
        max_length=120,
    )

    @field_validator("answer")
    @classmethod
    def validate_answer(
        cls,
        value: str,
    ) -> str:
        cleaned_answer = " ".join(
            value.split(),
        )

        if not cleaned_answer:
            raise ValueError(
                "O palpite não pode ficar vazio.",
            )

        return cleaned_answer


class InfiniteSkipRequest(
    InfiniteRoundRequest,
):
    pass

class InfiniteNextRequest(
    InfiniteRoundRequest,
):
    pass

class InfiniteRoundResultResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    run_id: UUID = Field(
        alias="runId",
    )

    round_id: UUID = Field(
        alias="roundId",
    )

    won: bool

    game_finished: bool = Field(
        alias="gameFinished",
    )

    attempts_used: int = Field(
        alias="attemptsUsed",
    )

    remaining_lives: int = Field(
        alias="remainingLives",
    )

    current_streak: int = Field(
        alias="currentStreak",
    )

    song_title: str | None = Field(
        default=None,
        alias="songTitle",
    )


class InfiniteGuessResponse(
    InfiniteRoundResultResponse,
):
    correct: bool


class InfiniteSkipResponse(
    InfiniteRoundResultResponse,
):
    skipped: bool

class InfiniteAttemptResponse(BaseModel):
    answer: str
    status: str

class ResumeInfiniteGameResponse(
    StartInfiniteGameResponse,
):
    attempts: list[InfiniteAttemptResponse]

    won: bool

    game_finished: bool = Field(
        serialization_alias="gameFinished",
    )

    song_title: str | None = Field(
        default=None,
        serialization_alias="songTitle",
    )

class InfiniteRecordResponse(BaseModel):
    best_streak: int = Field(
        serialization_alias="bestStreak",
    )