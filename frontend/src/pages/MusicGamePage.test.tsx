import {
  render,
  fireEvent,
  screen,
  waitFor,
} from "@testing-library/react";
import { MemoryRouter } from "react-router";
import {
  beforeEach,
  expect,
  test,
  vi,
} from "vitest";

import MusicGamePage from "./MusicGamePage";
import {
  skipDailyGuess,
  submitDailyGuess,
  type SessionAttempt,
  ApiError,
  getSongs,
  resumeDailyChallenge,
  startDailyChallenge,
  type ResumeDailyChallengeResponse,
} from "../services/deltatuneApi";

import type { ComponentProps } from "react";

vi.mock("../services/deltatuneApi", async (importOriginal) => {
  const actual = await importOriginal<
    typeof import("../services/deltatuneApi")
  >();

  return {
    ApiError: actual.ApiError,
    getSongs: vi.fn(),
    startDailyChallenge: vi.fn(),
    resumeDailyChallenge: vi.fn(),
    submitDailyGuess: vi.fn(),
    skipDailyGuess: vi.fn(),
    getDailyAudioUrl: vi.fn(() => "/daily-audio.mp3"),
    getDailyStreakStats: vi.fn().mockResolvedValue({
      currentStreak: 1,
      bestStreak: 2,
    }),
  };
});

vi.mock("../hooks/useAuth", () => ({
  useAuth: () => ({
    user: { id: "user-123" },
    isAuthenticated: true,
    isLoading: false,
  }),
}));

vi.mock("../hooks/useAudioClip", () => ({
  default: () => ({
    audioRef: { current: null },
    volume: 0.6,
    setVolume: vi.fn(),
    isPlaying: false,
    playAudio: vi.fn(),
    stopAudio: vi.fn(),
  }),
}));

// Permite verificar se a página libera ou bloqueia jogadas.
vi.mock("../components/GuessForm", () => ({
  default: ({
    disabled,
    guess,
    onGuessChange,
    onSubmit,
    onSkip,
  }: ComponentProps<
    typeof import("../components/GuessForm").default
  >) => (
    <form onSubmit={onSubmit}>
      <input
        aria-label="Palpite"
        value={guess}
        disabled={disabled}
        onChange={(event) =>
          onGuessChange(event.target.value)
        }
      />

      <button type="submit" disabled={disabled}>
        Enviar palpite
      </button>

      <button
        type="button"
        disabled={disabled}
        onClick={onSkip}
      >
        Pular
      </button>
    </form>
  ),
}));

// Permite verificar o resultado recuperado pela página.
vi.mock("../components/ResultModal", () => ({
  default: ({
    hasWon,
    songTitle,
  }: {
    hasWon: boolean;
    songTitle: string;
  }) => (
    <div data-testid="recovered-result">
      {hasWon ? "Vitória" : "Derrota"}: {songTitle}
    </div>
  ),
}));

const storageKey = "deltatune-daily-session-user-123";

const baseGame = {
  challengeId: "2026-09-30",
  challengeNumber: 38,
  sessionId: "daily-session-123",
  attemptDurations: [0.5, 1, 2, 4, 8, 16],
  nextResetAt: new Date(
    Date.now() + 24 * 60 * 60 * 1000,
  ).toISOString(),
  maximumAttempts: 6,
};

type RecoveryScenario = {
  name: string;
  attempts: ResumeDailyChallengeResponse["attempts"];
  remainingLives: number;
  won: boolean;
  gameFinished: boolean;
  songTitle: string | null;
};

const scenarios: RecoveryScenario[] = [
  {
    name: "nova",
    attempts: [],
    remainingLives: 6,
    won: false,
    gameFinished: false,
    songTitle: null,
  },
  {
    name: "em andamento",
    attempts: [
      { answer: "Pulou", status: "skipped" },
      { answer: "Resposta errada", status: "wrong" },
    ],
    remainingLives: 4,
    won: false,
    gameFinished: false,
    songTitle: null,
  },
  {
    name: "vencida",
    attempts: [
      { answer: "Pulou", status: "skipped" },
      { answer: "Dark Sanctuary", status: "correct" },
    ],
    remainingLives: 5,
    won: true,
    gameFinished: true,
    songTitle: "Dark Sanctuary",
  },
  {
    name: "perdida",
    attempts: Array.from({ length: 6 }, () => ({
      answer: "Pulou",
      status: "skipped" as const,
    })),
    remainingLives: 0,
    won: false,
    gameFinished: true,
    songTitle: "Dark Sanctuary",
  },
];

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  localStorage.setItem("deltatune-hide-tutorial", "true");

  vi.mocked(getSongs).mockResolvedValue([]);

  vi.mocked(startDailyChallenge).mockResolvedValue({
    ...baseGame,
    remainingLives: 6,
    guestToken: null,
  });
});

