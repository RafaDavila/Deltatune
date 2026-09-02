from typing import Literal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.game_session import (
    AttemptModel,
    GameSessionModel,
)
from datetime import date

AttemptStatus = Literal[
    "skipped",
    "wrong",
    "correct",
]


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

def create_game_session(
    db: Session,
    challenge_id: str,
    user_id: UUID | None = None,
) -> GameSessionModel:
    game_session = GameSessionModel(
        challenge_id=challenge_id,
        user_id=user_id,
    )

    db.add(game_session)
    db.commit()
    db.refresh(game_session)

    return game_session


def get_game_session_by_user_and_challenge(
    db: Session,
    user_id: UUID,
    challenge_id: str,
) -> GameSessionModel | None:
    statement = (
        select(GameSessionModel)
        .options(
            selectinload(GameSessionModel.attempts),
        )
        .where(
            GameSessionModel.user_id == user_id,
            GameSessionModel.challenge_id == challenge_id,
        )
    )

    return db.scalar(statement)


def get_game_session(
    db: Session,
    session_id: str,
) -> GameSessionModel | None:
    try:
        parsed_session_id = UUID(session_id)
    except ValueError:
        return None

    statement = (
        select(GameSessionModel)
        .options(
            selectinload(GameSessionModel.attempts),
        )
        .where(
            GameSessionModel.id == parsed_session_id,
        )
    )

    return db.scalar(statement)


def list_game_sessions_by_user_and_period(
    db: Session,
    user_id: UUID,
    start_date: date,
    end_date: date,
) -> list[GameSessionModel]:
    statement = (
        select(GameSessionModel)
        .options(
            selectinload(GameSessionModel.attempts),
        )
        .where(
            GameSessionModel.user_id == user_id,
            GameSessionModel.challenge_id >= start_date.isoformat(),
            GameSessionModel.challenge_id <= end_date.isoformat(),
        )
        .order_by(GameSessionModel.challenge_id)
    )

    return list(
        db.scalars(statement).all(),
    )


def add_attempt(
    db: Session,
    game_session: GameSessionModel,
    answer: str,
    status: AttemptStatus,
) -> AttemptModel:
    attempt = AttemptModel(
        attempt_number=len(game_session.attempts) + 1,
        answer=answer,
        status=status,
    )

    game_session.attempts.append(attempt)

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return attempt

def test_show_started_daily_game_as_in_progress(
    client: TestClient,
) -> None:
    headers = create_authenticated_headers(
        client,
    )

    start_response = client.post(
        "/challenges/daily/start",
        headers=headers,
    )

    week_response = client.get(
        "/challenges/daily/week",
        headers=headers,
    )

    today_id = datetime.now(
        GAME_TIME_ZONE,
    ).date().isoformat()

    today = next(
        day
        for day in week_response.json()["days"]
        if day["challengeId"] == today_id
    )

    assert week_response.status_code == 200
    assert today["status"] == "in_progress"
    assert today["attemptsUsed"] == 0
    assert (
        today["sessionId"]
        == start_response.json()["sessionId"]
    )


def test_show_won_daily_game_in_week(
    client: TestClient,
    db_session: Session,
) -> None:
    headers = create_authenticated_headers(
        client,
    )

    start_response = client.post(
        "/challenges/daily/start",
        headers=headers,
    )

    start_data = start_response.json()

    daily_challenge = get_daily_challenge(
        db_session,
    )

    guess_response = client.post(
        "/challenges/daily/guess",
        headers=headers,
        json={
            "sessionId": start_data["sessionId"],
            "challengeId": (
                start_data["challengeId"]
            ),
            "answer": daily_challenge.song.title,
        },
    )

    assert guess_response.status_code == 200

    week_response = client.get(
        "/challenges/daily/week",
        headers=headers,
    )

    today_id = datetime.now(
        GAME_TIME_ZONE,
    ).date().isoformat()

    today = next(
        day
        for day in week_response.json()["days"]
        if day["challengeId"] == today_id
    )

    assert today["status"] == "won"
    assert today["attemptsUsed"] == 1


def test_show_lost_daily_game_in_week(
    client: TestClient,
) -> None:
    headers = create_authenticated_headers(
        client,
    )

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
                "challengeId": (
                    start_data["challengeId"]
                ),
            },
        )

        assert skip_response.status_code == 200

    week_response = client.get(
        "/challenges/daily/week",
        headers=headers,
    )

    today_id = datetime.now(
        GAME_TIME_ZONE,
    ).date().isoformat()

    today = next(
        day
        for day in week_response.json()["days"]
        if day["challengeId"] == today_id
    )

    assert today["status"] == "lost"
    assert today["attemptsUsed"] == 6