from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Barrier
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.models.password_reset_token import PasswordResetTokenModel
from app.models.user import UserModel
from app.repositories.password_reset_tokens import (
    create_password_reset_token,
    reset_password_with_token,
)
from app.services.password_reset_tokens import hash_password_reset_token


def register_reset_user(client: TestClient) -> UUID:
    response = client.post(
        "/auth/register",
        json={
            "displayName": "Rafael",
            "email": "concurrency@example.com",
            "password": "SenhaAntiga123!",
        },
    )

    assert response.status_code == 201
    return UUID(response.json()["id"])


def test_concurrent_emission_keeps_one_active_token(
    client: TestClient,
    db_session: Session,
) -> None:
    user_id = register_reset_user(client)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    session_factory = sessionmaker(bind=db_session.get_bind())
    barrier = Barrier(2)

    token_hashes = [
        hash_password_reset_token("a" * 43),
        hash_password_reset_token("b" * 43),
    ]

    def issue_token(token_hash: str) -> None:
        with session_factory() as session:
            session.execute(
                select(1)
            )
            barrier.wait(timeout=10)

            create_password_reset_token(
                session,
                user_id=user_id,
                token_hash=token_hash,
                expires_at=expires_at,
            )

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(issue_token, token_hash)
            for token_hash in token_hashes
        ]

        for future in futures:
            future.result(timeout=20)

    tokens = list(
        db_session.scalars(
            select(PasswordResetTokenModel)
            .where(PasswordResetTokenModel.user_id == user_id)
        )
    )

    assert len(tokens) == 2
    assert sum(token.used_at is None for token in tokens) == 1


@pytest.mark.parametrize(
    "distinct_tokens",
    [False, True],
)
def test_concurrent_reset_succeeds_only_once(
    client: TestClient,
    db_session: Session,
    distinct_tokens: bool,
) -> None:
    user_id = register_reset_user(client)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    first_hash = hash_password_reset_token("a" * 43)
    second_hash = hash_password_reset_token("b" * 43)

    # Insere diretamente para representar também contas
    # que já tinham dois tokens ativos antes da correção.
    db_session.add(
        PasswordResetTokenModel(
            user_id=user_id,
            token_hash=first_hash,
            expires_at=expires_at,
        )
    )

    if distinct_tokens:
        db_session.add(
            PasswordResetTokenModel(
                user_id=user_id,
                token_hash=second_hash,
                expires_at=expires_at,
            )
        )

    db_session.commit()

    user = db_session.get(UserModel, user_id)
    assert user is not None
    previous_version = user.token_version

    # Libera a transação de leitura antes das threads.
    db_session.rollback()

    session_factory = sessionmaker(bind=db_session.get_bind())
    barrier = Barrier(2)

    requested_hashes = [
        first_hash,
        second_hash if distinct_tokens else first_hash,
    ]

    def consume_token(
        token_hash: str,
        password_hash: str,
    ) -> bool:
        with session_factory() as session:
            session.execute(
                select(1)
            )
            barrier.wait(timeout=10)

            return reset_password_with_token(
                session,
                token_hash=token_hash,
                new_password_hash=password_hash,
            )

    # O repository recebe hashes prontos. Estes valores
    # identificam qual operação venceu, sem executar Argon2.
    password_hashes = ["hash-operation-a", "hash-operation-b"]

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(
                consume_token,
                token_hash,
                password_hash,
            )
            for token_hash, password_hash in zip(
                requested_hashes,
                password_hashes,
                strict=True,
            )
        ]

        results = [
            future.result(timeout=20)
            for future in futures
        ]

    assert sorted(results) == [False, True]

    db_session.expire_all()

    updated_user = db_session.get(UserModel, user_id)
    assert updated_user is not None
    assert updated_user.token_version == previous_version + 1

    winning_index = results.index(True)
    assert updated_user.password_hash == password_hashes[winning_index]

    pending_tokens = list(
        db_session.scalars(
            select(PasswordResetTokenModel)
            .where(
                PasswordResetTokenModel.user_id == user_id,
                PasswordResetTokenModel.used_at.is_(None),
            )
        )
    )

    assert pending_tokens == []