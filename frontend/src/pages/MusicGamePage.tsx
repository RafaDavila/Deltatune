import { useEffect, useRef, useState, type ChangeEvent, type KeyboardEvent, type SubmitEvent, } from "react";
import { Link } from "react-router";
import deltatuneLogo from "../assets/deltatune-logo.png";
import SiteFooter from "../components/SiteFooter";
import TutorialModal from "../components/TutorialModal";
import ResultModal from "../components/ResultModal";
import { getDailyAudioUrl, getSongs, resumeDailyChallenge, skipDailyGuess, startDailyChallenge, submitDailyGuess, type DailyChallengeResponse, } from "../services/deltatuneApi";
import LivesDisplay from "../components/LivesDisplay";
import type { AttemptResult } from "../types/game";
import AttemptList from "../components/AttemptList";
import AudioPlayer from "../components/AudioPlayer";

const DEFAULT_ATTEMPT_DURATIONS = [
  0.5,
  1,
  2,
  4,
  8,
  16,
];



const GAME_SESSION_STORAGE_KEY =
  "deltatune-daily-session";


function formatCountdown(
  remainingMilliseconds: number,
): string {
  const totalSeconds = Math.floor(
    remainingMilliseconds / 1000,
  );

  const hours = Math.floor(totalSeconds / 3600);

  const minutes = Math.floor(
    (totalSeconds % 3600) / 60,
  );

  const seconds = totalSeconds % 60;

  return [hours, minutes, seconds]
    .map((value) =>
      value.toString().padStart(2, "0"),
    )
    .join(":");
}