test.each(scenarios)(
  "recupera partida $name sem identificador local",
  async (scenario) => {
    const recoveredGame: ResumeDailyChallengeResponse = {
      ...baseGame,
      attempts: scenario.attempts,
      remainingLives: scenario.remainingLives,
      won: scenario.won,
      gameFinished: scenario.gameFinished,
      songTitle: scenario.songTitle,
    };

    vi.mocked(resumeDailyChallenge).mockResolvedValue(
      recoveredGame,
    );

    expect(localStorage.getItem(storageKey)).toBeNull();

    render(
      <MemoryRouter>
        <MusicGamePage />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(
        localStorage.getItem(
          `deltatune-game-${baseGame.challengeId}`,
        ),
      ).toBe(JSON.stringify(scenario.attempts));
    });

    expect(startDailyChallenge).toHaveBeenCalledTimes(1);
    expect(resumeDailyChallenge).toHaveBeenCalledTimes(1);
    expect(resumeDailyChallenge).toHaveBeenCalledWith(
      baseGame.sessionId,
    );

    expect(localStorage.getItem(storageKey)).toBe(
      baseGame.sessionId,
    );

    expect(
      screen.getByText(
        `${scenario.remainingLives} de 6 tentativas restantes`,
      ),
    ).toBeInTheDocument();

    const submitButton = screen.getByRole("button", {
      name: "Enviar palpite",
    });

    if (scenario.gameFinished) {
      expect(submitButton).toBeDisabled();

      const result = await screen.findByTestId(
        "recovered-result",
      );

      expect(result).toHaveTextContent(
        `${scenario.won ? "Vitória" : "Derrota"}: ${scenario.songTitle
        }`,
      );
    } else {
      expect(submitButton).toBeEnabled();
      expect(
        screen.queryByTestId("recovered-result"),
      ).not.toBeInTheDocument();
    }
  },
);


const recoveryFailures = [
  {
    name: "falha de rede",
    error: () => new TypeError("Failed to fetch"),
  },
  {
    name: "erro 500",
    error: () => new ApiError("Erro interno.", 500),
  },
  {
    name: "erro 503",
    error: () => new ApiError("Serviço indisponível.", 503),
  },
  {
    name: "erro 401",
    error: () => new ApiError("Autenticação inválida.", 401),
  },
  {
    name: "erro 403",
    error: () => new ApiError("Acesso negado.", 403),
  },
  {
    name: "outro conflito 409",
    error: () => new ApiError("Outro conflito.", 409),
  },
];

test.each(recoveryFailures)(
  "preserva a sessão diária após $name e permite recuperar",
  async ({ error }) => {
    const recoveredGame: ResumeDailyChallengeResponse = {
      ...baseGame,
      attempts: [
        { answer: "Pulou", status: "skipped" },
      ],
      remainingLives: 5,
      won: false,
      gameFinished: false,
      songTitle: null,
    };

    localStorage.setItem(storageKey, baseGame.sessionId);

    vi.mocked(resumeDailyChallenge)
      .mockRejectedValueOnce(error())
      .mockResolvedValueOnce(recoveredGame);

    render(
      <MemoryRouter>
        <MusicGamePage />
      </MemoryRouter>,
    );

    const retryButton = await screen.findByRole("button", {
      name: "Tentar novamente",
    });

    expect(localStorage.getItem(storageKey)).toBe(
      baseGame.sessionId,
    );
    expect(startDailyChallenge).not.toHaveBeenCalled();

    fireEvent.click(retryButton);

    await screen.findByText("5 de 6 tentativas restantes");

    expect(resumeDailyChallenge).toHaveBeenCalledTimes(2);
    expect(resumeDailyChallenge).toHaveBeenNthCalledWith(
      1,
      baseGame.sessionId,
    );
    expect(resumeDailyChallenge).toHaveBeenNthCalledWith(
      2,
      baseGame.sessionId,
    );
    expect(startDailyChallenge).not.toHaveBeenCalled();
    expect(localStorage.getItem(storageKey)).toBe(
      baseGame.sessionId,
    );
    expect(
      screen.queryByRole("button", {
        name: "Tentar novamente",
      }),
    ).not.toBeInTheDocument();
  },
);

