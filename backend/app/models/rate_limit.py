from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database import Base


class RateLimitModel(Base):
    __tablename__ = "rate_limits"

    __table_args__ = (
        CheckConstraint(
            "attempts >= 0",
            name="ck_rate_limits_attempts_nonnegative",
        ),
    )

    key_hash: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )