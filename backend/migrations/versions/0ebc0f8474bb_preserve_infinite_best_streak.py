"""preserve infinite best streak

Revision ID: 0ebc0f8474bb
Revises: f7d1347a1b33
Create Date: 2026-09-30 19:02:20.558038

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ebc0f8474bb'
down_revision: Union[str, Sequence[str], None] = 'f7d1347a1b33'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "infinite_runs",
        sa.Column(
            "best_streak",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )

    op.execute(
        sa.text(
            """
            WITH round_results AS (
                SELECT
                    r.run_id,
                    r.round_number,
                    EXISTS (
                        SELECT 1
                        FROM infinite_attempts AS a
                        WHERE a.round_id = r.id
                          AND a.status = 'correct'
                    ) AS won
                FROM infinite_rounds AS r
            ),
            grouped_rounds AS (
                SELECT
                    run_id,
                    won,
                    SUM(
                        CASE WHEN won THEN 0 ELSE 1 END
                    ) OVER (
                        PARTITION BY run_id
                        ORDER BY round_number
                        ROWS BETWEEN UNBOUNDED PRECEDING
                                 AND CURRENT ROW
                    ) AS streak_group
                FROM round_results
            ),
            winning_streaks AS (
                SELECT
                    run_id,
                    streak_group,
                    COUNT(*) AS streak_length
                FROM grouped_rounds
                WHERE won
                GROUP BY run_id, streak_group
            ),
            historical_records AS (
                SELECT
                    run_id,
                    MAX(streak_length) AS best_streak
                FROM winning_streaks
                GROUP BY run_id
            )
            UPDATE infinite_runs AS run
            SET best_streak = GREATEST(
                run.current_streak,
                COALESCE(
                    (
                        SELECT history.best_streak
                        FROM historical_records AS history
                        WHERE history.run_id = run.id
                    ),
                    0
                )
            )
            """
        )
    )


def downgrade() -> None:
    op.drop_column(
        "infinite_runs",
        "best_streak",
    )
