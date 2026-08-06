import { Link } from "react-router";
import deltatuneLogo from "../assets/deltatune-logo.png";
import heartIcon from "../assets/heart.png";
import { useEffect, useRef, useState, type SubmitEvent } from "react";
import testSongAudio from "../assets/audio/BIG SHOT.mp3";
import TutorialModal from "../components/TutorialModal";
import SiteFooter from "../components/SiteFooter";

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

type AttemptResult = {
  answer: string;
  status: "skipped" | "wrong" | "correct";
}

function MusicGamePage() {
  const [guess, setGuess] = useState("");
  const [isTutorialOpen, setIsTutorialOpen] = useState(() => {
  return (
    localStorage.getItem("deltatune-hide-tutorial") !== "true"
  );
});
  const audioRef = useRef<HTMLAudioElement>(null);
  const stopTimerRef = 
          useRef<ReturnType<typeof setTimeout> | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [attemptResults, setAttemptResults] = useState<AttemptResult[]>([]);

  useEffect(() => {
    const audio = audioRef.current;

    return () => {
      if (stopTimerRef.current){
        clearTimeout(stopTimerRef.current);
      }
      audio?.pause();
    }
  }, [])
  const failedAttempts = attemptResults.filter(
    (result) => result.status !== "correct",
  ).length;
  const currentAttempt = Math.min (
    failedAttempts,
    attemptDurations.length -1,
  );

  const remainingLives = attemptDurations.length - failedAttempts;
  const hasWon = attemptResults.some(
    (result) => result.status === "correct",
  );
  const gameFinished = hasWon || failedAttempts === attemptDurations.length;
  const maximumDuration =
    attemptDurations[attemptDurations.length - 1];
  
  const unlockedDuration = gameFinished
    ? maximumDuration
    : attemptDurations[currentAttempt];
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

  async function handlePlay() {
  const audio = audioRef.current;

  if (!audio) {
    return;
  }

  stopAudio();

  try {
    await audio.play();
    setIsPlaying(true);

    const clipDuration =
      unlockedDuration * 1000;

    stopTimerRef.current = setTimeout(
      stopAudio,
      clipDuration,
    );
  } catch (error) {
    console.error("Não foi possível reproduzir o áudio:", error);
    stopAudio();
  }
}

  function handleSkip() {
    if (gameFinished) {
      return;
    }
    stopAudio();
    setAttemptResults((previousResults) => [
      ...previousResults,
      {
        answer: "Pulou",
        status: "skipped",
      },
    ]);
    setGuess("")
  }
  function handleSubmit(event: SubmitEvent<HTMLFormElement>,) {
    event.preventDefault();

    const cleanedGuess = guess.trim();

    if (gameFinished || !cleanedGuess) {
      return;
    }
    stopAudio();
    const isCorrect = 
      cleanedGuess.toLocaleLowerCase() ===
      dailySongTitle.toLocaleLowerCase();

    setAttemptResults((previousResults) => [
      ...previousResults,
      {
        answer: cleanedGuess,
        status: isCorrect ? "correct" : "wrong",
      },
    ]);
    setGuess("");
  }

function handleCloseTutorial(dontShowAgain: boolean) {
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
          onClick={() => setIsTutorialOpen(true)}
          >
            ?
        </button>
        
      </header>

      <section className="music-panel">
        <div className="music-panel__heading">
          <p>Escute o trecho e descubra qual música está tocando.</p>
        </div>

        <div
          className="daily-challenge"
          aria-label="Música do dia número 1"
        >
          <span>Música do dia</span>
          <strong>#001</strong>
        </div>

        <div className="lives">
          <div
            className="lives__hearts"
            aria-label= {`${remainingLives} de 6 tentativas restantes`}
          >
            {attemptDurations.map((duration, index) => (
              <img
                key={duration}
                className= {
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
            <div className={`attempt-slot attempt-slot--${
                    attemptResults[index]?.status ?? "empty"
            }`}
             key={duration}>
              <span className="attempt-slot__number">
                {index + 1}
              </span>
              <span
                className={
                  `attempt-slot__result attempt-slot__result--${
                    attemptResults[index]?.status ?? "empty"
                  }`
                }
              >
                {attemptResults[index]?.answer ?? ""}
              </span>

              <span className="attempt-slot__duration">
                {duration.toString().replace(".", ",")}s
              </span>
            </div>
          ))}
        </div>

        <section className="audio-player" >
          <audio
            ref={audioRef}
            src={testSongAudio}
            preload="auto"
            onEnded={stopAudio}
            />
          <div className="audio-player__info">
            <span>Trecho liberado</span>
            <strong>
              {unlockedDuration.toString().replace(".",",")}{" "}
              {unlockedDuration <= 1 ? "segundo" : "segundos"}
            </strong>
          </div>

          <div
            className="audio-timeline"
            aria-label="Primeiro trecho de seis liberado"
          >
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
            <span>
              {isPlaying? "Tocando..." : "Reproduzir"}
            </span>
          </button>
        </section>

        <form className="guess-form" onSubmit={handleSubmit}>
          <label className="guess-form__label" htmlFor="song-guess">
            Qual é a música?
          </label>
          <div className="guess-form__controls">
            <input
              id="song-guess"
              name="song-guess"
              type="text"
              list="song-options"
              placeholder="Digite o nome da música..."
              autoComplete="off"
              value={guess}
              onChange={(event) => setGuess(event.target.value)}
              disabled={gameFinished}

            />
            <datalist id="song-options">
              {songTitles.map((songTitle) => (
                <option key={songTitle} value={songTitle} />
              ))}
            </datalist>
            <button className="guess-button guess-button--skip" type="button" onClick={handleSkip} disabled={gameFinished}>
              Pular
            </button>

            <button className="guess-button guess-button--confirm" type="submit" disabled={gameFinished}>
              Confirmar
            </button>

          </div>
        </form>

        <SiteFooter />

        {isTutorialOpen && (
          <TutorialModal onClose={handleCloseTutorial} />
        )}

      </section>
      {isTutorialOpen && (
        <TutorialModal onClose={handleCloseTutorial} />
    )}
    </main>
  );
}

export default MusicGamePage;