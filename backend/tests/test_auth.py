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