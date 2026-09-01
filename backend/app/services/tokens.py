from datetime import (
    datetime,
    timedelta,
    timezone,
)

import jwt 
from jwt import InvalidTokenError

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

def decode_access_token(
    token: str,
) -> str:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[JWT_ALGORITHM],
        )
    except InvalidTokenError as error:
        raise ValueError(
            "Token inválido.",
        ) from error

    subject = payload.get("sub")
    token_type = payload.get("type")

    if (
        not isinstance(subject, str)
        or token_type != "access"
    ):
        raise ValueError(
            "Token inválido.",
        )

    return subject