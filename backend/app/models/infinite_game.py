from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import (
    UUID as PostgreSQLUUID,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database import Base
from app.models.game_session import MAX_ATTEMPTS


class InfiniteRunModel(Base):
    __tablename__ = "infinite_runs"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    current_streak: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    rounds: Mapped[list["InfiniteRoundModel"]] = (
        relationship(
            back_populates="game_run",
            cascade="all, delete-orphan",
            order_by="InfiniteRoundModel.round_number",
        )
    )


class InfiniteRoundModel(Base):
    __tablename__ = "infinite_rounds"
    __table_args__ = (
        UniqueConstraint(
            "run_id",
            "round_number",
            name="uq_infinite_run_round_number",
        ),
        UniqueConstraint(
            "run_id",
            "cycle_number",
            "song_id",
            name="uq_infinite_cycle_song",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    run_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "infinite_runs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    song_id: Mapped[int] = mapped_column(
        ForeignKey(
            "songs.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    round_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    cycle_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    game_run: Mapped["InfiniteRunModel"] = (
        relationship(
            back_populates="rounds",
        )
    )

    attempts: Mapped[
        list["InfiniteAttemptModel"]
    ] = relationship(
        back_populates="round",
        cascade="all, delete-orphan",
        order_by=(
            "InfiniteAttemptModel.attempt_number"
        ),
    )

    @property
    def failed_attempts(self) -> int:
        return sum(
            attempt.status != "correct"
            for attempt in self.attempts
        )

    @property
    def remaining_lives(self) -> int:
        return max(
            MAX_ATTEMPTS - self.failed_attempts,
            0,
        )

    @property
    def won(self) -> bool:
        return any(
            attempt.status == "correct"
            for attempt in self.attempts
        )

    @property
    def finished(self) -> bool:
        return (
            self.won or
            self.remaining_lives == 0
        )


class InfiniteAttemptModel(Base):
    __tablename__ = "infinite_attempts"
    __table_args__ = (
        UniqueConstraint(
            "round_id",
            "attempt_number",
            name="uq_infinite_round_attempt_number",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    round_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "infinite_rounds.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    attempt_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    answer: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    round: Mapped["InfiniteRoundModel"] = (
        relationship(
            back_populates="attempts",
        )
    )