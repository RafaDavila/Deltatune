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

from pytest import MonkeyPatch

from app.repositories.password_reset_tokens import (
    get_active_password_reset_token,
)
from app.services.password_reset_tokens import (
    hash_password_reset_token,
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

def test_request_password_reset(
    client: TestClient,
    db_session: Session,
    monkeypatch: MonkeyPatch,
) -> None:
    client.post(
        "/auth/register",
        json={
            "displayName": "Rafael",
            "email": "rafael@example.com",
            "password": "Deltarune123!",
        },
    )

    captured_email: dict[str, str] = {}

    def fake_send_password_reset_email(
        recipient_email: str,
        reset_token: str,
    ) -> None:
        captured_email["recipient"] = (
            recipient_email
        )
        captured_email["token"] = reset_token

    monkeypatch.setattr(
        "app.routers.auth."
        "send_password_reset_email",
        fake_send_password_reset_email,
    )

    response = client.post(
        "/auth/forgot-password",
        json={
            "email": "rafael@example.com",
        },
    )

    assert response.status_code == 202
    assert (
        "Se existir uma conta"
        in response.json()["message"]
    )

    assert (
        captured_email["recipient"]
        == "rafael@example.com"
    )

    raw_token = captured_email["token"]
    token_hash = hash_password_reset_token(
        raw_token,
    )

    saved_token = (
        get_active_password_reset_token(
            db_session,
            token_hash,
        )
    )

    assert saved_token is not None
    assert saved_token.token_hash != raw_token


def test_hide_unknown_password_reset_email(
    client: TestClient,
    monkeypatch: MonkeyPatch,
) -> None:
    sent_tokens: list[str] = []

    def fake_send_password_reset_email(
        recipient_email: str,
        reset_token: str,
    ) -> None:
        sent_tokens.append(reset_token)

    monkeypatch.setattr(
        "app.routers.auth."
        "send_password_reset_email",
        fake_send_password_reset_email,
    )

    response = client.post(
        "/auth/forgot-password",
        json={
            "email": "desconhecido@example.com",
        },
    )

    assert response.status_code == 202
    assert (
        "Se existir uma conta"
        in response.json()["message"]
    )
    assert sent_tokens == []

def test_reset_password_flow(
    client: TestClient,
    monkeypatch: MonkeyPatch,
) -> None:
    client.post(
        "/auth/register",
        json={
            "displayName": "Rafael",
            "email": "rafael@example.com",
            "password": "SenhaAntiga123!",
        },
    )

    captured_token: dict[str, str] = {}

    def fake_send_password_reset_email(
        recipient_email: str,
        reset_token: str,
    ) -> None:
        captured_token["value"] = reset_token

    monkeypatch.setattr(
        "app.routers.auth."
        "send_password_reset_email",
        fake_send_password_reset_email,
    )

    request_response = client.post(
        "/auth/forgot-password",
        json={
            "email": "rafael@example.com",
        },
    )

    assert request_response.status_code == 202

    reset_token = captured_token["value"]

    reset_response = client.post(
        "/auth/reset-password",
        json={
            "token": reset_token,
            "newPassword": "SenhaNova123!",
        },
    )

    assert reset_response.status_code == 200
    assert reset_response.json() == {
        "message": "Senha redefinida com sucesso.",
    }

    old_login = client.post(
        "/auth/login",
        json={
            "email": "rafael@example.com",
            "password": "SenhaAntiga123!",
        },
    )

    new_login = client.post(
        "/auth/login",
        json={
            "email": "rafael@example.com",
            "password": "SenhaNova123!",
        },
    )

    assert old_login.status_code == 401
    assert new_login.status_code == 200

    reused_response = client.post(
        "/auth/reset-password",
        json={
            "token": reset_token,
            "newPassword": "OutraSenha123!",
        },
    )

    assert reused_response.status_code == 400
    assert reused_response.json()["detail"] == (
        "O link de recuperação é inválido "
        "ou expirou."
    )


def test_reject_unknown_password_reset_token(
    client: TestClient,
) -> None:
    response = client.post(
        "/auth/reset-password",
        json={
            "token": "x" * 43,
            "newPassword": "SenhaNova123!",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "O link de recuperação é inválido "
        "ou expirou."
    )