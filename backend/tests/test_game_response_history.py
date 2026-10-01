from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.infinite_game import InfiniteRoundModel
from app.services.daily_challenge import get_daily_challenge


@pytest.mark.parametrize("mode", ["daily", "infinite"])
def test_mutations_return_complete_ordered_history(
    client: TestClient,
    db_session: Session,
    mode: str,
) -> None:
    if mode == "daily":
        prefix = "/challenges/daily"
    else:
        prefix = "/infinite"

    start_response = client.post(f"{prefix}/start")
    assert start_response.status_code == 201

    game = start_response.json()
    headers = {
        "X-Guest-Token": game["guestToken"],
    }

    if mode == "daily":
        identifiers = {
            "sessionId": game["sessionId"],
            "challengeId": game["challengeId"],
        }
        song_title = get_daily_challenge(db_session).song.title
        resume_path = (
            f"/challenges/daily/session/{game['sessionId']}"
        )
    else:
        identifiers = {
            "runId": game["runId"],
            "roundId": game["roundId"],
        }
        game_round = db_session.get(
            InfiniteRoundModel,
            UUID(game["roundId"]),
        )
        assert game_round is not None
        song_title = game_round.song.title
        resume_path = f"/infinite/{game['runId']}"

    wrong_answer = "Resposta inexistente para este teste"

    wrong_response = client.post(
        f"{prefix}/guess",
        headers=headers,
        json={
            **identifiers,
            "answer": wrong_answer,
        },
    )
    assert wrong_response.status_code == 200

    expected_attempts = [
        {
            "answer": wrong_answer,
            "status": "wrong",
        },
    ]

    wrong_game = wrong_response.json()
    assert wrong_game["attempts"] == expected_attempts
    assert wrong_game["attemptsUsed"] == 1
    assert wrong_game["remainingLives"] == 5
    assert wrong_game["correct"] is False
    assert wrong_game["won"] is False
    assert wrong_game["gameFinished"] is False
    assert wrong_game["songTitle"] is None

    skip_response = client.post(
        f"{prefix}/skip",
        headers=headers,
        json=identifiers,
    )
    assert skip_response.status_code == 200

    expected_attempts.append(
        {
            "answer": "Pulou",
            "status": "skipped",
        },
    )

    skipped_game = skip_response.json()
    assert skipped_game["attempts"] == expected_attempts
    assert skipped_game["attemptsUsed"] == 2
    assert skipped_game["remainingLives"] == 4
    assert skipped_game["skipped"] is True
    assert skipped_game["won"] is False
    assert skipped_game["gameFinished"] is False
    assert skipped_game["songTitle"] is None

    correct_response = client.post(
        f"{prefix}/guess",
        headers=headers,
        json={
            **identifiers,
            "answer": song_title,
        },
    )
    assert correct_response.status_code == 200

    expected_attempts.append(
        {
            "answer": song_title,
            "status": "correct",
        },
    )

    won_game = correct_response.json()
    assert won_game["attempts"] == expected_attempts
    assert won_game["attemptsUsed"] == 3
    assert won_game["remainingLives"] == 4
    assert won_game["correct"] is True
    assert won_game["won"] is True
    assert won_game["gameFinished"] is True
    assert won_game["songTitle"] == song_title

    resumed_response = client.get(
        resume_path,
        headers=headers,
    )
    assert resumed_response.status_code == 200
    assert resumed_response.json()["attempts"] == expected_attempts