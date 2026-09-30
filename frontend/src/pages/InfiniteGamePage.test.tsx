import {
  act,
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

import InfiniteGamePage from "./InfiniteGamePage";
import {
  getSongs,
  getInfiniteRecord,
  resumeInfiniteGame,
  startInfiniteGame,
  type ResumeInfiniteGameResponse,
} from "../services/deltatuneApi";

const authState = vi.hoisted(() => ({
  user: null as { id: string } | null,
  isLoading: false,
}));

vi.mock("../services/deltatuneApi", () => ({

  getInfiniteRecord: vi.fn(),
  getSongs: vi.fn(),
  resumeInfiniteGame: vi.fn(),
  startInfiniteGame: vi.fn(),
  startNextInfiniteRound: vi.fn(),
  submitInfiniteGuess: vi.fn(),
  skipInfiniteGuess: vi.fn(),
  getInfiniteAudioUrl: vi.fn(
    () => "/infinite-audio.mp3",
  ),
}));

vi.mock("../hooks/useAuth", () => ({
  useAuth: () => authState,
}));

vi.mock("../hooks/useInfiniteAudio", () => ({
  default: () => ({
    audioUrl: "/infinite-audio.mp3",
    audioError: null,
  }),
}));

vi.mock("../hooks/useAudioClip", () => ({
  default: () => ({
    audioRef: {
      current: null,
    },
    volume: 0.6,
    setVolume: vi.fn(),
    isPlaying: false,
    playAudio: vi.fn(),
    stopAudio: vi.fn(),
  }),
}));

const resumedGame: ResumeInfiniteGameResponse = {
  runId: "run-123",
  roundId: "round-456",
  roundNumber: 3,
  attemptDurations: [
    0.5,
    1,
    2,
    4,
    8,
    16,
  ],
  remainingLives: 4,
  maximumAttempts: 6,
  currentStreak: 2,
  attempts: [
    {
      answer: "Pulou",
      status: "skipped",
    },
    {
      answer: "Resposta errada",
      status: "wrong",
    },
  ],
  won: false,
  gameFinished: false,
  songTitle: null,
};

function renderPage() {
  return render(
    <MemoryRouter>
      <InfiniteGamePage />
    </MemoryRouter>,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  authState.user = null;
  authState.isLoading = false;

  vi.mocked(getInfiniteRecord).mockReset();
  vi.mocked(getInfiniteRecord).mockResolvedValue({
    bestStreak: 0,
  });
  localStorage.clear();


  vi.mocked(getSongs).mockResolvedValue([]);

  vi.mocked(startInfiniteGame).mockResolvedValue({
    runId: "new-run",
    roundId: "new-round",
    roundNumber: 1,
    attemptDurations: [
      0.5,
      1,
      2,
      4,
      8,
      16,
    ],
    remainingLives: 6,
    maximumAttempts: 6,
    currentStreak: 0,
  });
});

test(
  "recupera a rodada infinita salva",
  async () => {
    localStorage.setItem(
      "deltatune-infinite-run-anonymous",
      resumedGame.runId,
    );

    vi.mocked(
      resumeInfiniteGame,
    ).mockResolvedValue(resumedGame);

    renderPage();

    expect(
      await screen.findByText("003"),
    ).toBeInTheDocument();

    expect(
      resumeInfiniteGame,
    ).toHaveBeenCalledWith("run-123");

    expect(
      startInfiniteGame,
    ).not.toHaveBeenCalled();

    expect(
      screen.getByText("Pulou"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("Resposta errada"),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "4 de 6 tentativas restantes",
      ),
    ).toBeInTheDocument();
  },
);

test(
  "registra e preserva o maior recorde",
  async () => {
    localStorage.setItem(
     "deltatune-infinite-run-anonymous",
      resumedGame.runId,
    );

    localStorage.setItem(
      "deltatune-infinite-record-anonymous",
      "1",
    );
    vi.mocked(
      resumeInfiniteGame,
    ).mockResolvedValue(resumedGame);
    renderPage();

    await screen.findByText("003");

    await waitFor(() => {
      expect(
        localStorage.getItem(
          "deltatune-infinite-record-anonymous",
        ),
      ).toBe("2");
    });

    expect(
      screen.getByText(/Sequência atual:/),
    ).toHaveTextContent(
      "Sequência atual: 2 . Recorde: 2",
    );
  },
);

test(
  "recupera o recorde da conta sem armazenamento local",
  async () => {
    authState.user = { id: "user-a" };

    vi.mocked(getInfiniteRecord).mockResolvedValue({
      bestStreak: 12,
    });

    renderPage();

    await waitFor(() => {
      expect(
        screen.getByText(/Sequência atual:/),
      ).toHaveTextContent(
        "Sequência atual: 0 . Recorde: 12",
      );
    });

    expect(getInfiniteRecord).toHaveBeenCalledTimes(1);

    expect(
      localStorage.getItem(
        "deltatune-infinite-record-user-a",
      ),
    ).toBe("12");

    expect(
      localStorage.getItem(
        "deltatune-infinite-record-anonymous",
      ),
    ).toBeNull();
  },
);

test(
  "recupera o recorde mesmo com a partida perdida",
  async () => {
    authState.user = { id: "user-a" };

    localStorage.setItem(
      "deltatune-infinite-run-user-a",
      resumedGame.runId,
    );

    vi.mocked(getInfiniteRecord).mockResolvedValue({
      bestStreak: 12,
    });

    vi.mocked(resumeInfiniteGame).mockResolvedValue({
      ...resumedGame,
      currentStreak: 0,
      remainingLives: 0,
      attempts: Array.from({ length: 6 }, () => ({
        answer: "Pulou",
        status: "skipped" as const,
      })),
      won: false,
      gameFinished: true,
      songTitle: "Dark Sanctuary",
    });

    renderPage();

    await screen.findByText("003");

    await waitFor(() => {
      expect(
        screen.getByText(/Sequência atual:/),
      ).toHaveTextContent(
        "Sequência atual: 0 . Recorde: 12",
      );
    });

    expect(
      screen.getByText("0 de 6 tentativas restantes"),
    ).toBeInTheDocument();

    expect(startInfiniteGame).not.toHaveBeenCalled();
  },
);

test(
  "separa contas e ignora resposta atrasada da conta anterior",
  async () => {
    authState.user = { id: "user-a" };

    localStorage.setItem(
      "deltatune-infinite-record-user-a",
      "12",
    );
    localStorage.setItem(
      "deltatune-infinite-record-user-b",
      "3",
    );
    localStorage.setItem(
      "deltatune-infinite-record-anonymous",
      "50",
    );

    let resolveFirstRecord!: (
      record: { bestStreak: number },
    ) => void;

    const firstRecord = new Promise<{
      bestStreak: number;
    }>((resolve) => {
      resolveFirstRecord = resolve;
    });

    vi.mocked(getInfiniteRecord)
      .mockReturnValueOnce(firstRecord)
      .mockResolvedValueOnce({ bestStreak: 4 });

    const view = renderPage();

    await waitFor(() => {
      expect(getInfiniteRecord).toHaveBeenCalledTimes(1);
    });

    expect(
      screen.getByText(/Sequência atual:/),
    ).toHaveTextContent("Recorde: 12");

    authState.user = { id: "user-b" };

    view.rerender(
      <MemoryRouter>
        <InfiniteGamePage />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(
        screen.getByText(/Sequência atual:/),
      ).toHaveTextContent("Recorde: 4");
    });

    await act(async () => {
      resolveFirstRecord({ bestStreak: 99 });
      await firstRecord;
    });

    expect(
      screen.getByText(/Sequência atual:/),
    ).toHaveTextContent("Recorde: 4");

    expect(
      localStorage.getItem(
        "deltatune-infinite-record-user-a",
      ),
    ).toBe("12");

    expect(
      localStorage.getItem(
        "deltatune-infinite-record-user-b",
      ),
    ).toBe("4");

    expect(
      localStorage.getItem(
        "deltatune-infinite-record-anonymous",
      ),
    ).toBe("50");

    expect(getInfiniteRecord).toHaveBeenCalledTimes(2);
  },
);