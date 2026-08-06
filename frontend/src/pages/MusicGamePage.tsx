import { Link } from "react-router";
import deltatuneLogo from "../assets/deltatune-logo.png";
import heartIcon from "../assets/heart.png";
import { useState } from "react";

const attemptDurations = [0.5, 1, 2, 4, 8, 16];

type AttemptResult = {
  answer: string;
  status: "skipped" | "wrong" | "correct";
}

function MusicGamePage() {
  const [guess, setGuess] = useState("");
  const [attemptResults, setAttemptResults] = useState<AttemptResult[]>([]);
  const attemptsUsed = attemptResults.length;
  const currentAttempt = Math.min (
    attemptsUsed,
    attemptDurations.length -1,
  );

  const remainingLives = attemptDurations.length - attemptsUsed;
  const gameFinished = attemptsUsed === attemptDurations.length;
  function handleSkip() {
    if (gameFinished) {
      return;
    }
    setAttemptResults((previousResults) => [
      ...previousResults,
      {
        answer: "Pulou",
        status: "skipped",
      },
    ]);
    setGuess("")
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
            <div className="attempt-slot" key={duration}>
              <span className="attempt-slot__number">
                {index + 1}
              </span>
              <span
                className={
                  attemptResults[index]?.status === "skipped"
                  ? "attempt-slot__result attempt-slot__result--skipped"
                  : "attempt-slot__result"
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

        <section className="audio-player">
          <div className="audio-player__info">
            <span>Trecho liberado</span>
            <strong>
              {attemptDurations[currentAttempt].toString().replace(".",",")}{" "}
              {attemptDurations[currentAttempt] <= 1
              ? "segundo"
              : "segundos"} 
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
                  index <= currentAttempt
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
          >
            <img src={heartIcon} alt="" aria-hidden="true" />
            <span>Reproduzir</span>
          </button>
        </section>

        <form className="guess-form" onSubmit={(e) => e.preventDefault()}>
          <label className="guess-form__label" htmlFor="song-guess">
            Qual é a música?
          </label>
          <div className="guess-form__controls">
            <input
              id="song-guess"
              name="song-guess"
              type="text"
              placeholder="Digite o nome da música..."
              autoComplete="off"
              value={guess}
              onChange={(event) => setGuess(event.target.value)}

            />
            <button className="guess-button guess-button--skip" type="button" onClick={handleSkip} disabled={gameFinished}>
              Pular
            </button>

            <button className="guess-button guess-button--confirm" type="submit">
              Confirmar
            </button>

          </div>
        </form>

      </section>
    </main>
  );
}

export default MusicGamePage;