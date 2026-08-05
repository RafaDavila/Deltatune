import { Link } from "react-router";
import deltatuneLogo from "../assets/deltatune-logo.png";

function MusicGamePage() {
  return (
    <main className="music-game">
      <Link className="back-link" to="/">
        ← Voltar
      </Link>

      <header className="music-game__header">
        <img
          className="music-game__logo"
          src={deltatuneLogo}
          alt="Deltatune"
        />

        <h2>Adivinhe a música</h2>
        <p>Escute o trecho e descubra qual música está tocando.</p>
      </header>
    </main>
  );
}

export default MusicGamePage;