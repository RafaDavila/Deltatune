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

import InfiniteGamePage from "./InfiniteGamePage";
import {
  getSongs,
  resumeInfiniteGame,
  startInfiniteGame,
  type ResumeInfiniteGameResponse,
} from "../services/deltatuneApi";

vi.mock("../services/deltatuneApi", () => ({
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
      "deltatune-infinite-run",
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
    async() => {
        localStorage.setItem(
            "deltatune-infinite-run",
            resumedGame.runId,
        );

        localStorage.setItem(
            "deltatune-infinite-record",
            "1",
        );
        vi.mocked(
            resumeInfiniteGame,
        ).mockResolvedValue(resumedGame);
        renderPage();
        
        await screen.findByText("003");

        await waitFor(() =>{
            expect(
                localStorage.getItem(
                    "deltatune-infinite-record",
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