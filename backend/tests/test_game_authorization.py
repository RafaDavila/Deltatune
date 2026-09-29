import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.repositories.users import create_user
from app.services.passwords import hash_password
from app.services.tokens import create_access_token
from uuid import UUID

from app.models.infinite_game import InfiniteRoundModel


@pytest.mark.parametrize("action", ["skip", "guess"])

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
def test_rejects_game_access_by_non_owner(
    client: TestClient,
    db_session: Session,
    game_mode: str,
    authenticated_intruder: bool,
    expected_status: int,
    action: str,
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
        request_payload = {
            "challengeId": started["challengeId"],
            "sessionId": started["sessionId"],
        }
        resume_path = (
            f"{prefix}/session/{started['sessionId']}"
        )
    else:
        request_payload = {
            "runId": started["runId"],
            "roundId": started["roundId"],
        }
        resume_path = f"{prefix}/{started['runId']}"

    if action == "guess":
        request_payload["answer"] = "Música que não existe"
    rejected_response = client.post(
        f"{prefix}/{action}",
        json=request_payload,
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
    owner_response = client.post(
        f"{prefix}/{action}",
        json=request_payload,
        headers=owner_headers,
    )

        # Outra pessoa não pode ler o histórico do dono.
    rejected_resume = client.get(
        resume_path,
        headers=intruder_headers,
    )
    assert rejected_resume.status_code == expected_status

    # O histórico continua disponível para o dono.
    owner_resume = client.get(
        resume_path,
        headers=owner_headers,
    )
    assert owner_resume.status_code == 200

    expected_attempt = {
        "answer": (
            "Pulou"
            if action == "skip"
            else "Música que não existe"
        ),
        "status": (
            "skipped"
            if action == "skip"
            else "wrong"
        ),
    }
    assert owner_resume.json()["attempts"] == [
        expected_attempt,
    ]
    assert (
        owner_resume.json()["remainingLives"]
        == started["remainingLives"] - 1
    )

    assert owner_response.status_code == 200
    assert (
        owner_response.json()["remainingLives"]
        == started["remainingLives"] - 1
    )

@pytest.mark.parametrize(
    ("authenticated_intruder", "expected_status"),
    [
        (False, 401),
        (True, 404),
    ],
)
def test_infinite_round_access_requires_owner(
    client: TestClient,
    db_session: Session,
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

    start_response = client.post(
        "/infinite/start",
        headers=owner_headers,
    )
    assert start_response.status_code == 201
    game = start_response.json()

    round_payload = {
        "runId": game["runId"],
        "roundId": game["roundId"],
    }
    audio_path = (
        f"/infinite/{game['runId']}"
        f"/rounds/{game['roundId']}/audio"
    )

    # O áudio fica disponível somente para o dono.
    rejected_audio = client.get(
        audio_path,
        headers=intruder_headers,
    )
    assert rejected_audio.status_code == expected_status

    owner_audio = client.get(
        audio_path,
        headers=owner_headers,
    )
    assert owner_audio.status_code == 200
    assert owner_audio.headers["content-type"] == "audio/mpeg"
    assert len(owner_audio.content) > 0

    game_round = db_session.get(
        InfiniteRoundModel,
        UUID(game["roundId"]),
    )
    assert game_round is not None

    guess_payload = {
        **round_payload,
        "answer": game_round.song.title,
    }

    # Mesmo sabendo a resposta, outra pessoa não pode jogar.
    rejected_guess = client.post(
        "/infinite/guess",
        json=guess_payload,
        headers=intruder_headers,
    )
    assert rejected_guess.status_code == expected_status

    unchanged_game = client.get(
        f"/infinite/{game['runId']}",
        headers=owner_headers,
    )
    assert unchanged_game.status_code == 200
    assert unchanged_game.json()["attempts"] == []
    assert (
        unchanged_game.json()["remainingLives"]
        == game["remainingLives"]
    )

    owner_guess = client.post(
        "/infinite/guess",
        json=guess_payload,
        headers=owner_headers,
    )
    assert owner_guess.status_code == 200
    assert owner_guess.json()["correct"] is True
    assert owner_guess.json()["gameFinished"] is True

    # Com a rodada finalizada, só o dono pode avançar.
    rejected_next = client.post(
        "/infinite/next",
        json=round_payload,
        headers=intruder_headers,
    )
    assert rejected_next.status_code == expected_status

    owner_next = client.post(
        "/infinite/next",
        json=round_payload,
        headers=owner_headers,
    )
    assert owner_next.status_code == 201

    next_game = owner_next.json()
    assert next_game["runId"] == game["runId"]
    assert next_game["roundId"] != game["roundId"]
    assert next_game["roundNumber"] == 2

@pytest.mark.parametrize("game_mode", ["daily", "infinite"])
def test_guest_game_requires_its_own_token(
    client: TestClient,
    game_mode: str,
) -> None:
    prefix = (
        "/challenges/daily"
        if game_mode == "daily"
        else "/infinite"
    )

    first_start = client.post(f"{prefix}/start")
    second_start = client.post(f"{prefix}/start")

    assert first_start.status_code == 201
    assert second_start.status_code == 201

    first_game = first_start.json()
    second_game = second_start.json()

    assert isinstance(first_game["guestToken"], str)
    assert len(first_game["guestToken"]) == 43
    assert first_game["guestToken"] != second_game["guestToken"]

    owner_headers = {
        "X-Guest-Token": first_game["guestToken"],
    }
    other_headers = {
        "X-Guest-Token": second_game["guestToken"],
    }

    if game_mode == "daily":
        resume_path = (
            f"{prefix}/session/{first_game['sessionId']}"
        )
        payload = {
            "sessionId": first_game["sessionId"],
            "challengeId": first_game["challengeId"],
        }
    else:
        resume_path = f"{prefix}/{first_game['runId']}"
        payload = {
            "runId": first_game["runId"],
            "roundId": first_game["roundId"],
        }

    for rejected_headers in ({}, other_headers):
        rejected_resume = client.get(
            resume_path,
            headers=rejected_headers,
        )
        assert rejected_resume.status_code == 404

        for action in ("skip", "guess"):
            request_payload = dict(payload)

            if action == "guess":
                request_payload["answer"] = "Resposta incorreta"

            rejected_attempt = client.post(
                f"{prefix}/{action}",
                json=request_payload,
                headers=rejected_headers,
            )
            assert rejected_attempt.status_code == 404

    owner_resume = client.get(
        resume_path,
        headers=owner_headers,
    )
    assert owner_resume.status_code == 200
    assert owner_resume.json()["attempts"] == []
    assert (
        owner_resume.json()["remainingLives"]
        == first_game["remainingLives"]
    )

    owner_skip = client.post(
        f"{prefix}/skip",
        json=payload,
        headers=owner_headers,
    )
    assert owner_skip.status_code == 200
    assert (
        owner_skip.json()["remainingLives"]
        == first_game["remainingLives"] - 1
    )