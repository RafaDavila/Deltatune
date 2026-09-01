from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.repositories.users import (
    get_user_by_email,
)
from app.services.passwords import (
    verify_password,
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