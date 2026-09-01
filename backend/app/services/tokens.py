from datetime import (
    datetime,
    timedelta,
    timezone,
)

import jwt

from app.config import settings


JWT_ALGORITHM = "HS256"


def create_access_token(
    subject: str,
) -> str:
    issued_at = datetime.now(
        timezone.utc,
    )

    expires_at = issued_at + timedelta(
        minutes=(
            settings
            .jwt_access_token_expire_minutes
        ),
    )

    payload = {
        "sub": subject,
        "iat": issued_at,
        "exp": expires_at,
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=JWT_ALGORITHM,
    )