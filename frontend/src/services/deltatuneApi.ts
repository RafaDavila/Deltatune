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

import { getAccessToken } from "./authStorage";

export type UserResponse = {
  id: string;
  displayName: string;
  email: string;
  isActive: boolean;
  createdAt: string;
};

export type RegisterUserInput = {
  displayName: string;
  email: string;
  password: string;
};

export type LoginInput = {
  email: string;
  password: string;
};

export type TokenResponse = {
  accessToken: string;
  tokenType: string;
};

export type DailyWeekStatus =
  | "won"
  | "lost"
  | "in_progress"
  | "not_played"
  | "unavailable";

export type DailyWeekDayResponse = {
  challengeId: string;
  challengeNumber: number;
  status: DailyWeekStatus;
  attemptsUsed: number;
  sessionId: string | null;
};

export type DailyWeekResponse = {
  days: DailyWeekDayResponse[];
};

const API_BASE_URL = (
  import.meta.env.VITE_API_URL ??
  "http://127.0.0.1:8000"
).replace(/\/$/, "");

async function apiFetch(
  path: string,
  options: RequestInit = {},
): Promise<Response> {
  const headers = new Headers(
    options.headers,
  );

  const accessToken = getAccessToken();

  if (accessToken !== null) {
    headers.set(
      "Authorization",
      `Bearer ${accessToken}`,
    );
  }

  return fetch(
    `${API_BASE_URL}${path}`,
    {
      ...options,
      headers,
    },
  );
}

async function readErrorMessage(
  response: Response,
  fallbackMessage: string,
): Promise<string> {
  const errorData = await response
    .json()
    .catch(() => null) as {
      detail?: string;
    } | null;

  return (
    errorData?.detail ??
    fallbackMessage
  );
}

export async function registerUser(
  input: RegisterUserInput,
): Promise<UserResponse> {
  const response = await apiFetch(
    "/auth/register",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(input),
    },
  );

  if (!response.ok) {
    throw new Error(
      await readErrorMessage(
        response,
        "Não foi possível criar a conta.",
      ),
    );
  }

  return response.json();
}


export async function loginUser(
  input: LoginInput,
): Promise<TokenResponse> {
  const response = await apiFetch(
    "/auth/login",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(input),
    },
  );

  if (!response.ok) {
    throw new Error(
      await readErrorMessage(
        response,
        "Não foi possível entrar na conta.",
      ),
    );
  }

  return response.json();
}


export async function getCurrentUser():
  Promise<UserResponse> {
  const response = await apiFetch(
    "/auth/me",
  );

  if (!response.ok) {
    throw new Error(
      await readErrorMessage(
        response,
        "Não foi possível carregar a conta.",
      ),
    );
  }

  return response.json();
}

export async function getSongs(): Promise<SongResponse[]> {
  const response = await apiFetch(
    "/songs",
  );

  if (!response.ok) {
    throw new Error(
      "Não foi possível carregar o catálogo de músicas.",
    );
  }

  return response.json();
}

export async function getDailyChallenge(): Promise<DailyChallengeResponse> {
  const response = await apiFetch(
    "/challenges/daily",
  );

  if (!response.ok) {
    throw new Error("Não foi possivel carregar o desafio diário");
  }
  return response.json();
}

export async function startDailyChallenge():
  Promise<StartDailyChallengeResponse> {
  const response = await apiFetch(
    "/challenges/daily/start",
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
        detail?: string;
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

export async function getDailyWeek():
  Promise<DailyWeekResponse> {
  const response = await apiFetch(
    "/challenges/daily/week",
  );

  if (!response.ok) {
    throw new Error(
      await readErrorMessage(
        response,
        "Não foi possível carregar a semana.",
      ),
    );
  }

  return response.json();
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

export type InfiniteRecordResponse = {
  bestStreak: number;
};

export async function getInfiniteRecord():
  Promise<InfiniteRecordResponse> {
  const response = await apiFetch(
    "/infinite/record",
  );

  if (!response.ok) {
    throw new Error(
      await readErrorMessage(
        response,
        "Não foi possível carregar o recorde.",
      ),
    );
  }

  return response.json();
}

export async function startInfiniteGame():
  Promise<InfiniteGameResponse> {
  const response = await fetch(
    "/infinite/start",
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