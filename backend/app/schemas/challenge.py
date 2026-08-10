from datetime import datetime
from pydantic import BaseModel, Field

class DailyChallengeResponse(BaseModel):
    challenge_id: str = Field(serialization_alias="challengeId")
    challenge_number: int = Field(serialization_alias="challengeNumber")
    attempt_durations: list[float] = Field(
        serialization_alias="attemptDurations"
    )    
    next_reset_at: datetime = Field(serialization_alias="nextResetAt")