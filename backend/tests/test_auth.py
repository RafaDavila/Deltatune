from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.repositories.users import (
    get_user_by_email,
)
from app.services.passwords import (
    verify_password,
)

import jwt
import pytest
from app.config import settings
from app.services.tokens import JWT_ALGORITHM

from uuid import UUID

from app.models.game_session import (
    GameSessionModel,
)
from app.models.infinite_game import (
    InfiniteRunModel,
)

def test_register_user(
    client: TestClient,
    db_session: Session,
) -> None:
    response = client.post(
        "/auth/register",
        json={
            "displayName": "Rafael Davila",
            "email": "Rafael@Example.com",
            "password": "Deltarune123!",
        },
    )

    assert response.status_code == 201

    result = response.json()

    assert result["displayName"] == (
        "Rafael Davila"
    )
    assert result["email"] == (
        "rafael@example.com"
    )
    assert result["isActive"] is True
    assert result["id"]
    assert result["createdAt"]

    assert "password" not in result
    assert "passwordHash" not in result
    assert "password_hash" not in result

    user = get_user_by_email(
        db_session,
        "rafael@example.com",
    )

    assert user is not None
    assert user.password_hash != (
        "Deltarune123!"
    )
    assert verify_password(
        "Deltarune123!",
        user.password_hash,
    )


def test_reject_duplicate_email(
    client: TestClient,
) -> None:
    first_response = client.post(
        "/auth/register",
        json={
            "displayName": "Rafael",
            "email": "rafael@example.com",
            "password": "Deltarune123!",
        },
    )

    repeated_response = client.post(
        "/auth/register",
        json={
            "displayName": "Outro usuário",
            "email": "RAFAEL@example.com",
            "password": "OutraSenha123!",
        },
    )

    assert first_response.status_code == 201
    assert repeated_response.status_code == 409

    assert repeated_response.json()["detail"] == (
        "Já existe uma conta com este e-mail."
    )


def test_reject_invalid_registration(
    client: TestClient,
) -> None:
    response = client.post(
        "/auth/register",
        json={
            "displayName": "R",
            "email": "email-invalido",
            "password": "123",
        },
    )

    assert response.status_code == 422

def test_login_user(
    client: TestClient,
) -> None:
    registration_response = client.post(
        "/auth/register",
        json={
            "displayName": "Rafael",
            "email": "rafael@example.com",
            "password": "Deltarune123!",
        },
    )

    assert registration_response.status_code == 201

    registered_user = (
        registration_response.json()
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "RAFAEL@example.com",
            "password": "Deltarune123!",
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["tokenType"] == "bearer"
    assert result["accessToken"].count(".") == 2

    payload = jwt.decode(
        result["accessToken"],
        settings.jwt_secret_key.get_secret_value(),
        algorithms=[JWT_ALGORITHM],
    )

    assert payload["sub"] == (
        registered_user["id"]
    )
    assert payload["type"] == "access"
    assert "iat" in payload
    assert "exp" in payload


@pytest.mark.parametrize(
    ("email", "password"),
    [
        (
            "rafael@example.com",
            "SenhaErrada",
        ),
        (
            "inexistente@example.com",
            "Deltarune123!",
        ),
    ],
)
def test_reject_invalid_login(
    client: TestClient,
    email: str,
    password: str,
) -> None:
    registration_response = client.post(
        "/auth/register",
        json={
            "displayName": "Rafael",
            "email": "rafael@example.com",
            "password": "Deltarune123!",
        },
    )

    assert registration_response.status_code == 201

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "E-mail ou senha inválidos."
    )

    assert response.headers[
        "www-authenticate"
    ] == "Bearer"

def test_read_current_user(
    client: TestClient,
) -> None:
    registration = client.post(
        "/auth/register",
        json={
            "displayName": "Rafael",
            "email": "rafael@example.com",
            "password": "Deltarune123!",
        },
    ).json()

    login = client.post(
        "/auth/login",
        json={
            "email": "rafael@example.com",
            "password": "Deltarune123!",
        },
    ).json()

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": (
                f"Bearer {login['accessToken']}"
            ),
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["id"] == registration["id"]
    assert result["displayName"] == "Rafael"
    assert result["email"] == (
        "rafael@example.com"
    )
    assert result["isActive"] is True


