import { Link } from "react-router";
import deltatuneLogo from "../assets/deltatune-logo.png";
import heartIcon from "../assets/heart.png";

const attemptDurations = [0.5, 1, 2, 4, 8, 16];

function MusicGamePage() {
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
            aria-label="6 de 6 tentativas restantes"
          >
            {attemptDurations.map((duration) => (
              <img
                key={duration}
                className="lives__heart"
                src={heartIcon}
                alt=""
                aria-hidden="true"
              />
            ))}
          </div>

          <p>6 de 6 tentativas restantes</p>
        </div>

        <div className="attempt-list">
          {attemptDurations.map((duration, index) => (
            <div className="attempt-slot" key={duration}>
              <span className="attempt-slot__number">
                {index + 1}
              </span>


              <span className="attempt-slot__duration">
                {duration.toString().replace(".", ",")}s
              </span>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

export default MusicGamePage;