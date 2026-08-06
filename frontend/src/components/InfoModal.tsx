import { useEffect } from "react";

type InfoModalProps = {
  onClose: () => void;
};

function InfoModal({ onClose }: InfoModalProps) {
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
        className="tutorial-modal info-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="info-title"
      >
        <button
          className="tutorial-modal__close"
          type="button"
          aria-label="Fechar informações"
          onClick={onClose}
        >
          ×
        </button>

        <h2 id="info-title">Sobre o Deltatune</h2>

        <div className="info-modal__content">
          <section>
            <h3>O projeto</h3>

            <p>
              Deltatune é um jogo diário de adivinhação
              musical inspirado no universo de Deltarune.
              Ouça trechos progressivos e tente descobrir
              a música antes que seus corações acabem.
            </p>

            <p>
              Desenvolvido por Rafael Davila como projeto
              de estudo e portfólio.
            </p>
          </section>

          <section>
            <h3>Aviso</h3>

            <p>
              Este é um projeto de fã gratuito, independente
              e não oficial. Não possui associação, patrocínio
              ou endosso de Toby Fox ou dos responsáveis por
              Deltarune.
            </p>
          </section>

          <section>
            <h3>Créditos</h3>

            <ul>
              <li>Deltarune e músicas: Toby Fox</li>
              <li>
                Administração musical: Materia Music
                Publishing
              </li>
              <li>Desenvolvimento: Rafael Davila</li>
              <li>Inspiração de mecânica: Songless</li>
            </ul>
          </section>

          <section>
            <h3>Privacidade</h3>

            <p>
              Atualmente, o projeto não utiliza contas,
              cookies ou coleta de dados pessoais. O
              localStorage do navegador é usado apenas para
              guardar preferências locais, como a exibição
              do tutorial.
            </p>
          </section>
        </div>
      </section>
    </div>
  );
}

export default InfoModal;