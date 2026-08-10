import { useEffect, useRef, useState, type ChangeEvent, type KeyboardEvent, type SubmitEvent, } from "react";
import { FaVolumeHigh, FaVolumeXmark } from "react-icons/fa6";
import { Link } from "react-router";
import testSongAudio from "../assets/audio/BIG SHOT.mp3";
import deltatuneLogo from "../assets/deltatune-logo.png";
import heartIcon from "../assets/heart.png";
import SiteFooter from "../components/SiteFooter";
import TutorialModal from "../components/TutorialModal";
import ResultModal from "../components/ResultModal";

const attemptDurations = [0.5, 1, 2, 4, 8, 16];
const dailySongTitle = "BIG SHOT";
const songTitles = [
  "Rude Buster",
  "Field of Hopes and Dreams",
  "Scarlet Forest",
  "The World Revolving",
  "A Cyber's World?",
  "Smart Race",
  "Attack of the Killer Queen",
  "BIG SHOT",
];

const dailyChallengeId = "001";

const gameStorageKey =
  `deltatune-game-${dailyChallengeId}`;

type AttemptResult = {
  answer: string;
  status: "skipped" | "wrong" | "correct";
};

function loadSavedAttemptResults(): AttemptResult[] {
  const savedGame = localStorage.getItem(gameStorageKey);

  if (!savedGame) {
    return [];
  }

  try {
    const parsedGame: unknown = JSON.parse(savedGame);

    if (!Array.isArray(parsedGame)) {
      return [];
    }

    return parsedGame
      .filter((item): item is AttemptResult => {
        if (typeof item !== "object" || item === null) {
          return false;
        }

        const attempt = item as Record<string, unknown>;

        const validStatus =
          attempt.status === "skipped" ||
          attempt.status === "wrong" ||
          attempt.status === "correct";

        return (
          typeof attempt.answer === "string" &&
          validStatus
        );
      })
      .slice(0, attemptDurations.length);
  } catch {
    return [];
  }
}

