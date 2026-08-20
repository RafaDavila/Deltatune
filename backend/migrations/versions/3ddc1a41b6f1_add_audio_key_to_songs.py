"""add audio key to songs

Revision ID: 3ddc1a41b6f1
Revises: 46909fbd2a80
Create Date: 2026-08-20 19:52:27.691187

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ddc1a41b6f1'
down_revision: Union[str, Sequence[str], None] = '46909fbd2a80'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "songs",
        sa.Column(
            "audio_key",
            sa.String(length=50),
            nullable=True,
        ),
    )
    op.create_unique_constraint(
        "uq_songs_audio_key",
        "songs",
        ["audio_key"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "uq_songs_audio_key",
        "songs",
        type_="unique",
    )
    op.drop_column(
        "songs",
        "audio_key",
    )
