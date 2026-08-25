from fastapi.testclient import TestClient


def test_start_infinite_game(
    client: TestClient,
) -> None:
    response = client.post(
        "/infinite/start",
    )

    assert response.status_code == 201

    game = response.json()

    assert game["roundNumber"] == 1

    assert game["attemptDurations"] == [
        0.5,
        1,
        2,
        4,
        8,
        16,
    ]

    assert game["remainingLives"] == 6
    assert game["maximumAttempts"] == 6
    assert game["currentStreak"] == 0

    assert game["runId"]
    assert game["roundId"]

    assert "songId" not in game
    assert "songTitle" not in game
    assert "audioKey" not in game

def test_read_infinite_round_audio(
    client: TestClient,
) -> None:
    start_response = client.post(
        "/infinite/start",
    )

    assert start_response.status_code == 201

    game = start_response.json()

    response = client.get(
        f"/infinite/{game['runId']}"
        f"/rounds/{game['roundId']}/audio",
    )

    assert response.status_code == 200

    assert (
        response.headers["content-type"]
        == "audio/mpeg"
    )

    assert len(response.content) > 0

def test_reject_round_from_another_run(
    client: TestClient,
) -> None:
    first_game = client.post(
        "/infinite/start",
    ).json()

    second_game = client.post(
        "/infinite/start",
    ).json()

    response = client.get(
        f"/infinite/{first_game['runId']}"
        f"/rounds/{second_game['roundId']}"
        "/audio",
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "A rodada não pertence a esta sessão."
    )