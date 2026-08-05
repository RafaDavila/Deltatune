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
          <h2>Adivinhe a música</h2>
          <p>Escute o trecho e descubra qual música está tocando.</p>
        </div>

        <label className="chapter-filter">
          <span>Seleção de músicas</span>

          <select defaultValue="all">
            <option value="all">Todos os capítulos</option>
            <option value="1">Capítulo 1</option>
            <option value="2">Capítulo 2</option>
            <option value="3">Capítulo 3</option>
            <option value="4">Capítulo 4</option>
            <option value="5">Capítulo 5</option>
          </select>
        </label>

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

              <span className="attempt-slot__message">
                Tentativa disponível
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