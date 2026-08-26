from fastapi.testclient import TestClient
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.infinite_game import (
    InfiniteRoundModel,
)
from sqlalchemy import func, select
from app.models.song import SongModel

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

def test_wrong_infinite_guess(
    client: TestClient,
) -> None:
    game = client.post(
        "/infinite/start",
    ).json()

    response = client.post(
        "/infinite/guess",
        json={
            "runId": game["runId"],
            "roundId": game["roundId"],
            "answer": (
                "Resposta certamente incorreta"
            ),
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["correct"] is False
    assert result["won"] is False
    assert result["gameFinished"] is False
    assert result["attemptsUsed"] == 1
    assert result["remainingLives"] == 5
    assert result["currentStreak"] == 0
    assert result["songTitle"] is None

def test_reject_repeated_infinite_guess(
    client: TestClient,
    db_session: Session,
) -> None:
    game = client.post(
        "/infinite/start",
    ).json()

    request_body = {
        "runId": game["runId"],
        "roundId": game["roundId"],
        "answer": "Resposta repetida",
    }

    first_response = client.post(
        "/infinite/guess",
        json=request_body,
    )

    repeated_response = client.post(
        "/infinite/guess",
        json={
            **request_body,
            "answer": "  resposta   repetida  ",
        },
    )

    assert first_response.status_code == 200
    assert repeated_response.status_code == 409

    assert repeated_response.json()["detail"] == (
        "Você já tentou essa música."
    )

    db_session.expire_all()

    game_round = db_session.get(
        InfiniteRoundModel,
        UUID(game["roundId"]),
    )

    assert game_round is not None
    assert len(game_round.attempts) == 1
    assert game_round.remaining_lives == 5

def test_correct_infinite_guess(
    client: TestClient,
    db_session: Session,
) -> None:
    game = client.post(
        "/infinite/start",
    ).json()

    game_round = db_session.get(
        InfiniteRoundModel,
        UUID(game["roundId"]),
    )

    assert game_round is not None

    correct_answer = game_round.song.title

    response = client.post(
        "/infinite/guess",
        json={
            "runId": game["runId"],
            "roundId": game["roundId"],
            "answer": correct_answer,
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["correct"] is True
    assert result["won"] is True
    assert result["gameFinished"] is True
    assert result["attemptsUsed"] == 1
    assert result["remainingLives"] == 6
    assert result["currentStreak"] == 1
    assert result["songTitle"] == correct_answer

def test_finish_infinite_round_after_six_skips(
    client: TestClient,
) -> None:
    game = client.post(
        "/infinite/start",
    ).json()

    response = None

    for _ in range(6):
        response = client.post(
            "/infinite/skip",
            json={
                "runId": game["runId"],
                "roundId": game["roundId"],
            },
        )

        assert response.status_code == 200

    assert response is not None

    result = response.json()

    assert result["won"] is False
    assert result["gameFinished"] is True
    assert result["attemptsUsed"] == 6
    assert result["remainingLives"] == 0
    assert result["currentStreak"] == 0
    assert result["songTitle"] is not None

def test_reject_next_before_round_finishes(
    client: TestClient,
) -> None:
    game = client.post(
        "/infinite/start",
    ).json()

    response = client.post(
        "/infinite/next",
        json={
            "runId": game["runId"],
            "roundId": game["roundId"],
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "A rodada atual ainda não foi finalizada."
    )

def test_create_next_infinite_round(
    client: TestClient,
    db_session: Session,
) -> None:
    first_game = client.post(
        "/infinite/start",
    ).json()

    first_round = db_session.get(
        InfiniteRoundModel,
        UUID(first_game["roundId"]),
    )

    assert first_round is not None

    guess_response = client.post(
        "/infinite/guess",
        json={
            "runId": first_game["runId"],
            "roundId": first_game["roundId"],
            "answer": first_round.song.title,
        },
    )

    assert guess_response.status_code == 200

    response = client.post(
        "/infinite/next",
        json={
            "runId": first_game["runId"],
            "roundId": first_game["roundId"],
        },
    )

    assert response.status_code == 201

    next_game = response.json()

    assert next_game["runId"] == (
        first_game["runId"]
    )
    assert next_game["roundId"] != (
        first_game["roundId"]
    )
    assert next_game["roundNumber"] == 2
    assert next_game["remainingLives"] == 6
    assert next_game["maximumAttempts"] == 6
    assert next_game["currentStreak"] == 1

    assert "songId" not in next_game
    assert "songTitle" not in next_game
    assert "audioKey" not in next_game

    db_session.expire_all()

    next_round = db_session.get(
        InfiniteRoundModel,
        UUID(next_game["roundId"]),
    )

    assert next_round is not None
    assert next_round.cycle_number == 1
    assert next_round.song_id != (
        first_round.song_id
    )

def test_reject_next_from_old_round(
    client: TestClient,
    db_session: Session,
) -> None:
    game = client.post(
        "/infinite/start",
    ).json()

    game_round = db_session.get(
        InfiniteRoundModel,
        UUID(game["roundId"]),
    )

    assert game_round is not None

    client.post(
        "/infinite/guess",
        json={
            "runId": game["runId"],
            "roundId": game["roundId"],
            "answer": game_round.song.title,
        },
    )

    first_next_response = client.post(
        "/infinite/next",
        json={
            "runId": game["runId"],
            "roundId": game["roundId"],
        },
    )

    assert first_next_response.status_code == 201

    repeated_response = client.post(
        "/infinite/next",
        json={
            "runId": game["runId"],
            "roundId": game["roundId"],
        },
    )

    assert repeated_response.status_code == 409

    assert repeated_response.json()["detail"] == (
        "Esta não é a rodada atual da sessão."
    )

def test_infinite_cycle_uses_every_song_before_repeat(
    client: TestClient,
    db_session: Session,
) -> None:
    playable_song_count = db_session.scalar(
        select(func.count(SongModel.id))
        .where(
            SongModel.audio_key.is_not(None),
        )
    )

    assert playable_song_count is not None
    assert playable_song_count > 1

    game = client.post(
        "/infinite/start",
    ).json()

    used_song_ids: set[int] = set()

    for expected_round_number in range(
        1,
        playable_song_count + 1,
    ):
        db_session.expire_all()

        game_round = db_session.get(
            InfiniteRoundModel,
            UUID(game["roundId"]),
        )

        assert game_round is not None
        assert game_round.round_number == (
            expected_round_number
        )
        assert game_round.cycle_number == 1
        assert game_round.song_id not in (
            used_song_ids
        )

        used_song_ids.add(
            game_round.song_id,
        )

        guess_response = client.post(
            "/infinite/guess",
            json={
                "runId": game["runId"],
                "roundId": game["roundId"],
                "answer": game_round.song.title,
            },
        )

        assert guess_response.status_code == 200
        assert (
            guess_response.json()["correct"]
            is True
        )

        if (
            expected_round_number
            < playable_song_count
        ):
            next_response = client.post(
                "/infinite/next",
                json={
                    "runId": game["runId"],
                    "roundId": game["roundId"],
                },
            )

            assert next_response.status_code == 201

            game = next_response.json()

    assert len(used_song_ids) == (
        playable_song_count
    )

    second_cycle_response = client.post(
        "/infinite/next",
        json={
            "runId": game["runId"],
            "roundId": game["roundId"],
        },
    )

    assert second_cycle_response.status_code == 201

    second_cycle_game = (
        second_cycle_response.json()
    )

    assert second_cycle_game["roundNumber"] == (
        playable_song_count + 1
    )
    assert second_cycle_game["currentStreak"] == (
        playable_song_count
    )

    db_session.expire_all()

    second_cycle_round = db_session.get(
        InfiniteRoundModel,
        UUID(second_cycle_game["roundId"]),
    )

    assert second_cycle_round is not None
    assert second_cycle_round.cycle_number == 2
    assert second_cycle_round.song_id in (
        used_song_ids
    )