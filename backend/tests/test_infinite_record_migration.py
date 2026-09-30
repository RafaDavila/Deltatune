import importlib.util
from pathlib import Path
from uuid import uuid4

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session


def test_backfill_infinite_records(
    db_session: Session,
) -> None:
    migration_path = next(
        (
            Path(__file__).resolve().parents[1]
            / "migrations"
            / "versions"
        ).glob("0ebc0f8474bb_*.py")
    )

    spec = importlib.util.spec_from_file_location(
        "infinite_record_migration",
        migration_path,
    )
    assert spec is not None
    assert spec.loader is not None

    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    connection = db_session.connection()
    schema_name = f"record_migration_{uuid4().hex}"

    connection.execute(
        text(f'CREATE SCHEMA "{schema_name}"')
    )
    connection.execute(
        text(f'SET LOCAL search_path TO "{schema_name}"')
    )

    # Estrutura mínima anterior à migração.
    connection.execute(
        text(
            """
            CREATE TABLE infinite_runs (
                id UUID PRIMARY KEY,
                current_streak INTEGER NOT NULL DEFAULT 0
            )
            """
        )
    )
    connection.execute(
        text(
            """
            CREATE TABLE infinite_rounds (
                id UUID PRIMARY KEY,
                run_id UUID NOT NULL REFERENCES infinite_runs(id),
                round_number INTEGER NOT NULL
            )
            """
        )
    )
    connection.execute(
        text(
            """
            CREATE TABLE infinite_attempts (
                id INTEGER GENERATED ALWAYS AS IDENTITY
                    PRIMARY KEY,
                round_id UUID NOT NULL
                    REFERENCES infinite_rounds(id),
                status VARCHAR(10) NOT NULL
            )
            """
        )
    )

    # W = vitória; L = derrota; P = rodada em andamento.
    scenarios = [
        ("sem rodadas", "", 0, 0),
        ("somente derrotas", "LL", 0, 0),
        ("vitórias antes da derrota", "WWL", 0, 2),
        ("maior sequência histórica", "WWLWWWL", 0, 3),
        ("sequência em andamento", "WWP", 2, 2),
        ("sequência antiga maior", "WWWLWP", 1, 3),
        ("valor atual sem histórico", "", 9, 9),
    ]

    expected_records = {}

    for name, rounds, current_streak, expected in scenarios:
        run_id = uuid4()
        expected_records[run_id] = (name, expected)

        connection.execute(
            text(
                """
                INSERT INTO infinite_runs (id, current_streak)
                VALUES (:id, :current_streak)
                """
            ),
            {
                "id": run_id,
                "current_streak": current_streak,
            },
        )

        for round_number, result in enumerate(rounds, start=1):
            round_id = uuid4()

            connection.execute(
                text(
                    """
                    INSERT INTO infinite_rounds (
                        id, run_id, round_number
                    )
                    VALUES (:id, :run_id, :round_number)
                    """
                ),
                {
                    "id": round_id,
                    "run_id": run_id,
                    "round_number": round_number,
                },
            )

            statuses = (
                ["wrong", "correct"]
                if result == "W"
                else ["skipped"] * 6
                if result == "L"
                else ["wrong"]
            )

            connection.execute(
                text(
                    """
                    INSERT INTO infinite_attempts (
                        round_id, status
                    )
                    VALUES (:round_id, :status)
                    """
                ),
                [
                    {
                        "round_id": round_id,
                        "status": status,
                    }
                    for status in statuses
                ],
            )

    context = MigrationContext.configure(connection)

    with Operations.context(context):
        migration.upgrade()

    records = connection.execute(
        text("SELECT id, best_streak FROM infinite_runs")
    ).all()

    assert len(records) == len(scenarios)

    for run_id, best_streak in records:
        name, expected = expected_records[run_id]
        assert best_streak == expected, name

    # Novas partidas recebem zero pelo default do banco.
    new_run_id = uuid4()

    connection.execute(
        text("INSERT INTO infinite_runs (id) VALUES (:id)"),
        {"id": new_run_id},
    )

    assert connection.scalar(
        text(
            """
            SELECT best_streak
            FROM infinite_runs
            WHERE id = :id
            """
        ),
        {"id": new_run_id},
    ) == 0

    with Operations.context(context):
        migration.downgrade()

    columns = inspect(connection).get_columns(
        "infinite_runs",
        schema=schema_name,
    )
    assert "best_streak" not in {
        column["name"] for column in columns
    }

    assert connection.scalar(
        text("SELECT COUNT(*) FROM infinite_runs")
    ) == len(scenarios) + 1

    # Sem commit: a fixture fecha a sessão e desfaz o schema.