from hashlib import sha256
from secrets import token_urlsafe


PASSWORD_RESET_TOKEN_BYTES = 32


def generate_password_reset_token() -> str:
    return token_urlsafe(
        PASSWORD_RESET_TOKEN_BYTES,
    )


def hash_password_reset_token(
    token: str,
) -> str:
    return sha256(
        token.encode("utf-8"),
    ).hexdigest()