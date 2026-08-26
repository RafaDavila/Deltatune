export type DailyChallengeResponse = {
  challengeId: string;
  challengeNumber: number;
  attemptDurations: number[];
  nextResetAt: string;
};

export type GuessResponse = {
  challengeId: string;
  correct: boolean;
  won: boolean;
  gameFinished: boolean;
  attemptsUsed: number;
  remainingLives: number;
  songTitle: string | null;
};

export type SkipResponse = {
  challengeId: string;
  skipped: boolean;
  won: boolean;
  gameFinished: boolean;
  attemptsUsed: number;
  remainingLives: number;
  songTitle: string | null;
};

const API_BASE_URL = (
  import.meta.env.VITE_API_URL ??
  "http://127.0.0.1:8000"
).replace(/\/$/, "");

export async function getSongs(): Promise<SongResponse[]> {
  const response = await fetch(
    `${API_BASE_URL}/songs`,
  );

  if (!response.ok) {
    throw new Error(
      "Não foi possível carregar o catálogo de músicas.",
    );
  }

  return response.json();
}

export async function getDailyChallenge(): Promise<DailyChallengeResponse> {
  const response = await fetch(
    `${API_BASE_URL}/challenges/daily`,
  );

  if (!response.ok) {
    throw new Error("Não foi possivel carregar o desafio diário");
  }
  return response.json();
}

export async function startDailyChallenge():
  Promise<StartDailyChallengeResponse> {
  const response = await fetch(
    `${API_BASE_URL}/challenges/daily/start`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    throw new Error(
      "Não foi possível iniciar a partida.",
    );
  }

  return response.json();
}

export async function submitDailyGuess(
  sessionId: string,
  challengeId: string,
  answer: string,
): Promise<GuessResponse> {
  const response = await fetch(
    `${API_BASE_URL}/challenges/daily/guess`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sessionId,
        challengeId,
        answer,
      }),
    },
  );

  if (!response.ok) {
    const errorData = await response
    .json()
    .catch(() => null) as {
      detail?:string;
    } | null;

    throw new Error(
        errorData?.detail ??
      "Não foi possível validar o palpite.",
    );
  }

  return response.json();
}

export type StartDailyChallengeResponse =
  DailyChallengeResponse & {
    sessionId: string,
    remainingLives: number,
    maximumAttempts: number,
  };


export async function skipDailyGuess(
  sessionId: string,
  challengeId: string,
): Promise<SkipResponse> {
  const response = await fetch(
    `${API_BASE_URL}/challenges/daily/skip`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sessionId,
        challengeId,
      }),
    },
  );

  if (!response.ok) {
    throw new Error(
      "Não foi possível pular a tentativa.",
    );
  }

  return response.json();
}

export type SessionAttempt = {
  answer: string;
  status: "skipped" | "wrong" | "correct";
};

export type ResumeDailyChallengeResponse =
  DailyChallengeResponse & {
    sessionId: string,
    attempts: SessionAttempt[];
    remainingLives: number,
    maximumAttempts: number,
    won: boolean;
    gameFinished: boolean;
    songTitle: string | null,
  };

export async function resumeDailyChallenge(
  sessionId: string,
): Promise<ResumeDailyChallengeResponse> {
  const response = await fetch(
    `${API_BASE_URL}/challenges/daily/session/${sessionId}`,
  );

  if (!response.ok) {
    throw new Error(
      "Não foi possível recuperar a partida.",
    );
  }

  return response.json();
}

export type SongResponse = {
  id: number;
  title: string;
  chapter: number;
};

export function getDailyAudioUrl(
  challengeId: string,
): string {
  return (
    `${API_BASE_URL}/challenges/daily/audio` +
    `?challenge=${encodeURIComponent(challengeId)}`
  );
}

export type InfiniteGameResponse = {
  runId: string;
  roundId: string;
  roundNumber: number;
  attemptDurations: number[];
  remainingLives: number;
  maximumAttempts: number;
  currentStreak: number;
};

export type InfiniteRoundResult = {
  runId: string;
  roundId: string;
  won: boolean;
  gameFinished: boolean;
  attemptsUsed: number;
  remainingLives: number;
  currentStreak: number;
  songTitle: string | null;
};

export type InfiniteGuessResponse =
  InfiniteRoundResult & {
    correct: boolean;
  };

export type InfiniteSkipResponse =
  InfiniteRoundResult & {
    skipped: boolean;
  };

export type ResumeInfiniteGameResponse =
  InfiniteGameResponse & {
    attempts: SessionAttempt[];
    won: boolean;
    gameFinished: boolean;
    songTitle: string | null;
  };

export async function startInfiniteGame():
  Promise<InfiniteGameResponse> {
  const response = await fetch(
    `${API_BASE_URL}/infinite/start`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    throw new Error(
      "Não foi possível iniciar o modo infinito.",
    );
  }

  return response.json();
}

export async function resumeInfiniteGame(
  runId: string,
): Promise<ResumeInfiniteGameResponse> {
  const response = await fetch(
    `${API_BASE_URL}/infinite/` +
      encodeURIComponent(runId),
  );

  if (!response.ok) {
    throw new Error(
      "Não foi possível recuperar o modo infinito.",
    );
  }

  return response.json();
}

export async function submitInfiniteGuess(
  runId: string,
  roundId: string,
  answer: string,
): Promise<InfiniteGuessResponse> {
  const response = await fetch(
    `${API_BASE_URL}/infinite/guess`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        runId,
        roundId,
        answer,
      }),
    },
  );

  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => null) as {
        detail?: string;
      } | null;

    throw new Error(
      errorData?.detail ??
        "Não foi possível validar o palpite.",
    );
  }

  return response.json();
}

export async function skipInfiniteGuess(
  runId: string,
  roundId: string,
): Promise<InfiniteSkipResponse> {
  const response = await fetch(
    `${API_BASE_URL}/infinite/skip`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        runId,
        roundId,
      }),
    },
  );

  if (!response.ok) {
    throw new Error(
      "Não foi possível pular a tentativa.",
    );
  }

  return response.json();
}

export async function startNextInfiniteRound(
  runId: string,
  roundId: string,
): Promise<InfiniteGameResponse> {
  const response = await fetch(
    `${API_BASE_URL}/infinite/next`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        runId,
        roundId,
      }),
    },
  );

  if (!response.ok) {
    throw new Error(
      "Não foi possível iniciar a próxima rodada.",
    );
  }

  return response.json();
}

export function getInfiniteAudioUrl(
  runId: string,
  roundId: string,
): string {
  return (
    `${API_BASE_URL}/infinite/` +
    `${encodeURIComponent(runId)}/rounds/` +
    `${encodeURIComponent(roundId)}/audio`
  );
}