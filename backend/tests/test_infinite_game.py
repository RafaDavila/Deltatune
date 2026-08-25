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