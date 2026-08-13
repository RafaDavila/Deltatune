from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

class DailyChallengeResponse(BaseModel):
    challenge_id: str = Field(serialization_alias="challengeId")
    challenge_number: int = Field(serialization_alias="challengeNumber")
    attempt_durations: list[float] = Field(
        serialization_alias="attemptDurations"
    )    
    next_reset_at: datetime = Field(serialization_alias="nextResetAt")

class GuessRequest(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    session_id: str = Field(
        alias="sessionId",
        min_length=36,
        max_length=36,
    )

    challenge_id: str = Field(
        alias="challengeId",
        min_length=3,
        max_length=20,
    )
    answer: str = Field(
        min_length=1,
        max_length=120,
    )

    @field_validator("answer")
    @classmethod
    def validate_answer(cls, value: str) -> str:
        cleaned_answer= " ".join(value.split())

        if not cleaned_answer:
            raise ValueError("O palpite não pode ficar vazio")
        return cleaned_answer
    
class GuessResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    challenge_id: str = Field(
        alias="challengeId",
    )
    correct: bool
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
    song_title: str | None = Field(
        default=None,
        alias="songTitle",
    )

class StartDailyChallengeResponse(
    DailyChallengeResponse
):
    session_id: str = Field(
        serialization_alias="sessionId",
    )
    remaining_lives: int =Field(
        serialization_alias="remainingLives",
    )
    maximum_attempts: int = Field(
        serialization_alias="maximumAttempts",
    )


class SkipRequest(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    session_id: str = Field(
        alias="sessionId",
        min_length=36,
        max_length=36,
    )
    challenge_id: str = Field(
        alias="challengeId",
        min_length=3,
        max_length=20,
    )


class SkipResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    challenge_id: str = Field(
        alias="challengeId",
    )
    skipped: bool
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
    song_title: str | None = Field(
        default=None,
        alias="songTitle",
    )