import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { expect, test, vi } from "vitest";
import userEvent from "@testing-library/user-event";
import { resetPassword } from "../services/deltatuneApi";
import ResetPasswordPage from "./ResetPasswordPage";

vi.mock("../services/deltatuneApi", () => ({
  resetPassword: vi.fn(),
}));

test("mostra aviso quando o link não possui token", () => {
  render(
    <MemoryRouter initialEntries={["/redefinir-senha"]}>
      <ResetPasswordPage />
    </MemoryRouter>,
  );

  expect(screen.getByRole("alert")).toHaveTextContent(
    "Link de recuperação incompleto.",
  );

  expect(
    screen.queryByLabelText("Nova senha"),
  ).not.toBeInTheDocument();
});

test("redefine a senha e bloqueia novo envio após sucesso", async () => {
  const user = userEvent.setup();

  vi.mocked(resetPassword).mockResolvedValue({
    message: "Senha redefinida com sucesso.",
  });

  render(
    <MemoryRouter
      initialEntries={["/redefinir-senha?token=token-simulado"]}
    >
      <ResetPasswordPage />
    </MemoryRouter>,
  );

  const passwordInput = screen.getByLabelText("Nova senha");

  await user.type(passwordInput, "NovaSenha123!");

  await user.click(
    screen.getByRole("button", {
      name: "Redefinir senha",
    }),
  );

  expect(resetPassword).toHaveBeenCalledWith({
    token: "token-simulado",
    newPassword: "NovaSenha123!",
  });

  expect(await screen.findByRole("status")).toHaveTextContent(
    "Senha redefinida com sucesso.",
  );

  expect(passwordInput).toHaveValue("");
  expect(passwordInput).toBeDisabled();

  expect(
    screen.getByRole("button", {
      name: "Redefinir senha",
    }),
  ).toBeDisabled();
});

test("mostra o erro da API e permite tentar novamente", async () => {
  const user = userEvent.setup();

  vi.mocked(resetPassword).mockRejectedValueOnce(
    new Error("O link de recuperação é inválido ou expirou."),
  );

  render(
    <MemoryRouter
      initialEntries={["/redefinir-senha?token=token-simulado"]}
    >
      <ResetPasswordPage />
    </MemoryRouter>,
  );

  const passwordInput = screen.getByLabelText("Nova senha");

  await user.type(passwordInput, "NovaSenha123!");

  await user.click(
    screen.getByRole("button", {
      name: "Redefinir senha",
    }),
  );

  expect(await screen.findByRole("alert")).toHaveTextContent(
    "O link de recuperação é inválido ou expirou.",
  );

  expect(screen.queryByRole("status")).not.toBeInTheDocument();

  expect(passwordInput).toBeEnabled();

  expect(
    screen.getByRole("button", {
      name: "Redefinir senha",
    }),
  ).toBeEnabled();
});