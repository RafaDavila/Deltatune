import { useState } from "react";
import {
  FaGithub,
  FaInfoCircle,
} from "react-icons/fa";import InfoModal from "./InfoModal";

function SiteFooter() {
  const [isInfoOpen, setIsInfoOpen] = useState(false);

  return (
    <>
      <footer
        className="site-footer"
        aria-label="Links do projeto"
      >
        <button
          className="site-footer__action"
          type="button"
          aria-label="Informações sobre o projeto"
          title="Sobre o projeto"
          onClick={() => setIsInfoOpen(true)}
        >
          <FaInfoCircle aria-hidden="true" />
        </button>

        <a
          className="site-footer__action"
          href="https://github.com/RafaDavila/Deltatune"
          target="_blank"
          rel="noreferrer"
          aria-label="Abrir repositório no GitHub"
          title="GitHub"
        >
          <FaGithub aria-hidden="true" />
        </a>
      </footer>

      {isInfoOpen && (
        <InfoModal
          onClose={() => setIsInfoOpen(false)}
        />
      )}
    </>
  );
}

export default SiteFooter;