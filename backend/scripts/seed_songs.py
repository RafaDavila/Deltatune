from sqlalchemy.orm import Session

from app.database import engine
from app.models.song import (
    SongAliasModel,
    SongModel,
)

SONG_SEEDS = (
    {
        "id": 1,
        "title": "Rude Buster",
        "chapter": 1,
        "audio_key": "track-004",
        "aliases": (),
    },
    {
        "id": 2,
        "title": "Field of Hopes and Dreams",
        "chapter": 1,
        "audio_key": "track-006",
        "aliases": ("Field of Hopes & Dreams",),
    },
    {
        "id": 3,
        "title": "The World Revolving",
        "chapter": 1,
        "audio_key": "track-011",
        "aliases": ("The World Revolving",),
    },
    {
        "id": 4,
        "title": "A Cyber's World?",
        "chapter": 2,
        "audio_key": None,
        "aliases": ("A Cybers World",),
    },
    {
        "id": 5,
        "title": "Attack of the Killer Queen",
        "chapter": 2,
        "audio_key": None,
        "aliases": (),
    },
    {
        "id": 6,
        "title": "BIG SHOT",
        "chapter": 2,
        "audio_key": None,
        "aliases": ("Big Shot",),
    },
    {
        "id": 7,
        "title": "Beginning",
        "chapter": 1,
        "audio_key": "track-001",
        "aliases": (),
    },
    {
        "id": 8,
        "title": "The Legend",
        "chapter": 1,
        "audio_key": "track-002",
        "aliases": (),
    },
    {
        "id": 9,
        "title": "Lancer",
        "chapter": 1,
        "audio_key": "track-003",
        "aliases": (),
    },
    {
        "id": 10,
        "title": "Empty Town",
        "chapter": 1,
        "audio_key": "track-005",
        "aliases": (),
    },
    {
        "id": 11,
        "title": "Scarlet Forest",
        "chapter": 1,
        "audio_key": "track-007",
        "aliases": (),
    },
    {
        "id": 12,
        "title": "Vs. Susie",
        "chapter": 1,
        "audio_key": "track-008",
        "aliases": ("Vs Susie",),
    },
    {
        "id": 13,
        "title": "Rouxls Kaard",
        "chapter": 1,
        "audio_key": "track-009",
        "aliases": (),
    },
    {
        "id": 14,
        "title": "Chaos King",
        "chapter": 1,
        "audio_key": "track-010",
        "aliases": (),
    },
    {
        "id": 15,
        "title": "A Town Called Hometown",
        "chapter": 1,
        "audio_key": "track-012",
        "aliases": (),
    },
    {
        "id": 16,
        "title": "Don't Forget",
        "chapter": 1,
        "audio_key": "track-013",
        "aliases": ("Dont Forget",),
    },
)


def seed_songs(db: Session) -> None:
    for song_data in SONG_SEEDS:
        song = db.get(
            SongModel,
            song_data["id"],
        )

        if song is None:
            song = SongModel(
                id=song_data["id"],
                title=song_data["title"],
                chapter=song_data["chapter"],
                audio_key=song_data["audio_key"],
            )
            db.add(song)
        else:
            song.title = song_data["title"]
            song.chapter = song_data["chapter"]
            song.audio_key = song_data["audio_key"]

        existing_aliases = {song_alias.alias for song_alias in song.aliases}

        for alias in song_data["aliases"]:
            if alias not in existing_aliases:
                song.aliases.append(
                    SongAliasModel(alias=alias),
                )

    db.commit()


def main() -> None:
    with Session(engine) as db:
        seed_songs(db)

    print("Catálogo de músicas carregado com sucesso.")


if __name__ == "__main__":
    main()
