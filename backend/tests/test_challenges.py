from fastapi.testclient import TestClient


def start_session(
    client: TestClient,
) -> tuple[str, str]:
    response = client.post("/challenges/daily/start")

    assert response.status_code == 201

    response_data = response.json()
    return (
        response_data["sessionId"],
        response_data["challengeId"],
    )


def test_skip_daily_challenge(
    client: TestClient,
) -> None:
    session_id, challenge_id = start_session(
        client,
    )

    skip_response = client.post(
        "/challenges/daily/skip",
        json={
            "sessionId": session_id,
            "challengeId": challenge_id,
        },
    )

    assert skip_response.status_code == 200

    skip_data = skip_response.json()

    assert skip_data["skipped"] is True
    assert skip_data["attemptsUsed"] == 1
    assert skip_data["remainingLives"] == 5
    assert skip_data["gameFinished"] is False

    resume_response = client.get(
        f"/challenges/daily/session/{session_id}",
    )

    resume_data = resume_response.json()

    assert resume_data["attempts"] == [
        {
            "answer": "Pulou",
            "status": "skipped",
        }
    ]
    assert resume_data["remainingLives"] == 5


def test_wrong_daily_guess(
    client: TestClient,
) -> None:
    session_id, challenge_id = start_session(
        client,
    )

    guess_response = client.post(
        "/challenges/daily/guess",
        json={
            "sessionId": session_id,
            "challengeId": challenge_id,
            "answer": "Música que não existe",
        },
    )

    assert guess_response.status_code == 200

    guess_data = guess_response.json()

    assert guess_data["correct"] is False
    assert guess_data["won"] is False
    assert guess_data["attemptsUsed"] == 1
    assert guess_data["remainingLives"] == 5
    assert guess_data["songTitle"] is None

    resume_response = client.get(
        f"/challenges/daily/session/{session_id}",
    )

    resume_data = resume_response.json()

    assert resume_data["attempts"] == [
        {
            "answer": "Música que não existe",
            "status": "wrong",
        }
    ]


def test_start_daily_challenge(
    client: TestClient,
) -> None:
    response = client.post(
        "/challenges/daily/start",
    )

    assert response.status_code == 201

    response_data = response.json()

    assert response_data["sessionId"]
    assert response_data["remainingLives"] == 6
    assert response_data["maximumAttempts"] == 6


def test_resume_new_daily_challenge(
    client: TestClient,
) -> None:
    start_response = client.post(
        "/challenges/daily/start",
    )

    session_id = start_response.json()["sessionId"]

    resume_response = client.get(
        f"/challenges/daily/session/{session_id}",
    )

    assert resume_response.status_code == 200

    response_data = resume_response.json()

    assert response_data["sessionId"] == session_id
    assert response_data["attempts"] == []
    assert response_data["remainingLives"] == 6
    assert response_data["won"] is False
    assert response_data["gameFinished"] is False
    assert response_data["songTitle"] is None
