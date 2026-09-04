from datetime import date, datetime, timedelta

from fastapi.testclient import TestClient
from uuid import UUID, uuid4
from app.services.daily_challenge import (
    CHALLENGE_START_DATE,
    GAME_TIME_ZONE,
    calculate_daily_streaks,
    get_daily_challenge,
    DAILY_ROTATION,
    get_week_dates,
    calculate_daily_streaks,
)

from sqlalchemy.orm import Session

from app.models.game_session import (
    AttemptModel,
    GameSessionModel,
)


def create_authenticated_headers(
    client: TestClient,
) -> dict[str, str]:
    client.post(
        "/auth/register",
        json={
            "displayName": "Rafael",
            "email": "rafael@example.com",
            "password": "Deltarune123!",
        },
    )

    login = client.post(
        "/auth/login",
        json={
            "email": "rafael@example.com",
            "password": "Deltarune123!",
        },
    ).json()

    return {
        "Authorization": (
            f"Bearer {login['accessToken']}"
        ),
    }


def get_today_week_day(
    response_data: dict[str, object],
) -> dict[str, object]:
    today_id = datetime.now(
        GAME_TIME_ZONE,
    ).date().isoformat()

    return next(
        day
        for day in response_data["days"]
        if day["challengeId"] == today_id
    )


def test_show_started_daily_game_as_in_progress(
    client: TestClient,
) -> None:
    headers = create_authenticated_headers(client)

    start_response = client.post(
        "/challenges/daily/start",
        headers=headers,
    )
    week_response = client.get(
        "/challenges/daily/week",
        headers=headers,
    )
    today = get_today_week_day(week_response.json())

    assert week_response.status_code == 200
    assert today["status"] == "in_progress"
    assert today["attemptsUsed"] == 0
    assert today["sessionId"] == start_response.json()["sessionId"]


def test_show_won_daily_game_in_week(
    client: TestClient,
    db_session: Session,
) -> None:
    headers = create_authenticated_headers(client)
    start_response = client.post(
        "/challenges/daily/start",
        headers=headers,
    )
    start_data = start_response.json()
    daily_challenge = get_daily_challenge(db_session)

    guess_response = client.post(
        "/challenges/daily/guess",
        headers=headers,
        json={
            "sessionId": start_data["sessionId"],
            "challengeId": start_data["challengeId"],
            "answer": daily_challenge.song.title,
        },
    )

    week_response = client.get(
        "/challenges/daily/week",
        headers=headers,
    )
    today = get_today_week_day(week_response.json())

    assert guess_response.status_code == 200
    assert today["status"] == "won"
    assert today["attemptsUsed"] == 1


def test_show_lost_daily_game_in_week(
    client: TestClient,
) -> None:
    headers = create_authenticated_headers(client)
    start_response = client.post(
        "/challenges/daily/start",
        headers=headers,
    )
    start_data = start_response.json()

    for _ in range(6):
        skip_response = client.post(
            "/challenges/daily/skip",
            headers=headers,
            json={
                "sessionId": start_data["sessionId"],
                "challengeId": start_data["challengeId"],
            },
        )
        assert skip_response.status_code == 200

    week_response = client.get(
        "/challenges/daily/week",
        headers=headers,
    )
    today = get_today_week_day(week_response.json())

    assert today["status"] == "lost"
    assert today["attemptsUsed"] == 6


def test_get_week_dates_from_sunday_to_saturday(
) -> None:
    week_dates = get_week_dates(
        date(2026, 9, 2),
    )

    assert week_dates == (
        date(2026, 8, 30),
        date(2026, 8, 31),
        date(2026, 9, 1),
        date(2026, 9, 2),
        date(2026, 9, 3),
        date(2026, 9, 4),
        date(2026, 9, 5),
    )

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

def test_reject_unauthenticated_daily_week(
    client: TestClient,
) -> None:
    response = client.get(
        "/challenges/daily/week",
    )

    assert response.status_code == 401
    assert response.headers[
        "www-authenticate"
    ] == "Bearer"