def test_reject_missing_access_token(
    client: TestClient,
) -> None:
    response = client.get(
        "/auth/me",
    )

    assert response.status_code == 401
    assert response.headers[
        "www-authenticate"
    ] == "Bearer"


def test_reject_invalid_access_token(
    client: TestClient,
) -> None:
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": (
                "Bearer token-invalido"
            ),
        },
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Não foi possível validar "
        "a autenticação."
    )

def test_link_daily_session_to_user(
    client: TestClient,
    db_session: Session,
) -> None:
    registration = client.post(
        "/auth/register",
        json={
            "displayName": "Rafael",
            "email": "rafael@example.com",
            "password": "Deltarune123!",
        },
    ).json()

    login = client.post(
        "/auth/login",
        json={
            "email": "rafael@example.com",
            "password": "Deltarune123!",
        },
    ).json()

    start_response = client.post(
        "/challenges/daily/start",
        headers={
            "Authorization": (
                f"Bearer {login['accessToken']}"
            ),
        },
    )

    assert start_response.status_code == 201

    game_session = db_session.get(
        GameSessionModel,
        UUID(
            start_response.json()["sessionId"],
        ),
    )

    assert game_session is not None
    assert game_session.user_id == UUID(
        registration["id"],
    )


def test_link_infinite_run_to_user(
    client: TestClient,
    db_session: Session,
) -> None:
    registration = client.post(
        "/auth/register",
        json={
            "displayName": "Rafael",
            "email": "rafael@example.com",
            "password": "Deltarune123!",
        },
    ).json()

    login = client.post(
        "/auth/login",
        json={
            "email": "rafael@example.com",
            "password": "Deltarune123!",
        },
    ).json()

    start_response = client.post(
        "/infinite/start",
        headers={
            "Authorization": (
                f"Bearer {login['accessToken']}"
            ),
        },
    )

    assert start_response.status_code == 201

    game_run = db_session.get(
        InfiniteRunModel,
        UUID(
            start_response.json()["runId"],
        ),
    )

    assert game_run is not None
    assert game_run.user_id == UUID(
        registration["id"],
    )


def test_keep_anonymous_games_unlinked(
    client: TestClient,
    db_session: Session,
) -> None:
    daily_response = client.post(
        "/challenges/daily/start",
    )

    infinite_response = client.post(
        "/infinite/start",
    )

    assert daily_response.status_code == 201
    assert infinite_response.status_code == 201

    game_session = db_session.get(
        GameSessionModel,
        UUID(
            daily_response.json()["sessionId"],
        ),
    )

    game_run = db_session.get(
        InfiniteRunModel,
        UUID(
            infinite_response.json()["runId"],
        ),
    )

    assert game_session is not None
    assert game_run is not None

    assert game_session.user_id is None
    assert game_run.user_id is None

def test_reuse_daily_session_for_authenticated_user(
    client: TestClient,
) -> None:
    client.post(
        "/auth/register",
        json={
            "displayName": "Rafael",
            "email": "rafael@example.com",
            "password": "Deltarune123!",
        },
    )

    login = client.post(
        "/auth/login",
        json={
            "email": "rafael@example.com",
            "password": "Deltarune123!",
        },
    ).json()

    headers = {
        "Authorization": (
            f"Bearer {login['accessToken']}"
        ),
    }

    first_start = client.post(
        "/challenges/daily/start",
        headers=headers,
    )

    second_start = client.post(
        "/challenges/daily/start",
        headers=headers,
    )

    assert first_start.status_code == 201
    assert second_start.status_code == 201

    assert (
        first_start.json()["sessionId"]
        == second_start.json()["sessionId"]
    )

def test_create_distinct_daily_sessions_for_anonymous_user(
    client: TestClient,
) -> None:
    first_start = client.post(
        "/challenges/daily/start",
    )

    second_start = client.post(
        "/challenges/daily/start",
    )

    assert first_start.status_code == 201
    assert second_start.status_code == 201

    assert (
        first_start.json()["sessionId"]
        != second_start.json()["sessionId"]
    )