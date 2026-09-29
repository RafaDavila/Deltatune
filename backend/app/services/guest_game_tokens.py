import hashlib
import secrets


def generate_guest_game_token() -> str:
    return secrets.token_urlsafe(32)


def hash_guest_game_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8"),
    ).hexdigest()

def verify_guest_game_token(
    token: str | None,
    stored_hash: str | None,
) -> bool:
    if (
        token is None
        or stored_hash is None
        or len(token) != 43
    ):
        return False

    received_hash = hash_guest_game_token(token)

    return secrets.compare_digest(
        received_hash,
        stored_hash,
    )