from datetime import datetime
from uuid import UUID
from pydantic import(
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)

class RegisterUserRequest(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    display_name: str = Field(
        alias="displayName",
        min_length=2,
        max_length=60,
    )

    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )

class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: UUID

    display_name: str = Field(
        serialization_alias="displayName",
    )

    email: EmailStr

    is_active: bool = Field(
        serialization_alias="isActive",
    )

    created_at: datetime = Field(
        serialization_alias="createdAt",
    )