function MusicGamePage() {
  const [guess, setGuess] = useState("");
  const [isResultOpen, setIsResultOpen] = useState(false);
  const [isTutorialOpen, setIsTutorialOpen] = useState(
    () => localStorage.getItem("deltatune-hide-tutorial") !== "true",
  );
  const [volume, setVolume] = useState(() => {
    const savedVolume = localStorage.getItem("deltatune-volume");

    if (savedVolume === null) {
      return 0.6;
    }

    const parsedVolume = Number(savedVolume);
    return Number.isFinite(parsedVolume)
      ? Math.min(1, Math.max(0, parsedVolume))
      : 0.6;
  });
  const [isPlaying, setIsPlaying] = useState(false);
  const [isSuggestionsOpen, setIsSuggestionsOpen] =
    useState(false);

  const [activeSuggestionIndex, setActiveSuggestionIndex] =
    useState(-1);
  const [attemptResults, setAttemptResults] = useState<AttemptResult[]>(loadSavedAttemptResults);
  const audioRef = useRef<HTMLAudioElement>(null);
  const stopTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const failedAttempts = attemptResults.filter(
    (result) => result.status !== "correct",
  ).length;
  const currentAttempt = Math.min(failedAttempts, attemptDurations.length - 1);
  const remainingLives = attemptDurations.length - failedAttempts;
  const hasWon = attemptResults.some((result) => result.status === "correct");
  const gameFinished = hasWon || failedAttempts === attemptDurations.length;
  const normalizedGuess = guess.trim().toLocaleLowerCase();

  const filteredSongs = normalizedGuess
    ? songTitles
      .filter((songTitle) =>
        songTitle
          .toLocaleLowerCase()
          .includes(normalizedGuess),
      )
      .slice(0, 5)
    : [];

  const showSuggestions =
    isSuggestionsOpen &&
    normalizedGuess.length > 0 &&
    !gameFinished;
  const maximumDuration = attemptDurations[attemptDurations.length - 1];
  const unlockedDuration = gameFinished
    ? maximumDuration
    : attemptDurations[currentAttempt];
  useEffect(() => {
    if (!gameFinished) {
      return;
    }
    const resultTimer = setTimeout(() => {
      setIsTutorialOpen(false);
      setIsResultOpen(true);
    }, 650);
    return () => {
      clearTimeout(resultTimer);
    };
  }, [gameFinished]);
  function stopAudio() {
    if (stopTimerRef.current) {
      clearTimeout(stopTimerRef.current);
      stopTimerRef.current = null;
    }

    const audio = audioRef.current;

    if (audio) {
      audio.pause();
      audio.currentTime = 0;
    }

    setIsPlaying(false);
  }

  useEffect(() => {
    const audio = audioRef.current;

    if (audio) {
      audio.volume = volume;
    }

    localStorage.setItem("deltatune-volume", volume.toString());
  }, [volume]);

  useEffect(() => {
    const audio = audioRef.current;

    return () => {
      if (stopTimerRef.current) {
        clearTimeout(stopTimerRef.current);
      }

      audio?.pause();
    };
  }, []);

  async function handlePlay() {
    const audio = audioRef.current;

    if (!audio) {
      return;
    }

    stopAudio();

    try {
      await audio.play();
      setIsPlaying(true);
      stopTimerRef.current = setTimeout(stopAudio, unlockedDuration * 1000);
    } catch (error) {
      console.error("Não foi possível reproduzir o áudio:", error);
      stopAudio();
    }
  }

  useEffect(() => {
    localStorage.setItem(
      gameStorageKey,
      JSON.stringify(attemptResults),
    );
  }, [attemptResults]);

  function handleGuessChange(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    setGuess(event.target.value);
    setIsSuggestionsOpen(true);
    setActiveSuggestionIndex(-1);
  }

  function handleSelectSong(songTitle: string) {
    setGuess(songTitle);
    setIsSuggestionsOpen(false);
    setActiveSuggestionIndex(-1);
  }

  function handleGuessKeyDown(
    event: KeyboardEvent<HTMLInputElement>,
  ) {
    if (event.key === "Escape") {
      setIsSuggestionsOpen(false);
      setActiveSuggestionIndex(-1);
      return;
    }

    if (filteredSongs.length === 0) {
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      setIsSuggestionsOpen(true);

      setActiveSuggestionIndex((previousIndex) =>
        previousIndex >= filteredSongs.length - 1
          ? 0
          : previousIndex + 1,
      );
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      setIsSuggestionsOpen(true);

      setActiveSuggestionIndex((previousIndex) =>
        previousIndex <= 0
          ? filteredSongs.length - 1
          : previousIndex - 1,
      );
    }

    if (
      event.key === "Enter" &&
      isSuggestionsOpen &&
      activeSuggestionIndex >= 0
    ) {
      event.preventDefault();

      handleSelectSong(
        filteredSongs[activeSuggestionIndex],
      );
    }
  }

  function handleSkip() {
    if (gameFinished) {
      return;
    }

    setIsSuggestionsOpen(false);
    setActiveSuggestionIndex(-1);
    stopAudio();
    setAttemptResults((previousResults) => [
      ...previousResults,
      { answer: "Pulou", status: "skipped" },
    ]);
    setGuess("");
  }

  function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSuggestionsOpen(false);
    setActiveSuggestionIndex(-1);

    const cleanedGuess = guess.trim();

    if (gameFinished || !cleanedGuess) {
      return;
    }

    stopAudio();
    const isCorrect =
      cleanedGuess.toLocaleLowerCase() === dailySongTitle.toLocaleLowerCase();

    setAttemptResults((previousResults) => [
      ...previousResults,
      { answer: cleanedGuess, status: isCorrect ? "correct" : "wrong" },
    ]);
    setGuess("");
  }

  function handleCloseTutorial(dontShowAgain: boolean) {
    if (dontShowAgain) {
      localStorage.setItem("deltatune-hide-tutorial", "true");
    }

    setIsTutorialOpen(false);
  }

  return (
    <main className="music-game">
      <header className="music-game__topbar">
        <Link className="back-link" to="/">
          ← Voltar
        </Link>

        <img className="music-game__logo" src={deltatuneLogo} alt="Deltatune" />

        <button
          className="tutorial-button"
          type="button"
          aria-label="Abrir tutorial"
          onClick={() => setIsTutorialOpen(true)}
        >
          ?
        </button>
      </header>

      <section className="music-panel">
        <div className="music-panel__heading">
          <p>Escute o trecho e descubra qual música está tocando.</p>
        </div>

        <div className="daily-challenge" aria-label="Música do dia número 1">
          <span>Música do dia</span>
          <strong>#{dailyChallengeId}</strong>
        </div>

        <div className="lives">
          <div
            className="lives__hearts"
            aria-label={`${remainingLives} de 6 tentativas restantes`}
          >
            {attemptDurations.map((duration, index) => (
              <img
                key={duration}
                className={
                  index >= remainingLives
                    ? "lives__heart lives__heart--lost"
                    : "lives__heart"
                }
                src={heartIcon}
                alt=""
                aria-hidden="true"
              />
            ))}
          </div>

          <p>{remainingLives} de 6 tentativas restantes</p>
        </div>

        <div className="attempt-list">
          {attemptDurations.map((duration, index) => (
            <div
              key={duration}
              className={`attempt-slot attempt-slot--${attemptResults[index]?.status ?? "empty"
                }`}
            >
              <span className="attempt-slot__number">{index + 1}</span>
              <span
                className={`attempt-slot__result attempt-slot__result--${attemptResults[index]?.status ?? "empty"
                  }`}
              >
                {attemptResults[index]?.answer ?? ""}
              </span>
              <span className="attempt-slot__duration">
                {duration.toString().replace(".", ",")}s
              </span>
            </div>
          ))}
        </div>

        <section className="audio-player">
          <audio ref={audioRef} src={testSongAudio} preload="auto" onEnded={stopAudio} />

          <div className="audio-player__info">
            <span>Trecho liberado</span>
            <strong>
              {unlockedDuration.toString().replace(".", ",")} {unlockedDuration <= 1 ? "segundo" : "segundos"}
            </strong>
          </div>

          <div className="audio-timeline" aria-label="Primeiro trecho de seis liberado">
            {attemptDurations.map((duration, index) => (
              <span
                key={duration}
                className={
                  gameFinished || index <= currentAttempt
                    ? "audio-timeline__segment audio-timeline__segment--active"
                    : "audio-timeline__segment"
                }
              />
            ))}
          </div>

          <button
            className="play-button"
            type="button"
            aria-label="Reproduzir trecho da música"
            onClick={handlePlay}
          >
            <img src={heartIcon} alt="" aria-hidden="true" />
            <span>{isPlaying ? "Tocando..." : "Reproduzir"}</span>
          </button>

          <label className="volume-control">
            <span className="volume-control__icon" aria-hidden="true">
              {volume === 0 ? <FaVolumeXmark /> : <FaVolumeHigh />}
            </span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={volume}
              aria-label="Volume do áudio"
              aria-valuetext={`${Math.round(volume * 100)}%`}
              onChange={(event) => setVolume(Number(event.target.value))}
            />
            <strong>{Math.round(volume * 100)}%</strong>
          </label>
        </section>

        <form className="guess-form" onSubmit={handleSubmit}>
          <label className="guess-form__label" htmlFor="song-guess">
            Qual é a música?
          </label>
          <div className="guess-form__autocomplete">
            <input
              id="song-guess"
              name="song-guess"
              type="text"
              role="combobox"
              placeholder="Digite o nome da música..."
              autoComplete="off"
              value={guess}
              disabled={gameFinished}
              aria-autocomplete="list"
              aria-expanded={showSuggestions}
              aria-controls="song-suggestions"
              aria-activedescendant={
                activeSuggestionIndex >= 0
                  ? `song-suggestion-${activeSuggestionIndex}`
                  : undefined
              }
              onChange={handleGuessChange}
              onKeyDown={handleGuessKeyDown}
              onFocus={() => {
                if (guess.trim()) {
                  setIsSuggestionsOpen(true);
                }
              }}
              onBlur={() => setIsSuggestionsOpen(false)}
            />

            {showSuggestions && (
              <ul
                className="song-suggestions"
                id="song-suggestions"
                role="listbox"
              >
                {filteredSongs.length > 0 ? (
                  filteredSongs.map((songTitle, index) => (
                    <li
                      id={`song-suggestion-${index}`}
                      key={songTitle}
                      role="option"
                      aria-selected={
                        index === activeSuggestionIndex
                      }
                    >
                      <button
                        className={`song-suggestions__option ${index === activeSuggestionIndex
                          ? "song-suggestions__option--active"
                          : ""
                          }`}
                        type="button"
                        onPointerDown={(event) => {
                          event.preventDefault();
                          handleSelectSong(songTitle);
                        }}
                        onClick={() =>
                          handleSelectSong(songTitle)
                        }
                      >
                        {songTitle}

                      </button>

                    </li>
                  ))
                ) : (
                  <li className="song-suggestions__empty">
                    Nenhuma música encontrada
                  </li>
                )}

              </ul>
            )}

            <button
              className="guess-button guess-button--skip"
              type="button"
              onClick={handleSkip}
              disabled={gameFinished}
            >
              Pular
            </button>
            <button
              className="guess-button guess-button--confirm"
              type="submit"
              disabled={gameFinished}
            >
              Confirmar
            </button>
          </div>
        </form>

        <SiteFooter />
      </section>

      {isTutorialOpen && <TutorialModal onClose={handleCloseTutorial} />}
      {isResultOpen && (
        <ResultModal
          hasWon={hasWon}
          songTitle={dailySongTitle}
          attemptsUsed={attemptResults.length}
          remainingLives={remainingLives}
          isPlaying={isPlaying}
          onReplay={handlePlay}
          onClose={() => setIsResultOpen(false)}
        />
      )}
    </main>
  );
}

export default MusicGamePage;
