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
    challenge_id: str = Field(alias="challengeId")
    correct: bool
    song_title: str | None = Field(
        default=None,
        alias="songTitle",
    )
