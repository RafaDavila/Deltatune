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
    token_version: int,
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
        "token_version": token_version,
    }
    

    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=JWT_ALGORITHM,
    )

def decode_access_token(
    token: str,
) -> tuple[str, int]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[JWT_ALGORITHM],
            options={
                "require": [
                    "sub",
                    "iat",
                    "exp",
                    "type",
                    "token_version",
                ],
            },
        )
    except InvalidTokenError as error:
        raise ValueError(
            "Token inválido.",
        ) from error

    subject = payload.get("sub")
    token_type = payload.get("type")
    token_version = payload.get("token_version")

    if (
        not isinstance(subject, str)
        or token_type != "access"
        or type(token_version) is not int
    ):
        raise ValueError(
            "Token inválido.",
        )

    if token_version < 0:
        raise ValueError(
            "Token inválido.",
        )

    return subject, token_version