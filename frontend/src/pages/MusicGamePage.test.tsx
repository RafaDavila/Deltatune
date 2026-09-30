import {
  render,
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
  getSongs,
  resumeDailyChallenge,
  startDailyChallenge,
  type ResumeDailyChallengeResponse,
} from "../services/deltatuneApi";

vi.mock("../services/deltatuneApi", () => ({
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
}));

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
  default: ({ disabled }: { disabled: boolean }) => (
    <button disabled={disabled}>Enviar palpite</button>
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
        `${scenario.won ? "Vitória" : "Derrota"}: ${
          scenario.songTitle
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