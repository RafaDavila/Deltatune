from dataclasses import dataclass


@dataclass(frozen=True)
class Song:
    id: int
    title: str
    chapter: int
    aliases: tuple[str, ...] = ()


SONGS = (
    Song(
        id=1,
        title="Rude Buster",
        chapter=1,
    ),
    Song(
        id=2,
        title="Field of Hopes and Dreams",
        chapter=1,
        aliases=("Field of Hopes & Dreams",),
    ),
    Song(
        id=3,
        title="The World Revolving",
        chapter=1,
    ),
    Song(
        id=4,
        title="A Cyber's World?",
        chapter=2,
        aliases=("A Cybers World",),
    ),
    Song(
        id=5,
        title="Attack of the Killer Queen",
        chapter=2,
    ),
    Song(
        id=6,
        title="BIG SHOT",
        chapter=2,
        aliases=("Big Shot",),
    ),
)

SONGS_BY_ID = {
    song.id: song
    for song in SONGS
}

DAILY_ROTATION = (6, 1, 2, 3, 4, 5)