function MusicGamePage() {

  const [sessionId, setSessionId] =
    useState<string | null>(null);

  const [
    revealedSongTitle,
    setRevealedSongTitle,
  ] = useState<string | null>(null);

  const [currentTime, setCurrentTime] =
    useState(() => Date.now());

  const [isChallengeLoading, setIsChallengeLoading] =
    useState(true);

  const [isProgressLoaded, setIsProgressLoaded] =
    useState(false);

  const [isSubmittingGuess, setIsSubmittingGuess] =
    useState(false);

  const [guessError, setGuessError] =
    useState<string | null>(null);
  const [dailyChallenge, setDailyChallenge] = useState<DailyChallengeResponse | null>(null);
  const [challengeError, setChallengeError] = useState<string | null>(null);
  const [songTitles, setSongTitles] =
    useState<string[]>([]);

  const [songCatalogError, setSongCatalogError] =
    useState<string | null>(null);
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
  const [attemptResults, setAttemptResults] = useState<AttemptResult[]>([]);
  const audioRef = useRef<HTMLAudioElement>(null);
  const stopTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const attemptDurations =
    dailyChallenge?.attemptDurations ??
    DEFAULT_ATTEMPT_DURATIONS;

  const dailyAudioUrl = dailyChallenge
    ? getDailyAudioUrl(
      dailyChallenge.challengeId,
    )
    : undefined;

  const remainingResetTime = dailyChallenge
    ? Math.max(
      new Date(
        dailyChallenge.nextResetAt,
      ).getTime() - currentTime,
      0,
    )
    : 0;

  const resetCountdown = dailyChallenge
    ? formatCountdown(remainingResetTime)
    : "--:--:--";

  const isGameUnavailable =
    isChallengeLoading ||
    !isProgressLoaded ||
    !dailyChallenge ||
    !sessionId ||
    Boolean(challengeError);
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
    !gameFinished &&
    !songCatalogError;
  const maximumDuration = attemptDurations[attemptDurations.length - 1];
  const unlockedDuration = gameFinished
    ? maximumDuration
    : attemptDurations[currentAttempt];
  useEffect(() => {
    let isCancelled = false;

    async function loadSongCatalog() {
      try {
        const songs = await getSongs();

        if (!isCancelled) {
          setSongTitles(
            songs.map((song) => song.title),
          );
          setSongCatalogError(null);
        }
      } catch (error) {
        console.error(
          "Erro ao carregar catálogo:",
          error,
        );

        if (!isCancelled) {
          setSongCatalogError(
            "Não foi possível carregar as sugestões.",
          );
        }
      }
    }

    loadSongCatalog();

    return () => {
      isCancelled = true;
    };
  }, []);
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
    const intervalid = window.setInterval(() => {
      setCurrentTime(Date.now());
    }, 1000);
    return () => {
      window.clearInterval(intervalid);
    }
  }, []);

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

    if (!audio || isGameUnavailable) {
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
    if (!dailyChallenge || !isProgressLoaded) {
      return;
    }

    const gameStorageKey =
      `deltatune-game-${dailyChallenge.challengeId}`;

    localStorage.setItem(
      gameStorageKey,
      JSON.stringify(attemptResults),
    );
  }, [
    attemptResults,
    dailyChallenge,
    isProgressLoaded,
  ]);

  useEffect(() => {
    let cancelled = false;

    async function createNewSession() {
      const challenge = await startDailyChallenge();

      localStorage.setItem(
        GAME_SESSION_STORAGE_KEY,
        challenge.sessionId,
      );

      return {
        challenge,
        attempts: [] as AttemptResult[],
        songTitle: null as string | null,
      };
    }

    async function loadDailyChallenge() {
      setIsChallengeLoading(true);
      setIsProgressLoaded(false);

      try {
        const savedSessionId = localStorage.getItem(
          GAME_SESSION_STORAGE_KEY,
        );

        let loadedGame;

        if (savedSessionId) {
          try {
            const resumedGame =
              await resumeDailyChallenge(
                savedSessionId,
              );

            loadedGame = {
              challenge: resumedGame,
              attempts: resumedGame.attempts,
              songTitle: resumedGame.songTitle,
            };
          } catch {
            localStorage.removeItem(
              GAME_SESSION_STORAGE_KEY,
            );

            loadedGame =
              await createNewSession();
          }
        } else {
          loadedGame =
            await createNewSession();
        }

        if (cancelled) {
          return;
        }

        setDailyChallenge(loadedGame.challenge);
        setSessionId(
          loadedGame.challenge.sessionId,
        );
        setAttemptResults(loadedGame.attempts);
        setRevealedSongTitle(
          loadedGame.songTitle,
        );
        setChallengeError(null);
        setIsProgressLoaded(true);
      } catch (error) {
        if (cancelled) {
          return;
        }

        console.error(
          "Erro ao carregar partida:",
          error,
        );

        setDailyChallenge(null);
        setSessionId(null);
        setAttemptResults([]);
        setRevealedSongTitle(null);
        setChallengeError(
          "Não foi possível carregar a partida.",
        );
      } finally {
        if (!cancelled) {
          setIsChallengeLoading(false);
        }
      }
    }

    loadDailyChallenge();

    return () => {
      cancelled = true;
    };
  }, []);

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

  async function handleSkip() {
    if (
      gameFinished ||
      isGameUnavailable ||
      isSubmittingGuess ||
      !dailyChallenge ||
      !sessionId
    ) {
      return;
    }

    setIsSuggestionsOpen(false);
    setActiveSuggestionIndex(-1);
    stopAudio();
    setIsSubmittingGuess(true);
    setGuessError(null);

    try {
      const result = await skipDailyGuess(
        sessionId,
        dailyChallenge.challengeId,
      );

      setAttemptResults((previousResults) => [
        ...previousResults,
        {
          answer: "Pulou",
          status: "skipped",
        },
      ]);

      if (result.songTitle) {
        setRevealedSongTitle(result.songTitle);
      }

      setGuess("");
    } catch (error) {
      console.error(
        "Erro ao pular tentativa:",
        error,
      );

      setGuessError(
        "Não foi possível pular a tentativa. Tente novamente.",
      );
    } finally {
      setIsSubmittingGuess(false);
    }
  }

  async function handleSubmit(
    event: SubmitEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setIsSuggestionsOpen(false);
    setActiveSuggestionIndex(-1);

    const cleanedGuess = guess.trim();

    if (
      gameFinished ||
      isGameUnavailable ||
      isSubmittingGuess ||
      !dailyChallenge ||
      !sessionId ||
      !cleanedGuess
    ) {
      return;
    }

    stopAudio();
    setIsSubmittingGuess(true);
    setGuessError(null);

    try {
      const result = await submitDailyGuess(
        sessionId,
        dailyChallenge.challengeId,
        cleanedGuess,
      );

      setAttemptResults((previousResults) => [
        ...previousResults,
        {
          answer: cleanedGuess,
          status: result.correct
            ? "correct"
            : "wrong",
        },
      ]);

      if (result.songTitle) {
        setRevealedSongTitle(result.songTitle);
      }

      setGuess("");
    } catch (error) {
      console.error(
        "Erro ao validar palpite:",
        error,
      );

      setGuessError(
        error instanceof Error
        ? error.message
        :"Não foi possível validar o palpite. Tente novamente.",
      );
    } finally {
      setIsSubmittingGuess(false);
    }
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

        <div className="daily-challenge" aria-label={
          dailyChallenge
            ? `Música do dia número ${dailyChallenge.challengeNumber}`
            : "Carregando música do dia"
        }>

          <span>Música do dia:</span>
          <strong>{dailyChallenge
            ? `${String(
              dailyChallenge.challengeNumber,
            ).padStart(2, "0")}`
            : "CARREGANDO"}
          </strong>
        </div>
        <p
          className="daily-challenge__countdown"
          aria-live="polite"
        >
          Próxima música em{" "}
          <strong>{resetCountdown}</strong>
        </p>

        <LivesDisplay
          remainingLives={remainingLives}
          maximumLives={attemptDurations.length}
        ></LivesDisplay>

        <AttemptList
          attemptDurations={attemptDurations}
          attemptResults={attemptResults}
        ></AttemptList>

        <AudioPlayer
          audioRef={audioRef}
          audioUrl={dailyAudioUrl}
          attemptDurations={attemptDurations}
          currentAttempt={currentAttempt}
          unlockedDuration={unlockedDuration}
          gameFinished={gameFinished}
          isPlaying={isPlaying}
          volume={volume}
          challengeError={challengeError}
          onPlay={handlePlay}
          onStop={stopAudio}
          onVolumeChange={setVolume}
        />

        <form className="guess-form" onSubmit={handleSubmit}>
          <label className="guess-form__label" htmlFor="song-guess">
            Qual é a música?
          </label>
          {guessError && (
            <p className="guess-form__error" role="alert">
              {guessError}
            </p>
          )}
          {songCatalogError && (
            <p
              className="guess-form__error"
              role="alert"
            >
              {songCatalogError}
            </p>
          )}
          <div className="guess-form__autocomplete">
            <input
              id="song-guess"
              name="song-guess"
              type="text"
              role="combobox"
              placeholder="Digite o nome da música..."
              autoComplete="off"
              value={guess}
              disabled={
                gameFinished ||
                isGameUnavailable ||
                isSubmittingGuess
              }
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
              disabled={
                gameFinished ||
                isGameUnavailable ||
                isSubmittingGuess
              }
            >
              Pular
            </button>
            <button
              className="guess-button guess-button--confirm"
              type="submit"
              disabled={
                gameFinished ||
                isGameUnavailable ||
                isSubmittingGuess
              }
            >
              {isSubmittingGuess
                ? "Validando..."
                : "Confirmar"}
            </button>
          </div>
        </form>

        <SiteFooter />
      </section>

      {isTutorialOpen && <TutorialModal onClose={handleCloseTutorial} />}
      {isResultOpen && (
        <ResultModal
          hasWon={hasWon}
          songTitle={revealedSongTitle ?? "Resposta não revelada"}
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
