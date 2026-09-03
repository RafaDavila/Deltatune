import { Link } from "react-router";
import deltatuneLogo from "../assets/deltatune-logo.png";
import heartIcon from "../assets/heart.png";
import SiteFooter from "../components/SiteFooter";
import { useState } from "react";

import AuthModal from "../components/AuthModal";
import { useAuth } from "../hooks/useAuth";

function HomePage() {
  const [isAuthOpen, setIsAuthOpen] =
    useState(false);

  const {
    user,
    isAuthenticated,
    isLoading,
    logout,
  } = useAuth();
  return (
    <main className="home">
      <div className="home__account">
        {isLoading ? (
          <span className="home__account-status">
            Carregando conta...
          </span>
        ) : isAuthenticated && user !== null ? (
          <>
            <span className="home__account-name">
              {user.displayName}
            </span>

            <button
              className="home__account-button"
              type="button"
              onClick={logout}
            >
              Sair
            </button>
          </>
        ) : (
          <button
            className="home__account-button"
            type="button"
            onClick={() => {
              setIsAuthOpen(true);
            }}
          >
            Entrar
          </button>
        )}
      </div>
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

        <Link
          className="game-card game-card--available"
          to="/infinito"
        >
          <img
            className="game-card__heart"
            src={heartIcon}
            alt=""
            aria-hidden="true"
          />

          <div>
            <h2>MODO INFINITO</h2>
            <p>
              Adivinhe quantas músicas conseguir
              sem esperar o próximo desafio.
            </p>
          </div>

          <span className="game-card__status">
            Jogar
          </span>
        </Link>
      </section>
      <SiteFooter />
      {isAuthOpen && (
        <AuthModal
          onClose={() => {
            setIsAuthOpen(false);
          }}
        />
      )}
    </main>
  );
}

export default HomePage;