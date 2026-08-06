import { useEffect, useState } from "react";
import heartIcon from "../assets/heart.png";

type TutorialModalProps = {
  onClose: (dontShowAgain: boolean) => void;
};

function TutorialModal({ onClose }: TutorialModalProps) {
  const [dontShowAgain, setDontShowAgain] = useState(false);

  function handleClose() {
    onClose(dontShowAgain);
  }

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onClose(dontShowAgain);
      }
    }

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [dontShowAgain, onClose]);

  return (
    <div
      className="tutorial-overlay"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) {
          handleClose();
        }
      }}
    >
      <section
        className="tutorial-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="tutorial-title"
      >
        <button
          className="tutorial-modal__close"
          type="button"
          aria-label="Fechar tutorial"
          onClick={handleClose}
        >
          ×
        </button>

        <img
          className="tutorial-modal__heart"
          src={heartIcon}
          alt=""
          aria-hidden="true"
        />

        <h2 id="tutorial-title">Como jogar</h2>

        <ol className="tutorial-steps">
          <li>
            Ouça o trecho inicial de
            <strong> 0,5 segundo</strong>.
          </li>

          <li>
            Digite o nome da música ou escolha uma das sugestões.
          </li>

          <li>
            Uma resposta errada ou um pulo consome um coração.
          </li>

          <li>
            Cada tentativa libera um trecho maior da música.
          </li>

          <li>
            Acerte antes que seus seis corações terminem.
          </li>
        </ol>

        <label className="tutorial-modal__preference">
          <input
            type="checkbox"
            checked={dontShowAgain}
            onChange={(event) =>
              setDontShowAgain(event.target.checked)
            }
          />

          <span>Não mostrar novamente</span>
        </label>

        <button
          className="tutorial-modal__start"
          type="button"
          onClick={handleClose}
          autoFocus
        >
          Começar
        </button>
      </section>
    </div>
  );
}

export default TutorialModal;