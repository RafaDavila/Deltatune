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
        "aliases": (),
    },
    {
        "id": 2,
        "title": "Field of Hopes and Dreams",
        "chapter": 1,
        "aliases": (
            "Field of Hopes & Dreams",
        ),
    },
    {
        "id": 3,
        "title": "The World Revolving",
        "chapter": 1,
        "aliases": (),
    },
    {
        "id": 4,
        "title": "A Cyber's World?",
        "chapter": 2,
        "aliases": (
            "A Cybers World",
        ),
    },
    {
        "id": 5,
        "title": "Attack of the Killer Queen",
        "chapter": 2,
        "aliases": (),
    },
    {
        "id": 6,
        "title": "BIG SHOT",
        "chapter": 2,
        "aliases": (
            "Big Shot",
        ),
    },
)


def seed_songs() -> None:
    with Session(engine) as db:
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
                )
                db.add(song)
            else:
                song.title = song_data["title"]
                song.chapter = song_data["chapter"]

            existing_aliases = {
                song_alias.alias
                for song_alias in song.aliases
            }

            for alias in song_data["aliases"]:
                if alias not in existing_aliases:
                    song.aliases.append(
                        SongAliasModel(alias=alias),
                    )

        db.commit()

    print("Catálogo de músicas carregado com sucesso.")


if __name__ == "__main__":
    seed_songs()