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
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class GameSessionModel(Base):
    __tablename__ = "game_sessions"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    challenge_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    attempts: Mapped[list["AttemptModel"]] = relationship(
        back_populates="game_session",
        cascade="all, delete-orphan",
        order_by="AttemptModel.attempt_number",
    )


class AttemptModel(Base):
    __tablename__ = "attempts"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "attempt_number",
            name="uq_attempt_session_number",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    session_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "game_sessions.id",
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

    game_session: Mapped["GameSessionModel"] = relationship(
        back_populates="attempts",
    )