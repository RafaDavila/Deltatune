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

class LoginRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    email: EmailStr

    password: str = Field(
        min_length=1,
        max_length=128,
    )


class TokenResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    access_token: str = Field(
        serialization_alias="accessToken",
    )

    token_type: str = Field(
        default="bearer",
        serialization_alias="tokenType",
    )

class ForgotPasswordRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    token: str = Field(
        min_length=40,
        max_length=200,
    )

    new_password: str = Field(
        alias="newPassword",
        min_length=8,
        max_length=128,
    )


class PasswordResetMessageResponse(BaseModel):
    message: str