def test_return_empty_daily_week_for_user(
    client: TestClient,
) -> None:
    client.post(
        "/auth/register",
        json={
            "displayName": "Rafael",
            "email": "rafael@example.com",
            "password": "Deltarune123!",
        },
    )

    login = client.post(
        "/auth/login",
        json={
            "email": "rafael@example.com",
            "password": "Deltarune123!",
        },
    ).json()

    response = client.get(
        "/challenges/daily/week",
        headers={
            "Authorization": (
                f"Bearer {login['accessToken']}"
            ),
        },
    )

    assert response.status_code == 200

    days = response.json()["days"]

    today = datetime.now(
        GAME_TIME_ZONE,
    ).date()

    week_dates = get_week_dates(today)

    assert len(days) == 7

    assert [
        day["challengeId"]
        for day in days
    ] == [
        challenge_date.isoformat()
        for challenge_date in week_dates
    ]

    for day, challenge_date in zip(
        days,
        week_dates,
        strict=True,
    ):
        if (
            challenge_date < CHALLENGE_START_DATE
            or challenge_date > today
        ):
            expected_status = "unavailable"
        else:
            expected_status = "not_played"

        assert day["status"] == expected_status
        assert day["attemptsUsed"] == 0
        assert day["sessionId"] is None

def create_daily_session_for_streak(
    challenge_id: str,
    statuses: list[str],
) -> GameSessionModel:
    game_session = GameSessionModel(
        challenge_id=challenge_id,
    )

    game_session.attempts = [
        AttemptModel(
            attempt_number=index,
            answer="Teste",
            status=attempt_status,
        )
        for index, attempt_status in enumerate(
            statuses,
            start=1,
        )
    ]

    return game_session

def test_preserve_daily_streak_before_playing_today() -> None:
    sessions = [
        create_daily_session_for_streak(
            "2026-08-24",
            ["correct"],
        ),
        create_daily_session_for_streak(
            "2026-08-25",
            ["correct"],
        ),
    ]

    result = calculate_daily_streaks(
        sessions,
        today=date(2026, 8, 26),
    )

    assert result == (2, 2)


def test_break_daily_streak_after_missed_day() -> None:
    sessions = [
        create_daily_session_for_streak(
            "2026-08-24",
            ["correct"],
        ),
        create_daily_session_for_streak(
            "2026-08-26",
            ["correct"],
        ),
    ]

    result = calculate_daily_streaks(
        sessions,
        today=date(2026, 8, 26),
    )

    assert result == (1, 1)


def test_reset_daily_streak_after_loss() -> None:
    sessions = [
        create_daily_session_for_streak(
            "2026-08-24",
            ["correct"],
        ),
        create_daily_session_for_streak(
            "2026-08-25",
            ["correct"],
        ),
        create_daily_session_for_streak(
            "2026-08-26",
            ["wrong"] * 6,
        ),
    ]

    result = calculate_daily_streaks(
        sessions,
        today=date(2026, 8, 26),
    )

    assert result == (0, 2)

def test_require_authentication_for_daily_stats(
    client: TestClient,
) -> None:
    response = client.get(
        "/challenges/daily/stats",
    )

    assert response.status_code == 401


def test_return_daily_streak_stats(
    client: TestClient,
    db_session: Session,
) -> None:
    registration = client.post(
        "/auth/register",
        json={
            "displayName": "Rafael",
            "email": "rafael@example.com",
            "password": "Deltarune123!",
        },
    ).json()

    login = client.post(
        "/auth/login",
        json={
            "email": "rafael@example.com",
            "password": "Deltarune123!",
        },
    ).json()

    user_id = UUID(registration["id"])

    today = datetime.now(
        GAME_TIME_ZONE,
    ).date()

    for challenge_date in (
        today - timedelta(days=1),
        today,
    ):
        game_session = GameSessionModel(
            user_id=user_id,
            challenge_id=(
                challenge_date.isoformat()
            ),
        )

        game_session.attempts.append(
            AttemptModel(
                attempt_number=1,
                answer="Resposta correta",
                status="correct",
            )
        )

        db_session.add(game_session)

    db_session.commit()

    response = client.get(
        "/challenges/daily/stats",
        headers={
            "Authorization": (
                f"Bearer {login['accessToken']}"
            ),
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "currentStreak": 2,
        "bestStreak": 2,
    }