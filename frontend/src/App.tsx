import "./App.css";

function App() {
  return (
    <main className="home">
      <header className="home__header">
        <h1>DELTATUNE</h1>
        <p>Escolha o seu desafio</p>
      </header>

      <section className="game-list">
        <button className="game-card game-card--available">
          <span className="game-card__heart">♥</span>

          <div>
            <h2>Adivinhe a música</h2>
            <p>Reconheça a música ouvindo pequenos trechos.</p>
          </div>

          <span className="game-card__status">Jogar</span>
        </button>

        <button className="game-card" disabled>
          <span className="game-card__heart">♡</span>

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

export default App;