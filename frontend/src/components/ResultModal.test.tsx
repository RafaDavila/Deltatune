import {
  render,
  screen,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
  expect,
  test,
  vi,
} from "vitest";

import ResultModal from "./ResultModal";

test(
  "inicia a próxima rodada no modo infinito",
  async () => {
    const user = userEvent.setup();
    const handleClose = vi.fn();
    const handleContinue = vi.fn();

    render(
      <ResultModal
        hasWon
        songTitle="Burning Eyes"
        attemptsUsed={1}
        remainingLives={6}
        isPlaying={false}
        revealLabel="A música desta rodada era"
        continueLabel="Próxima música"
        onReplay={vi.fn()}
        onClose={handleClose}
        onContinue={handleContinue}
      />,
    );

    expect(
      screen.getByText(
        "A música desta rodada era",
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText("Burning Eyes"),
    ).toBeInTheDocument();

    await user.click(
      screen.getByRole("button", {
        name: "Próxima música",
      }),
    );

    expect(handleContinue).toHaveBeenCalledOnce();
    expect(handleClose).not.toHaveBeenCalled();
  },
);

test(
  "mantém o comportamento do desafio diário",
  async () => {
    const user = userEvent.setup();
    const handleClose = vi.fn();

    render(
      <ResultModal
        hasWon={false}
        songTitle="Field of Hopes and Dreams"
        attemptsUsed={6}
        remainingLives={0}
        isPlaying={false}
        onReplay={vi.fn()}
        onClose={handleClose}
      />,
    );

    expect(
      screen.getByText(
        "A música do dia era",
      ),
    ).toBeInTheDocument();

    await user.click(
      screen.getByRole("button", {
        name: "Continuar",
      }),
    );

    expect(handleClose).toHaveBeenCalledOnce();
  },
);