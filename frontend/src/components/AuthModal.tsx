import {
  useEffect,
  useState,
} from "react";

import type {
  FormEvent,
} from "react";

import { useAuth } from "../hooks/useAuth";


type AuthModalProps = {
  onClose: () => void;
};

type AuthMode = "login" | "register";

function AuthModal({
  onClose,
}: AuthModalProps) {
  const {
    login,
    register,
  } = useAuth();

  const [mode, setMode] =
    useState<AuthMode>("login");

  const [displayName, setDisplayName] =
    useState("");

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [errorMessage, setErrorMessage] =
    useState<string | null>(null);

  const [isSubmitting, setIsSubmitting] =
    useState(false);

  useEffect(() => {
    function handleKeyDown(
      event: KeyboardEvent,
    ) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    window.addEventListener(
      "keydown",
      handleKeyDown,
    );

    return () => {
      window.removeEventListener(
        "keydown",
        handleKeyDown,
      );
    };
  }, [onClose]);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setErrorMessage(null);
    setIsSubmitting(true);

    try {
      if (mode === "register") {
        await register({
          displayName,
          email,
          password,
        });
      } else {
        await login({
          email,
          password,
        });
      }

      onClose();
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Não foi possível autenticar.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  function changeMode(
    nextMode: AuthMode,
  ) {
    setMode(nextMode);
    setErrorMessage(null);
  }

  return (
    <div
      className="tutorial-overlay"
      onMouseDown={(event) => {
        if (
          event.target === event.currentTarget
        ) {
          onClose();
        }
      }}
    >
      <section
        className="tutorial-modal auth-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="auth-title"
      >
        <button
          className="tutorial-modal__close"
          type="button"
          aria-label="Fechar autenticação"
          onClick={onClose}
        >
          ×
        </button>

        <h2 id="auth-title">
          {mode === "login"
            ? "Entrar"
            : "Criar conta"}
        </h2>

        <div className="auth-modal__tabs">
          <button
            type="button"
            className={
              mode === "login"
                ? "auth-modal__tab auth-modal__tab--active"
                : "auth-modal__tab"
            }
            onClick={() => changeMode("login")}
          >
            Entrar
          </button>

          <button
            type="button"
            className={
              mode === "register"
                ? "auth-modal__tab auth-modal__tab--active"
                : "auth-modal__tab"
            }
            onClick={() => changeMode("register")}
          >
            Criar conta
          </button>
        </div>

        <form
          className="auth-form"
          onSubmit={handleSubmit}
        >
          {mode === "register" && (
            <label className="auth-form__field">
              <span>Usuário</span>

              <input
                type="text"
                value={displayName}
                minLength={2}
                maxLength={60}
                autoComplete="name"
                required
                onChange={(event) => {
                  setDisplayName(
                    event.target.value,
                  );
                }}
              />
            </label>
          )}

          <label className="auth-form__field">
            <span>E-mail</span>

            <input
              type="email"
              value={email}
              autoComplete="email"
              required
              onChange={(event) => {
                setEmail(event.target.value);
              }}
            />
          </label>

          <label className="auth-form__field">
            <span>Senha</span>

            <input
              type="password"
              value={password}
              minLength={8}
              maxLength={128}
              autoComplete={
                mode === "register"
                  ? "new-password"
                  : "current-password"
              }
              required
              onChange={(event) => {
                setPassword(
                  event.target.value,
                );
              }}
            />
          </label>

          {errorMessage !== null && (
            <p
              className="auth-form__error"
              role="alert"
            >
              {errorMessage}
            </p>
          )}

          <button
            className="auth-form__submit"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting
              ? "Aguarde..."
              : mode === "login"
                ? "Entrar"
                : "Criar conta"}
          </button>
        </form>
      </section>
    </div>
  );
}

export default AuthModal;