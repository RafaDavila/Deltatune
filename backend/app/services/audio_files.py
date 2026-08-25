from pathlib import Path


BACKEND_DIRECTORY = (
    Path(__file__).resolve().parents[2]
)

AUDIO_DIRECTORY = (
    BACKEND_DIRECTORY / "media" / "audio"
)


def find_audio_file(
    audio_key: str,
) -> Path | None:
    if Path(audio_key).name != audio_key:
        return None

    audio_path = (
        AUDIO_DIRECTORY / f"{audio_key}.mp3"
    )

    if not audio_path.is_file():
        return None

    return audio_path