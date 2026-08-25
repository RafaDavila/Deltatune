from fastapi.testclient import TestClient
from uuid import uuid4
from app.services.daily_challenge import (
    get_daily_challenge,
    DAILY_ROTATION,
)

from sqlalchemy.orm import Session

def test_correct_daily_guess(
    client: TestClient,
    db_session: Session,
) -> None:
    session_id, challenge_id = start_session(
        client,
    )

    daily_challenge = get_daily_challenge(db_session,)

    guess_response = client.post(
        "/challenges/daily/guess",
        json={
            "sessionId": session_id,
            "challengeId": challenge_id,
            "answer": daily_challenge.song.title,
        },
    )

    assert guess_response.status_code == 200

    guess_data = guess_response.json()

    assert guess_data["correct"] is True
    assert guess_data["won"] is True
    assert guess_data["gameFinished"] is True
    assert guess_data["attemptsUsed"] == 1
    assert guess_data["remainingLives"] == 6
    assert (
        guess_data["songTitle"]
        == daily_challenge.song.title
    )

    resume_response = client.get(
        f"/challenges/daily/session/{session_id}",
    )

    resume_data = resume_response.json()

    assert resume_data["won"] is True
    assert resume_data["gameFinished"] is True
    assert resume_data["attempts"] == [
        {
            "answer": daily_challenge.song.title,
            "status": "correct",
        }
    ]

    second_guess_response = client.post(
        "/challenges/daily/guess",
        json={
            "sessionId": session_id,
            "challengeId": challenge_id,
            "answer": daily_challenge.song.title,
        },
    )

    assert second_guess_response.status_code == 409
    assert second_guess_response.json()["detail"] == (
        "Esta partida já foi finalizada."
    )

def test_finish_game_after_six_skips(
        client: TestClient,
) -> None:
    session_id, challenge_id = start_session(
        client,
    )

    final_response = None

    for attempt_index in range(6):
        final_response = client.post(
            "/challenges/daily/skip",
            json={
                "sessionId": session_id,
                "challengeId": challenge_id,
            },
        )

        assert final_response.status_code == 200
        assert (
            final_response.json()["remainingLives"] == 5 - attempt_index
        )

    assert final_response is not None

    final_data = final_response.json()

    assert final_data["attemptsUsed"] == 6
    assert final_data["remainingLives"] == 0
    assert final_data["won"] is False
    assert final_data ["gameFinished"] is True
    assert final_data ["songTitle"] is not None

    seventh_skip_response = client.post(
        "/challenges/daily/skip",
        json={
            "sessionId": session_id,
            "challengeId": challenge_id,
        },
    )

    assert seventh_skip_response.status_code == 409
    assert seventh_skip_response.json()["detail"] == ("Esta partida já foi finalizada.")

def test_resume_nonexistent_session(
        client: TestClient,
) -> None:
    nonexistente_session_id = str(uuid4())

    response = client.get(
        "/challenges/daily/session/"
        f"{nonexistente_session_id}",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == ("Sessão de partida não encontrada.")

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

def test_accept_normalized_correct_answer(
    client: TestClient,
    db_session: Session,
) -> None:
    session_id, challenge_id = start_session(
        client,
    )

    daily_challenge = get_daily_challenge(db_session)

    answer_with_extra_spaces = "   ".join(
        daily_challenge.song.title
        .swapcase()
        .split()
    )

    response = client.post(
        "/challenges/daily/guess",
        json={
            "sessionId": session_id,
            "challengeId": challenge_id,
            "answer": f"  {answer_with_extra_spaces}  ",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["correct"] is True
    assert response_data["won"] is True
    assert response_data["gameFinished"] is True
    assert response_data["remainingLives"] == 6


def test_reject_outdated_challenge(
    client: TestClient,
) -> None:
    session_id, _ = start_session(client)

    response = client.post(
        "/challenges/daily/guess",
        json={
            "sessionId": session_id,
            "challengeId": "outdated-challenge",
            "answer": "Qualquer resposta",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Este desafio não é mais o desafio atual."
    )

    resume_response = client.get(
        f"/challenges/daily/session/{session_id}",
    )

    resume_data = resume_response.json()

    assert resume_data["attempts"] == []
    assert resume_data["remainingLives"] == 6


def test_resume_invalid_session_id(
    client: TestClient,
) -> None:
    response = client.get(
        "/challenges/daily/session/"
        "not-a-valid-uuid",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Sessão de partida não encontrada."
    )

def test_get_daily_audio(
    client: TestClient,
) -> None:
    response = client.get(
        "/challenges/daily/audio",
    )

    assert response.status_code == 200
    assert (
        response.headers["content-type"]
        == "audio/mpeg"
    )
    assert len(response.content) > 0

def test_daily_rotation_contains_every_song_once() -> None:
    assert len(DAILY_ROTATION) == 58
    assert len(set(DAILY_ROTATION)) == 58
    assert set(DAILY_ROTATION) == set(
        range(1,59),
    )

def test_reject_repeated_wrong_guess(
    client: TestClient,
) -> None:
    session_id, challenge_id = start_session(
        client,
    )

    request_body = {
        "sessionId": session_id,
        "challengeId": challenge_id,
        "answer": "Resposta certamente incorreta",
    }

    first_response = client.post(
        "/challenges/daily/guess",
        json=request_body,
    )

    repeated_response = client.post(
        "/challenges/daily/guess",
        json={
            **request_body,
            "answer": (
                "  resposta   certamente "
                "incorreta  "
            ),
        },
    )

    assert first_response.status_code == 200
    assert repeated_response.status_code == 409
    assert repeated_response.json()["detail"] == (
        "Você já tentou essa música."
    )

    resume_response = client.get(
        f"/challenges/daily/session/{session_id}",
    )

    resumed_game = resume_response.json()

    assert len(resumed_game["attempts"]) == 1
    assert resumed_game["remainingLives"] == 5