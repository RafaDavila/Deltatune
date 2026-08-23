from pathlib import Path
import subprocess
import sys


CLIP_DURATION = 16

BACKEND_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BACKEND_DIR / "audio_sources"
OUTPUT_DIR = BACKEND_DIR / "media" / "audio"

SUPPORTED_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".flac",
    ".ogg",
    ".m4a",
}

SONG_TITLES = [
    "Beginning",
    "The Legend",
    "Lancer",
    "Rude Buster",
    "Empty Town",
    "Field of Hopes and Dreams",
    "Scarlet Forest",
    "Vs. Susie",
    "Rouxls Kaard",
    "Chaos King",
    "THE WORLD REVOLVING",
    "A Town Called Hometown",
    "Don't Forget",
    "My Castle Town",
    "A CYBER'S WORLD?",
    "Cyber Battle",
    "Smart Race",
    "Spamton",
    "Pandora Palace",
    "Lost Girl",
    "Attack of the Killer Queen",
    "BIG SHOT",
    "sans.",
]

SOURCE_NAMES = {
    "A CYBER'S WORLD?": "A Cybers World",
    "sans.": "sans",
}


def normalize_name(name: str) -> str:
    return (
        name.casefold()
        .replace("’", "'")
        .strip()
    )


def get_audio_duration(audio_path: Path) -> float:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(audio_path),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )

    return float(result.stdout.strip())


def process_audio(
    source_path: Path,
    output_path: Path,
) -> None:
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(source_path),
        "-t",
        str(CLIP_DURATION),
        "-vn",
        "-af",
        "loudnorm=I=-16:LRA=11:TP=-1.5",
        "-codec:a",
        "libmp3lame",
        "-b:a",
        "192k",
        str(output_path),
    ]

    subprocess.run(
        command,
        check=True,
    )


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    source_files = {
        normalize_name(file.stem): file
        for file in INPUT_DIR.iterdir()
        if (
            file.is_file()
            and file.suffix.casefold()
            in SUPPORTED_EXTENSIONS
        )
    }

    processed_files = 0

    for index, song_title in enumerate(
        SONG_TITLES,
        start=1,
    ):
        output_path = (
            OUTPUT_DIR / f"track-{index:03d}.mp3"
        )

        source_name = SOURCE_NAMES.get(
            song_title,
            song_title,
        )

        source_path = source_files.get(
            normalize_name(source_name),
        )

        if source_path is None and output_path.exists():
            print(
                f"Faixa já processada: {output_path.name}",
            )
            processed_files += 1
            continue

        if source_path is None:
            print(
                f"Arquivo não encontrado: {source_name}",
            )
            continue

        duration = get_audio_duration(source_path)

        if duration < CLIP_DURATION:
            print(
                f"Áudio muito curto: {source_path.name} "
                f"({duration:.1f} segundos)",
            )
            continue

        print(
            f"Processando {song_title} "
            f"-> {output_path.name}",
        )

        process_audio(
            source_path,
            output_path,
        )

        processed_files += 1

    print(
        f"\nProcessamento concluído: "
        f"{processed_files} de "
        f"{len(SONG_TITLES)} faixas.",
    )

    if processed_files != len(SONG_TITLES):
        sys.exit(1)


if __name__ == "__main__":
    main()
