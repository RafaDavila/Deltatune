import {
  useCallback,
  useEffect,
  useState,
  type SubmitEvent,
} from "react";
import { Link } from "react-router";

import deltatuneLogo from "../assets/deltatune-logo.png";
import AttemptList from "../components/AttemptList";
import AudioPlayer from "../components/AudioPlayer";
import GuessForm from "../components/GuessForm";
import LivesDisplay from "../components/LivesDisplay";
import ResultModal from "../components/ResultModal";
import SiteFooter from "../components/SiteFooter";
import TutorialModal from "../components/TutorialModal";
import useAudioClip from "../hooks/useAudioClip";
import {
  getInfiniteAudioUrl,
  getSongs,
  resumeInfiniteGame,
  skipInfiniteGuess,
  startInfiniteGame,
  startNextInfiniteRound,
  submitInfiniteGuess,
  type InfiniteGameResponse,
} from "../services/deltatuneApi";
import type { AttemptResult } from "../types/game";
import { useAuth } from "../hooks/useAuth";

const DEFAULT_ATTEMPT_DURATIONS = [
  0.5,
  1,
  2,
  4,
  8,
  16,
];

const INFINITE_RUN_STORAGE_PREFIX =
  "deltatune-infinite-run";

const INFINITE_RECORD_STORAGE_KEY =
  "deltatune-infinite-record";

function loadInfiniteRecord(): number {
  const savedRecord = localStorage.getItem(
    INFINITE_RECORD_STORAGE_KEY,
  );

  if (savedRecord === null) {
    return 0;
  }
  const parsedRecord = Number(savedRecord);
  return Number.isInteger(parsedRecord) &&
    parsedRecord >= 0
    ? parsedRecord
    : 0;
}

function InfiniteGamePage() {
  const {
    user,
    isLoading: isAuthLoading,
  } = useAuth();

  const infiniteRunStorageKey = (
    `${INFINITE_RUN_STORAGE_PREFIX}-` +
    `${user?.id ?? "anonymous"}`
  );
  const [bestStreak, setBestStreak] =
    useState(loadInfiniteRecord);

  const updateBestStreak = useCallback(
    (currentStreak: number) => {
      setBestStreak((previousBestStreak) => {
        if (
          currentStreak <= previousBestStreak
        ) {
          return previousBestStreak;
        }

        localStorage.setItem(
          INFINITE_RECORD_STORAGE_KEY,
          currentStreak.toString(),
        );

        return currentStreak;
      });
    },
    [],
  );

  const [game, setGame] =
    useState<InfiniteGameResponse | null>(null);

  const [attemptResults, setAttemptResults] =
    useState<AttemptResult[]>([]);

  const [revealedSongTitle, setRevealedSongTitle] =
    useState<string | null>(null);

  const [songTitles, setSongTitles] =
    useState<string[]>([]);

  const [guess, setGuess] = useState("");

  const [isGameLoading, setIsGameLoading] =
    useState(true);

  const [isProgressLoaded, setIsProgressLoaded] =
    useState(false);

  const [isSubmitting, setIsSubmitting] =
    useState(false);

  const [isAdvancing, setIsAdvancing] =
    useState(false);

  const [gameError, setGameError] =
    useState<string | null>(null);

  const [guessError, setGuessError] =
    useState<string | null>(null);

  const [songCatalogError, setSongCatalogError] =
    useState<string | null>(null);

  const [isResultOpen, setIsResultOpen] =
    useState(false);

  const [isTutorialOpen, setIsTutorialOpen] =
    useState(false);

  const attemptDurations =
    game?.attemptDurations ??
    DEFAULT_ATTEMPT_DURATIONS;

  const failedAttempts = attemptResults.filter(
    (attempt) => attempt.status !== "correct",
  ).length;

  const currentAttempt = Math.min(
    failedAttempts,
    attemptDurations.length - 1,
  );

  const remainingLives = Math.max(
    attemptDurations.length - failedAttempts,
    0,
  );

  const hasWon = attemptResults.some(
    (attempt) => attempt.status === "correct",
  );

  const gameFinished =
    hasWon ||
    failedAttempts === attemptDurations.length;

  const maximumDuration =
    attemptDurations[
    attemptDurations.length - 1
    ];

  const unlockedDuration = gameFinished
    ? maximumDuration
    : attemptDurations[currentAttempt];

  const audioUrl = game
    ? getInfiniteAudioUrl(
      game.runId,
      game.roundId,
    )
    : undefined;

  const isGameUnavailable =
    isGameLoading ||
    !isProgressLoaded ||
    !game ||
    Boolean(gameError);

  const {
    audioRef,
    volume,
    setVolume,
    isPlaying,
    playAudio,
    stopAudio,
  } = useAudioClip({
    audioSource: audioUrl,
    clipDuration: unlockedDuration,
    disabled: isGameUnavailable,
  });

  useEffect(() => {
    let cancelled = false;

    async function loadSongCatalog() {
      try {
        const songs = await getSongs();

        if (!cancelled) {
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

        if (!cancelled) {
          setSongCatalogError(
            "Não foi possível carregar as sugestões.",
          );
        }
      }
    }

    loadSongCatalog();

    return () => {
      cancelled = true;
    };
  }, []);

  const continueButtonLabel = isAdvancing
    ? "Carregando..."
    : hasWon
      ? "Próxima música"
      : "Recomeçar";

  useEffect(() => {
    let cancelled = false;

    if (isAuthLoading) {
      return;
    }

    async function createNewGame() {
      const newGame = await startInfiniteGame();

      localStorage.setItem(
        infiniteRunStorageKey,
        newGame.runId,
      );

      return {
        game: newGame,
        attempts: [] as AttemptResult[],
        songTitle: null as string | null,
      };
    }

    async function loadInfiniteGame() {
          setIsGameLoading(true);
          setIsProgressLoaded(false);

          try {
            const savedRunId = localStorage.getItem(
              infiniteRunStorageKey,
            );

            let loadedGame;

            if (savedRunId) {
              try {
                const resumedGame =
                  await resumeInfiniteGame(savedRunId);

                loadedGame = {
                  game: resumedGame,
                  attempts: resumedGame.attempts,
                  songTitle: resumedGame.songTitle,
                };
              } catch {
                localStorage.removeItem(
                  infiniteRunStorageKey,
                );

                loadedGame = await createNewGame();
              }
            } else {
              loadedGame = await createNewGame();
            }

            if (cancelled) {
              return;
            }

            setGame(loadedGame.game);
            updateBestStreak(loadedGame.game.currentStreak,);
            setAttemptResults(loadedGame.attempts);
            setRevealedSongTitle(
              loadedGame.songTitle,
            );
            setGameError(null);
            setIsProgressLoaded(true);
          } catch (error) {
            if (cancelled) {
              return;
            }

            console.error(
              "Erro ao carregar modo infinito:",
              error,
            );

            setGame(null);
            setAttemptResults([]);
            setRevealedSongTitle(null);
            setGameError(
              "Não foi possível carregar o modo infinito.",
            );
          } finally {
            if (!cancelled) {
              setIsGameLoading(false);
            }
          }
        }

    void loadInfiniteGame();

      return () => {
        cancelled = true;
      };
    }, [
      infiniteRunStorageKey,
      isAuthLoading,
      updateBestStreak,
    ]);

  useEffect(() => {
    if (!gameFinished) {
      return;
    }

    const resultTimer = window.setTimeout(() => {
      setIsTutorialOpen(false);
      setIsResultOpen(true);
    }, 650);

    return () => {
      window.clearTimeout(resultTimer);
    };
  }, [gameFinished]);



  async function handleSkip() {
    if (
      gameFinished ||
      isGameUnavailable ||
      isSubmitting ||
      !game
    ) {
      return;
    }

    stopAudio();
    setIsSubmitting(true);
    setGuessError(null);

    try {
      const result = await skipInfiniteGuess(
        game.runId,
        game.roundId,
      );

      updateBestStreak(result.currentStreak);

      setAttemptResults((previous) => [
        ...previous,
        {
          answer: "Pulou",
          status: "skipped",
        },
      ]);

      setGame((previous) =>
        previous
          ? {
            ...previous,
            currentStreak:
              result.currentStreak,
          }
          : previous,
      );

      if (result.songTitle) {
        setRevealedSongTitle(
          result.songTitle,
        );
      }

      setGuess("");
    } catch (error) {
      console.error(
        "Erro ao pular tentativa:",
        error,
      );

      setGuessError(
        error instanceof Error
          ? error.message
          : "Não foi possível pular a tentativa.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleSubmit(
    event: SubmitEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const cleanedGuess = guess.trim();

    if (
      gameFinished ||
      isGameUnavailable ||
      isSubmitting ||
      !game ||
      !cleanedGuess
    ) {
      return;
    }

    stopAudio();
    setIsSubmitting(true);
    setGuessError(null);

    try {
      const result = await submitInfiniteGuess(
        game.runId,
        game.roundId,
        cleanedGuess,
      );

      updateBestStreak(result.currentStreak);

      setAttemptResults((previous) => [
        ...previous,
        {
          answer: cleanedGuess,
          status: result.correct
            ? "correct"
            : "wrong",
        },
      ]);

      setGame((previous) =>
        previous
          ? {
            ...previous,
            currentStreak:
              result.currentStreak,
          }
          : previous,
      );

      if (result.songTitle) {
        setRevealedSongTitle(
          result.songTitle,
        );
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
          : "Não foi possível validar o palpite.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleContinueGame() {
    if (
      !game ||
      !gameFinished ||
      isAdvancing
    ) {
      return;
    }

    stopAudio();
    setIsAdvancing(true);
    setGuessError(null);

    try {
      const nextGame = hasWon
        ? await startNextInfiniteRound(
          game.runId,
          game.roundId,
        )
        : await startInfiniteGame();

      localStorage.setItem(
        infiniteRunStorageKey,
        nextGame.runId,
      );

      setGame(nextGame);
      setAttemptResults([]);
      setRevealedSongTitle(null);
      setGuess("");
      setIsResultOpen(false);
    } catch (error) {
      console.error(
        "Erro ao continuar modo infinito:",
        error,
      );

      setGuessError(
        error instanceof Error
          ? error.message
          : "Não foi possível continuar o jogo.",
      );
    } finally {
      setIsAdvancing(false);
    }
  }

  function handleCloseTutorial(
    dontShowAgain: boolean,
  ) {
    if (dontShowAgain) {
      localStorage.setItem(
        "deltatune-hide-tutorial",
        "true",
      );
    }

    setIsTutorialOpen(false);
  }

  return (
    <main className="music-game">
      <header className="music-game__topbar">
        <Link className="back-link" to="/">
          ← Voltar
        </Link>

        <img
          className="music-game__logo"
          src={deltatuneLogo}
          alt="Deltatune"
        />

        <button
          className="tutorial-button"
          type="button"
          aria-label="Abrir tutorial"
          onClick={() =>
            setIsTutorialOpen(true)
          }
        >
          ?
        </button>
      </header>

      <section className="music-panel">
        <div className="music-panel__heading">
          <p>
            Continue acertando para aumentar
            sua sequência.
          </p>
        </div>

        <div
          className="daily-challenge"
          aria-label={
            game
              ? `Modo infinito, rodada ${game.roundNumber}`
              : "Carregando modo infinito"
          }
        >
          <span>Rodada:</span>

          <strong>
            {game
              ? String(
                game.roundNumber,
              ).padStart(3, "0")
              : "CARREGANDO"}
          </strong>
        </div>

        <p
          className="daily-challenge__countdown"
          aria-live="polite"
        >
          Sequência atual:{" "}
          <strong>
            {game?.currentStreak ?? 0}
          </strong>

          {" . "}
          Recorde:{" "}
          <strong>{bestStreak}</strong>
        </p>

        <LivesDisplay
          remainingLives={remainingLives}
          maximumLives={attemptDurations.length}
        />

        <AttemptList
          attemptDurations={attemptDurations}
          attemptResults={attemptResults}
        />

        <AudioPlayer
          audioRef={audioRef}
          audioUrl={audioUrl}
          attemptDurations={attemptDurations}
          currentAttempt={currentAttempt}
          unlockedDuration={unlockedDuration}
          gameFinished={gameFinished}
          isPlaying={isPlaying}
          volume={volume}
          challengeError={gameError}
          onPlay={playAudio}
          onStop={stopAudio}
          onVolumeChange={setVolume}
        />

        <GuessForm
          guess={guess}
          songTitles={songTitles}
          guessError={guessError}
          songCatalogError={songCatalogError}
          disabled={
            gameFinished ||
            isGameUnavailable ||
            isSubmitting ||
            isAdvancing
          }
          isSubmitting={isSubmitting}
          onGuessChange={setGuess}
          onSkip={handleSkip}
          onSubmit={handleSubmit}
        />

        {gameFinished && (
          <button
            className="result-modal__continue"
            type="button"
            disabled={isAdvancing}
            onClick={handleContinueGame}
          >
            {continueButtonLabel}
          </button>
        )}

        <SiteFooter />
      </section>

      {isTutorialOpen && (
        <TutorialModal
          onClose={handleCloseTutorial}
        />
      )}

      {isResultOpen && (
        <ResultModal
          hasWon={hasWon}
          songTitle={
            revealedSongTitle ??
            "Resposta não revelada"
          }
          attemptsUsed={attemptResults.length}
          remainingLives={remainingLives}
          isPlaying={isPlaying}
          revealLabel="A música desta rodada era"
          continueLabel={continueButtonLabel}

          onReplay={playAudio}
          onClose={() =>
            setIsResultOpen(false)
          }
          onContinue={handleContinueGame}
        />
      )}
    </main>
  );
}

export default InfiniteGamePage;
