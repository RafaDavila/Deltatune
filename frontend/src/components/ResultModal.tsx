import { useEffect } from "react";
import heartIcon from "../assets/heart.png";

type ResultModalProps = {
  hasWon: boolean;
  songTitle: string;
  attemptsUsed: number;
  remainingLives: number;
  isPlaying: boolean;
  revealLabel?: string;
  continueLabel?: string;
  onReplay: () => void;
  onClose: () => void;
  onContinue?: () => void | Promise<void>;
  currentStreak?: number;
  bestStreak?: number;
};

const maximumLives = 6;

function ResultModal({
  hasWon,
  songTitle,
  attemptsUsed,
  remainingLives,
  isPlaying,
  revealLabel = "A música do dia era",
  continueLabel = "Continuar",
  onReplay,
  onClose,
  onContinue,
  currentStreak,
  bestStreak,
}: ResultModalProps) {
  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [onClose]);

  return (
    <div
      className="tutorial-overlay"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) {
          onClose();
        }
      }}
    >
      <section
        className={`tutorial-modal result-modal ${hasWon
          ? "result-modal--win"
          : "result-modal--loss"
          }`}
        role="dialog"
        aria-modal="true"
        aria-labelledby="result-title"
      >
        <button
          className="tutorial-modal__close"
          type="button"
          aria-label="Fechar resultado"
          onClick={onClose}
        >
          ×
        </button>

        <p className="result-modal__status">
          {hasWon ? "Vitória" : "Fim de jogo"}
        </p>

        <h2 id="result-title">
          {hasWon
            ? "Você acertou!"
            : "Seus corações acabaram"}
        </h2>

        <p className="result-modal__reveal">
          {revealLabel}
        </p>

        <strong className="result-modal__song">
          {songTitle}
        </strong>

        <div
          className="result-modal__hearts"
          aria-label={`${remainingLives} de 6 corações restantes`}
        >
          {Array.from(
            { length: maximumLives },
            (_, index) => (
              <img
                key={index}
                className={
                  index >= remainingLives
                    ? "result-modal__heart result-modal__heart--lost"
                    : "result-modal__heart"
                }
                src={heartIcon}
                alt=""
                aria-hidden="true"
              />
            ),
          )}
        </div>

        <dl className="result-modal__stats">
          <div>
            <dt>Tentativas utilizadas</dt>
            <dd>{attemptsUsed} de 6</dd>
          </div>

          <div>
            <dt>Corações restantes</dt>
            <dd>{remainingLives} de 6</dd>
          </div>
        </dl>
        {(
          hasWon &&
          currentStreak !== undefined &&
          bestStreak !== undefined
        ) && (
            <dl
              className="result-modal__streaks"
              aria-label="Sequências do desafio diário"
            >
              <div>
                <dt>Sequência atual</dt>
                <dd>{currentStreak}</dd>
              </div>

              <div>
                <dt>Melhor sequência</dt>
                <dd>{bestStreak}</dd>
              </div>
            </dl>
          )}

        <button
          className="result-modal__replay"
          type="button"
          onClick={onReplay}
        >
          {isPlaying
            ? "Tocando..."
            : "Ouvir trecho final"}
        </button>

        <button
          className="result-modal__continue"
          type="button"
          onClick={onContinue ?? onClose}
        >
          {continueLabel}
        </button>
      </section>
    </div>
  );
}

export default ResultModal;