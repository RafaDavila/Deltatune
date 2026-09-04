from pydantic import SecretStr, EmailStr
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    database_url: str

    test_database_url: str | None = None

    jwt_secret_key: SecretStr
    jwt_access_token_expire_minutes: int = (60 * 24 * 7)

    brevo_api_key: SecretStr
    email_from_address: EmailStr

    frontend_reset_password_url: str = (
        "http://localhost:5173/redefinir-senha"
    )

    password_reset_token_expire_minutes: int = 30

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()