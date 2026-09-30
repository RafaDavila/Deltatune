from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from fastapi.testclient import TestClient

from app.main import app


def post_concurrently(
    path: str,
    *,
    payload: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
) -> list[int]:
    barrier = Barrier(2)

    def send_request() -> int:
        worker_client = TestClient(
            app,
            client=("127.0.0.1", 50000),
        )

        try:
            barrier.wait(timeout=10)

            response = worker_client.post(
                path,
                json=payload,
                headers=headers,
            )

            return response.status_code
        finally:
            worker_client.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(send_request)
            for _ in range(2)
        ]

        return [
            future.result(timeout=20)
            for future in futures
        ]


def start_guest_game(
    client: TestClient,
    mode: str,
) -> tuple[
    str,
    str,
    str,
    dict[str, str],
    dict[str, str],
]:
    start_path = (
        "/challenges/daily/start"
        if mode == "daily"
        else "/infinite/start"
    )

    response = client.post(start_path)
    assert response.status_code == 201

    game = response.json()
    headers = {"X-Guest-Token": game["guestToken"]}

    if mode == "daily":
        return (
            "/challenges/daily/skip",
            "/challenges/daily/guess",
            f"/challenges/daily/session/{game['sessionId']}",
            {
                "sessionId": game["sessionId"],
                "challengeId": game["challengeId"],
            },
            headers,
        )

    return (
        "/infinite/skip",
        "/infinite/guess",
        f"/infinite/{game['runId']}",
        {
            "runId": game["runId"],
            "roundId": game["roundId"],
        },
        headers,
    )


@pytest.mark.parametrize("mode", ["daily", "infinite"])
def test_concurrent_skips_preserve_both_attempts(
    client: TestClient,
    mode: str,
) -> None:
    skip_path, _, resume_path, payload, headers = (
        start_guest_game(client, mode)
    )

    statuses = post_concurrently(
        skip_path,
        payload=payload,
        headers=headers,
    )

    assert statuses == [200, 200]

    response = client.get(resume_path, headers=headers)
    assert response.status_code == 200

    state = response.json()
    assert len(state["attempts"]) == 2
    assert all(
        attempt["status"] == "skipped"
        for attempt in state["attempts"]
    )
    assert state["remainingLives"] == 4
    assert state["gameFinished"] is False


@pytest.mark.parametrize("mode", ["daily", "infinite"])
def test_concurrent_skips_cannot_exceed_last_life(
    client: TestClient,
    mode: str,
) -> None:
    skip_path, _, resume_path, payload, headers = (
        start_guest_game(client, mode)
    )

    for _ in range(5):
        response = client.post(
            skip_path,
            json=payload,
            headers=headers,
        )
        assert response.status_code == 200

    statuses = post_concurrently(
        skip_path,
        payload=payload,
        headers=headers,
    )

    assert sorted(statuses) == [200, 409]

    response = client.get(resume_path, headers=headers)
    assert response.status_code == 200

    state = response.json()
    assert len(state["attempts"]) == 6
    assert state["remainingLives"] == 0
    assert state["gameFinished"] is True
    assert state["won"] is False


@pytest.mark.parametrize("mode", ["daily", "infinite"])
def test_concurrent_duplicate_guess_consumes_one_attempt(
    client: TestClient,
    mode: str,
) -> None:
    _, guess_path, resume_path, payload, headers = (
        start_guest_game(client, mode)
    )

    statuses = post_concurrently(
        guess_path,
        payload={
            **payload,
            "answer": "Palpite concorrente inexistente",
        },
        headers=headers,
    )

    assert sorted(statuses) == [200, 409]

    response = client.get(resume_path, headers=headers)
    assert response.status_code == 200

    state = response.json()
    assert len(state["attempts"]) == 1
    assert state["attempts"][0]["status"] == "wrong"
    assert state["remainingLives"] == 5


def test_concurrent_daily_start_reuses_one_session(
    client: TestClient,
) -> None:
    registration = client.post(
        "/auth/register",
        json={
            "displayName": "Rafael",
            "email": "game-concurrency@example.com",
            "password": "SenhaSegura123!",
        },
    )
    assert registration.status_code == 201

    login = client.post(
        "/auth/login",
        json={
            "email": "game-concurrency@example.com",
            "password": "SenhaSegura123!",
        },
    )
    assert login.status_code == 200

    headers = {
        "Authorization": (
            f"Bearer {login.json()['accessToken']}"
        ),
    }
    barrier = Barrier(2)

    def start_session() -> str:
        worker_client = TestClient(
            app,
            client=("127.0.0.1", 50000),
        )

        try:
            barrier.wait(timeout=10)

            response = worker_client.post(
                "/challenges/daily/start",
                headers=headers,
            )

            assert response.status_code == 201
            return response.json()["sessionId"]
        finally:
            worker_client.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(start_session)
            for _ in range(2)
        ]

        session_ids = [
            future.result(timeout=20)
            for future in futures
        ]

    assert session_ids[0] == session_ids[1]


def test_concurrent_next_creates_only_one_round(
    client: TestClient,
) -> None:
    skip_path, _, resume_path, payload, headers = (
        start_guest_game(client, "infinite")
    )

    for _ in range(6):
        response = client.post(
            skip_path,
            json=payload,
            headers=headers,
        )
        assert response.status_code == 200

    statuses = post_concurrently(
        "/infinite/next",
        payload=payload,
        headers=headers,
    )

    assert sorted(statuses) == [201, 409]

    response = client.get(resume_path, headers=headers)
    assert response.status_code == 200

    state = response.json()
    assert state["roundNumber"] == 2
    assert state["roundId"] != payload["roundId"]
    assert state["attempts"] == []
    assert state["remainingLives"] == 6