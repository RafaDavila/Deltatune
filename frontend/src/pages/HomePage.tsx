import { Link } from "react-router";
import deltatuneLogo from "../assets/deltatune-logo.png";
import heartIcon from "../assets/heart.png";

function HomePage() {
  return (
    <main className="home">
      <header className="home__header">
        <h1 className="home__title">
          <img
            className="home__logo"
            src={deltatuneLogo}
            alt="Deltatune"
          />
        </h1>

        <p>Escolha o seu desafio</p>
      </header>

      <section className="game-list">
        <Link
          className="game-card game-card--available"
          to="/musica"
        >
          <img
            className="game-card__heart"
            src={heartIcon}
            alt=""
            aria-hidden="true"
          />

          <div>
            <h2>Adivinhe a música</h2>
            <p>Reconheça a música ouvindo pequenos trechos.</p>
          </div>

          <span className="game-card__status">Jogar</span>
        </Link>

        <button className="game-card" disabled>
          <img
            className="game-card__heart"
            src={heartIcon}
            alt=""
            aria-hidden="true"
          />

          <div>
            <h2>Adivinhe o personagem</h2>
            <p>Descubra o personagem utilizando pistas.</p>
          </div>

          <span className="game-card__status">Em breve</span>
        </button>
      </section>
    </main>
  );
}

export default HomePage;