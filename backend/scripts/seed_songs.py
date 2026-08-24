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
        "audio_key": "track-015",
        "aliases": ("A Cybers World",),
    },
    {
        "id": 5,
        "title": "Attack of the Killer Queen",
        "chapter": 2,
        "audio_key": "track-021",
        "aliases": (),
    },
    {
        "id": 6,
        "title": "BIG SHOT",
        "chapter": 2,
        "audio_key": "track-022",
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
    {
        "id": 17,
        "title": "My Castle Town",
        "chapter": 2,
        "aliases": (),
        "audio_key": "track-014",
    },
    {
        "id": 18,
        "title": "Cyber Battle",
        "chapter": 2,
        "aliases": (),
        "audio_key": "track-016",
    },
    {
        "id": 19,
        "title": "Smart Race",
        "chapter": 2,
        "aliases": (),
        "audio_key": "track-017",
    },
    {
        "id": 20,
        "title": "Spamton",
        "chapter": 2,
        "aliases": (),
        "audio_key": "track-018",
    },
    {
        "id": 21,
        "title": "Pandora Palace",
        "chapter": 2,
        "aliases": (),
        "audio_key": "track-019",
    },
    {
        "id": 22,
        "title": "Lost Girl",
        "chapter": 2,
        "aliases": (),
        "audio_key": "track-020",
    },
    {
        "id": 23,
        "title": "sans.",
        "chapter": 2,
        "aliases": ("sans",),
        "audio_key": "track-023",
    },
    {
        "id": 24,
        "title": "Flashback",
        "chapter": 3,
        "audio_key": "track-024",
        "aliases": ("Flashback (Excerpt)",),
    },
    {
        "id": 25,
        "title": "Ruder Buster",
        "chapter": 3,
        "audio_key": "track-025",
        "aliases": (),
    },
    {
        "id": 26,
        "title": "Welcome to the Green Room",
        "chapter": 3,
        "audio_key": "track-026",
        "aliases": (),
    },
    {
        "id": 27,
        "title": "Raise Up Your Bat",
        "chapter": 3,
        "audio_key": "track-027",
        "aliases": (),
    },
    {
        "id": 28,
        "title": "Glowing Snow",
        "chapter": 3,
        "audio_key": "track-028",
        "aliases": (),
    },
    {
        "id": 29,
        "title": "TV WORLD",
        "chapter": 3,
        "audio_key": "track-029",
        "aliases": ("TV World",),
    },
    {
        "id": 30,
        "title": "It's TV Time!",
        "chapter": 3,
        "audio_key": "track-030",
        "aliases": ("Its TV Time",),
    },
    {
        "id": 31,
        "title": "Black Knife",
        "chapter": 3,
        "audio_key": "track-031",
        "aliases": (),
    },
    {
        "id": 32,
        "title": "NORTHERNLIGHT",
        "chapter": 3,
        "audio_key": "track-032",
        "aliases": ("Northern Light",),
    },
    {
        "id": 33,
        "title": "GLACEIR",
        "chapter": 3,
        "audio_key": "track-033",
        "aliases": ("Glacier",),
    },
    {
        "id": 34,
        "title": "BURNING EYES",
        "chapter": 3,
        "audio_key": "track-034",
        "aliases": ("Burning Eyes",),
    },
    {
        "id": 35,
        "title": "Another day in hometown",
        "chapter": 4,
        "audio_key": "track-035",
        "aliases": (),
    },
    {
        "id": 36,
        "title": "Castle Funk",
        "chapter": 4,
        "audio_key": "track-036",
        "aliases": (),
    },
    {
        "id": 37,
        "title": "Dark Sanctuary",
        "chapter": 4,
        "audio_key": "track-037",
        "aliases": ("Dark Sanctuary feat. Itoki Hana",),
    },
    {
        "id": 38,
        "title": "From Now On (Battle 2)",
        "chapter": 4,
        "audio_key": "track-038",
        "aliases": ("From Now On",),
    },
    {
        "id": 39,
        "title": "Gyaa Ha ha!",
        "chapter": 4,
        "audio_key": "track-039",
        "aliases": (
            "Gyaa Ha Ha",
            "Gya Ha Ha",
        ),
    },
    {
        "id": 40,
        "title": "A DARK ZONE",
        "chapter": 4,
        "audio_key": "track-040",
        "aliases": (),
    },
    {
        "id": 41,
        "title": "Ever Higher",
        "chapter": 4,
        "audio_key": "track-041",
        "aliases": (),
    },
    {
        "id": 42,
        "title": "Hammer of Justice",
        "chapter": 4,
        "audio_key": "track-042",
        "aliases": (),
    },
    {
        "id": 43,
        "title": "The Third Sanctuary",
        "chapter": 4,
        "audio_key": "track-043",
        "aliases": (),
    },
    {
        "id": 44,
        "title": "GUARDIAN",
        "chapter": 4,
        "audio_key": "track-044",
        "aliases": (),
    },
    {
        "id": 45,
        "title": "Need a hand!?",
        "chapter": 4,
        "audio_key": "track-045",
        "aliases": (
            "Need a hand",
            "Need a hand!",
        ),
    },
    {
        "id": 46,
        "title": "The place where it rained",
        "chapter": 4,
        "audio_key": "track-046",
        "aliases": (),
    },
    {
        "id": 47,
        "title": "Neverending Night",
        "chapter": 4,
        "audio_key": "track-047",
        "aliases": ("Never Ending Night",),
    },
    {
        "id": 48,
        "title": "Air Waves",
        "chapter": 4,
        "audio_key": "track-048",
        "aliases": (
            "Airwaves",
            "AIRWAVES",
        ),
    },
    {
        "id": 49,
        "title": "Festival",
        "chapter": 5,
        "audio_key": "track-049",
        "aliases": (),
    },
    {
        "id": 50,
        "title": "Garden of Hopes and Dreams",
        "chapter": 5,
        "audio_key": "track-050",
        "aliases": ("Toby Fox & insaneintherainmusic - " "Garden of Hopes and Dreams",),
    },
    {
        "id": 51,
        "title": "Who might you be?",
        "chapter": 5,
        "audio_key": "track-051",
        "aliases": ("Who might you be",),
    },
    {
        "id": 52,
        "title": "Petal Dance",
        "chapter": 5,
        "audio_key": "track-052",
        "aliases": (),
    },
    {
        "id": 53,
        "title": "Sunset of Seven Suns",
        "chapter": 5,
        "audio_key": "track-053",
        "aliases": (),
    },
    {
        "id": 54,
        "title": "Flower King",
        "chapter": 5,
        "audio_key": "track-054",
        "aliases": (),
    },
    {
        "id": 55,
        "title": "Flower Castle",
        "chapter": 5,
        "audio_key": "track-055",
        "aliases": (),
    },
    {
        "id": 56,
        "title": "Cutie Mew Mew Magic",
        "chapter": 5,
        "audio_key": "track-056",
        "aliases": (),
    },
    {
        "id": 57,
        "title": "Running Sky",
        "chapter": 5,
        "audio_key": "track-057",
        "aliases": (),
    },
    {
        "id": 58,
        "title": "Flower Man",
        "chapter": 5,
        "audio_key": "track-058",
        "aliases": ("Flower Man feat. Camellia",),
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