test.each([
  {
    name: "sessão inexistente",
    status: 404,
    message: "Sessão de partida não encontrada.",
  },
  {
    name: "desafio anterior",
    status: 409,
    message: "A sessão pertence a outro desafio.",
  },
])(
  "inicia uma sessão diária para $name",
  async ({ status, message }) => {
    localStorage.setItem(storageKey, "old-session");

    vi.mocked(resumeDailyChallenge)
      .mockRejectedValueOnce(new ApiError(message, status))
      .mockResolvedValueOnce({
        ...baseGame,
        attempts: [],
        remainingLives: 6,
        won: false,
        gameFinished: false,
        songTitle: null,
      });

    render(
      <MemoryRouter>
        <MusicGamePage />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: "Enviar palpite",
        }),
      ).toBeEnabled();
    });

    expect(startDailyChallenge).toHaveBeenCalledTimes(1);
    expect(resumeDailyChallenge).toHaveBeenNthCalledWith(
      1,
      "old-session",
    );
    expect(resumeDailyChallenge).toHaveBeenNthCalledWith(
      2,
      baseGame.sessionId,
    );
    expect(localStorage.getItem(storageKey)).toBe(
      baseGame.sessionId,
    );
  },
);

test(
  "preserva a sessão recém-criada se a recuperação falhar",
  async () => {
    vi.mocked(resumeDailyChallenge)
      .mockRejectedValueOnce(
        new ApiError("Serviço indisponível.", 503),
      )
      .mockResolvedValueOnce({
        ...baseGame,
        attempts: [],
        remainingLives: 6,
        won: false,
        gameFinished: false,
        songTitle: null,
      });

    render(
      <MemoryRouter>
        <MusicGamePage />
      </MemoryRouter>,
    );

    const retryButton = await screen.findByRole("button", {
      name: "Tentar novamente",
    });

    expect(startDailyChallenge).toHaveBeenCalledTimes(1);
    expect(localStorage.getItem(storageKey)).toBe(
      baseGame.sessionId,
    );

    fireEvent.click(retryButton);

    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: "Enviar palpite",
        }),
      ).toBeEnabled();
    });

    expect(startDailyChallenge).toHaveBeenCalledTimes(1);
    expect(resumeDailyChallenge).toHaveBeenCalledTimes(2);
    expect(localStorage.getItem(storageKey)).toBe(
      baseGame.sessionId,
    );
  },
);

test.each(["palpite", "pular"] as const)(
  "sincroniza todo o histórico do servidor após %s",
  async (action) => {
    localStorage.setItem(storageKey, baseGame.sessionId);

    vi.mocked(resumeDailyChallenge).mockResolvedValueOnce({
      ...baseGame,
      attempts: [
        { answer: "Primeiro erro", status: "wrong" },
      ],
      remainingLives: 5,
      won: false,
      gameFinished: false,
      songTitle: null,
    });

    const attempts: SessionAttempt[] = [
      { answer: "Primeiro erro", status: "wrong" },
      { answer: "Erro de outra aba", status: "wrong" },
      action === "palpite"
        ? { answer: "Novo palpite", status: "wrong" }
        : { answer: "Pulou", status: "skipped" },
    ];

    const result = {
      challengeId: baseGame.challengeId,
      attempts,
      attemptsUsed: 3,
      remainingLives: 3,
      won: false,
      gameFinished: false,
      songTitle: null,
    };

    if (action === "palpite") {
      vi.mocked(submitDailyGuess).mockResolvedValueOnce({
        ...result,
        correct: false,
      });
    } else {
      vi.mocked(skipDailyGuess).mockResolvedValueOnce({
        ...result,
        skipped: true,
      });
    }

    render(
      <MemoryRouter>
        <MusicGamePage />
      </MemoryRouter>,
    );

    await screen.findByText("5 de 6 tentativas restantes");

    if (action === "palpite") {
      fireEvent.change(
        screen.getByRole("textbox", { name: "Palpite" }),
        { target: { value: "Novo palpite" } },
      );

      fireEvent.click(
        screen.getByRole("button", {
          name: "Enviar palpite",
        }),
      );
    } else {
      fireEvent.click(
        screen.getByRole("button", { name: "Pular" }),
      );
    }

    await screen.findByText("Erro de outra aba");

    expect(
      screen.getByText("3 de 6 tentativas restantes"),
    ).toBeInTheDocument();

    expect(
      screen.getAllByText("Primeiro erro"),
    ).toHaveLength(1);

    if (action === "palpite") {
      expect(submitDailyGuess).toHaveBeenCalledWith(
        baseGame.sessionId,
        baseGame.challengeId,
        "Novo palpite",
      );
    } else {
      expect(skipDailyGuess).toHaveBeenCalledWith(
        baseGame.sessionId,
        baseGame.challengeId,
      );
    }
  },
);