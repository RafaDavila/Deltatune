import { Link, useSearchParams } from "react-router";
import { useState } from "react";
import type { FormEvent } from "react";
import { resetPassword } from "../services/deltatuneApi";


function ResetPasswordPage() {
    const [searchParams] = useSearchParams();
    const token = searchParams.get("token");
    const [newPassword, setNewPassword] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);

    const [errorMessage, setErrorMessage] =
        useState<string | null>(null);

    const [successMessage, setSuccessMessage] =
        useState<string | null>(null);
    async function handleSubmit(
        event: FormEvent<HTMLFormElement>,
    ) {
        event.preventDefault();

        if (!token || isSubmitting || successMessage !== null) {
            return;
        }

        setIsSubmitting(true);
        setErrorMessage(null);

        try {
            const result = await resetPassword({
                token,
                newPassword,
            });

            setSuccessMessage(result.message);
            setNewPassword("");
        } catch (error) {
            setErrorMessage(
                error instanceof Error
                    ? error.message
                    : "Não foi possível redefinir a senha.",
            );
        } finally {
            setIsSubmitting(false);
        }

    }
    return (
        <main className="music-game reset-password">
            <section className="reset-password__panel">
                <h1>Redefinir senha</h1>

                {token ? (
                    <form
                        className="auth-form"
                        onSubmit={handleSubmit}
                    >
                        <p>Escolha uma nova senha para sua conta.</p>

                        <label className="auth-form__field">
                            <span>Nova senha</span>

                            <input
                                type="password"
                                value={newPassword}
                                onChange={(event) => {
                                    setNewPassword(event.target.value);
                                }}
                                autoComplete="new-password"
                                minLength={8}
                                maxLength={128}
                                required
                                disabled={
                                    isSubmitting || successMessage !== null
                                }
                            />
                        </label>

                        {errorMessage !== null && (
                            <p className="auth-form__error" role="alert">
                                {errorMessage}
                            </p>
                        )}

                        {successMessage !== null && (
                            <p className="auth-form__success" role="status">
                                {successMessage}
                            </p>
                        )}

                        <button
                            className="auth-form__submit"
                            type="submit"
                            disabled={
                                isSubmitting || successMessage !== null
                            }
                        >
                            {isSubmitting ? "Aguarde..." : "Redefinir senha"}
                        </button>
                    </form>
                ) : (
                    <p role="alert">
                        Link de recuperação incompleto. Solicite um novo e-mail.
                    </p>
                )}
                <Link className="back-link reset-password__back" to="/">
                    Voltar para o login
                </Link>
            </section>
        </main>
    );
}

export default ResetPasswordPage;
