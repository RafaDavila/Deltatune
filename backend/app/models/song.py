from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database import Base


class SongModel(Base):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    chapter: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    audio_key: Mapped[str | None] = mapped_column(
    String(50),
    nullable=True,
    unique=True,
)


    aliases: Mapped[list["SongAliasModel"]] = relationship(
        back_populates="song",
        cascade="all, delete-orphan",
    )


class SongAliasModel(Base):
    __tablename__ = "song_aliases"
    __table_args__ = (
        UniqueConstraint(
            "song_id",
            "alias",
            name="uq_song_alias",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    song_id: Mapped[int] = mapped_column(
        ForeignKey(
            "songs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    alias: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    song: Mapped["SongModel"] = relationship(
        back_populates="aliases",
    )


