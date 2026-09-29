import pytest

from app.services.guest_game_tokens import (
    generate_guest_game_token,
    hash_guest_game_token,
    verify_guest_game_token,
)


def test_accepts_matching_guest_token() -> None:
    token = generate_guest_game_token()
    stored_hash = hash_guest_game_token(token)

    assert stored_hash != token
    assert verify_guest_game_token(
        token,
        stored_hash,
    )


def test_rejects_token_from_another_game() -> None:
    owner_token = generate_guest_game_token()
    other_token = generate_guest_game_token()

    assert not verify_guest_game_token(
        other_token,
        hash_guest_game_token(owner_token),
    )


@pytest.mark.parametrize(
    "received_token",
    [None, "", "token-invalido"],
)
def test_rejects_missing_or_malformed_token(
    received_token: str | None,
) -> None:
    owner_token = generate_guest_game_token()

    assert not verify_guest_game_token(
        received_token,
        hash_guest_game_token(owner_token),
    )


def test_rejects_game_without_stored_hash() -> None:
    assert not verify_guest_game_token(
        generate_guest_game_token(),
        None,
    )