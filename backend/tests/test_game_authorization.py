import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.repositories.users import create_user
from app.services.passwords import hash_password
from app.services.tokens import create_access_token


@pytest.mark.parametrize(
    "game_mode",
    ["daily", "infinite"],
)
@pytest.mark.parametrize(
    ("authenticated_intruder", "expected_status"),
    [
        (False, 401),
        (True, 404),
    ],
)
def test_rejects_skip_by_non_owner(
    client: TestClient,
    db_session: Session,
    game_mode: str,
    authenticated_intruder: bool,
    expected_status: int,
) -> None:
    password_hash = hash_password("SenhaTeste123!")

    owner = create_user(
        db_session,
        display_name="Dono",
        email="dono@example.com",
        password_hash=password_hash,
    )

    owner_token = create_access_token(
        subject=str(owner.id),
        token_version=owner.token_version,
    )

    owner_headers = {
        "Authorization": f"Bearer {owner_token}",
    }

    intruder_headers: dict[str, str] = {}

    if authenticated_intruder:
        intruder = create_user(
            db_session,
            display_name="Outra pessoa",
            email="outra@example.com",
            password_hash=password_hash,
        )

        intruder_token = create_access_token(
            subject=str(intruder.id),
            token_version=intruder.token_version,
        )

        intruder_headers = {
            "Authorization": f"Bearer {intruder_token}",
        }

    prefix = (
        "/challenges/daily"
        if game_mode == "daily"
        else "/infinite"
    )

    start_response = client.post(
        f"{prefix}/start",
        headers=owner_headers,
    )

    assert start_response.status_code == 201
    started = start_response.json()

    if game_mode == "daily":
        skip_payload = {
            "challengeId": started["challengeId"],
            "sessionId": started["sessionId"],
        }
        resume_path = (
            f"{prefix}/session/{started['sessionId']}"
        )
    else:
        skip_payload = {
            "runId": started["runId"],
            "roundId": started["roundId"],
        }
        resume_path = f"{prefix}/{started['runId']}"

    rejected_response = client.post(
        f"{prefix}/skip",
        json=skip_payload,
        headers=intruder_headers,
    )

    assert rejected_response.status_code == expected_status

    # A tentativa rejeitada não pode consumir uma vida.
    resume_response = client.get(
        resume_path,
        headers=owner_headers,
    )

    assert resume_response.status_code == 200
    assert resume_response.json()["attempts"] == []
    assert (
        resume_response.json()["remainingLives"]
        == started["remainingLives"]
    )

    # O dono continua autorizado a jogar.
    owner_skip_response = client.post(
        f"{prefix}/skip",
        json=skip_payload,
        headers=owner_headers,
    )

    assert owner_skip_response.status_code == 200
    assert (
        owner_skip_response.json()["remainingLives"]
        == started["remainingLives"] - 1
    )