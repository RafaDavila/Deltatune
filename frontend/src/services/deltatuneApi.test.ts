import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  clearAccessToken,
  getAccessToken,
  saveAccessToken,
} from "./authStorage";

import {
  ApiError,
  getCurrentUser,
  loginUser,
  startDailyChallenge,
  startInfiniteGame,
  getInfiniteAudioBlob,
  resumeDailyChallenge,
  resumeInfiniteGame,
  skipDailyGuess,
  skipInfiniteGuess,
  startNextInfiniteRound,
  submitDailyGuess,
  submitInfiniteGuess,
} from "./deltatuneApi";

import {
  getGuestGameToken,
  saveGuestGameToken,
} from "./guestGameStorage";

describe("deltatuneApi authentication", () => {
  beforeEach(() => {
    clearAccessToken();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("sends the access token as a Bearer token", async () => {
    saveAccessToken("token-de-teste");

    const user = {
      id: "user-id",
      displayName: "Rafael",
      email: "rafael@example.com",
      isActive: true,
      createdAt: "2026-09-03T12:00:00Z",
    };

    const fetchMock = vi
      .fn<typeof fetch>()
      .mockResolvedValue(
        new Response(
          JSON.stringify(user),
          {
            status: 200,
            headers: {
              "Content-Type": "application/json",
            },
          },
        ),
      );

    vi.stubGlobal(
      "fetch",
      fetchMock,
    );

    const result = await getCurrentUser();

    const requestOptions =
      fetchMock.mock.calls[0][1];

    const headers = new Headers(
      requestOptions?.headers,
    );

    expect(
      headers.get("Authorization"),
    ).toBe("Bearer token-de-teste");

    expect(result).toEqual(user);
  });

  it("clears the session when an authenticated request returns 401", async () => {
    saveAccessToken("token-expirado");

    vi.stubGlobal(
      "fetch",
      vi.fn<typeof fetch>().mockResolvedValue(
        new Response(
          JSON.stringify({
            detail: "Autenticação inválida.",
          }),
          {
            status: 401,
            headers: {
              "Content-Type": "application/json",
            },
          },
        ),
      ),
    );

    await expect(
      getCurrentUser(),
    ).rejects.toThrow("Autenticação inválida.");

    expect(getAccessToken()).toBeNull();
  });

  it("preserves the session when login returns 401", async () => {
    saveAccessToken("token-atual");

    vi.stubGlobal(
      "fetch",
      vi.fn<typeof fetch>().mockResolvedValue(
        new Response(
          JSON.stringify({
            detail: "E-mail ou senha inválidos.",
          }),
          {
            status: 401,
            headers: {
              "Content-Type": "application/json",
            },
          },
        ),
      ),
    );

    await expect(
      loginUser({
        email: "rafael@example.com",
        password: "senha-incorreta",
      }),
    ).rejects.toThrow("E-mail ou senha inválidos.");

    expect(getAccessToken()).toBe("token-atual");
  });
});

describe("deltatuneApi guest games", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    localStorage.clear();
  });

  it("saves the guest token when starting a daily game", async () => {
    const game = {
      challengeId: "challenge-id",
      challengeNumber: 1,
      attemptDurations: [0.5, 1, 2, 4, 8, 16],
      nextResetAt: "2026-09-30T03:00:00Z",
      sessionId: "daily-session-id",
      remainingLives: 6,
      maximumAttempts: 6,
      guestToken: "daily-guest-token",
    };

    vi.stubGlobal(
      "fetch",
      vi.fn<typeof fetch>().mockResolvedValue(
        new Response(JSON.stringify(game), {
          status: 201,
          headers: {
            "Content-Type": "application/json",
          },
        }),
      ),
    );

    const result = await startDailyChallenge();

    expect(result).toEqual(game);

    expect(
      getGuestGameToken("daily", game.sessionId),
    ).toBe(game.guestToken);

    expect(
      getGuestGameToken("infinite", game.sessionId),
    ).toBeNull();
  });

  it("saves the guest token when starting an infinite game", async () => {
    const game = {
      runId: "infinite-run-id",
      roundId: "round-id",
      roundNumber: 1,
      attemptDurations: [0.5, 1, 2, 4, 8, 16],
      remainingLives: 6,
      maximumAttempts: 6,
      currentStreak: 0,
      guestToken: "infinite-guest-token",
    };

    vi.stubGlobal(
      "fetch",
      vi.fn<typeof fetch>().mockResolvedValue(
        new Response(JSON.stringify(game), {
          status: 201,
          headers: {
            "Content-Type": "application/json",
          },
        }),
      ),
    );

    const result = await startInfiniteGame();

    expect(result).toEqual(game);

    expect(
      getGuestGameToken("infinite", game.runId),
    ).toBe(game.guestToken);

    expect(
      getGuestGameToken("daily", game.runId),
    ).toBeNull();
  });
});

describe("guest game request headers", () => {
  beforeEach(() => {
    localStorage.clear();

    saveGuestGameToken(
      "daily",
      "daily-id",
      "daily-token",
    );

    saveGuestGameToken(
      "infinite",
      "run-id",
      "infinite-token",
    );

    saveGuestGameToken(
      "daily",
      "another-daily-id",
      "another-daily-token",
    );

    saveGuestGameToken(
      "infinite",
      "another-run-id",
      "another-infinite-token",
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    localStorage.clear();
  });

  it.each([
    {
      name: "daily guess",
      token: "daily-token",
      request: () =>
        submitDailyGuess("daily-id", "challenge-id", "Palpite"),
    },
    {
      name: "daily skip",
      token: "daily-token",
      request: () =>
        skipDailyGuess("daily-id", "challenge-id"),
    },
    {
      name: "daily resume",
      token: "daily-token",
      request: () =>
        resumeDailyChallenge("daily-id"),
    },
    {
      name: "infinite guess",
      token: "infinite-token",
      request: () =>
        submitInfiniteGuess("run-id", "round-id", "Palpite"),
    },
    {
      name: "infinite skip",
      token: "infinite-token",
      request: () =>
        skipInfiniteGuess("run-id", "round-id"),
    },
    {
      name: "infinite resume",
      token: "infinite-token",
      request: () =>
        resumeInfiniteGame("run-id"),
    },
    {
      name: "infinite next round",
      token: "infinite-token",
      request: () =>
        startNextInfiniteRound("run-id", "round-id"),
    },
    {
      name: "infinite audio",
      token: "infinite-token",
      request: () =>
        getInfiniteAudioBlob("run-id", "round-id"),
    },
  ])("sends the correct token for $name", async ({
    token,
    request,
  }) => {
    const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(JSON.stringify({}), {
        status: 200,
        headers: {
          "Content-Type": "application/json",
        },
      }),
    );

    vi.stubGlobal("fetch", fetchMock);

    await request();

    expect(fetchMock).toHaveBeenCalledTimes(1);

    const headers = new Headers(
      fetchMock.mock.calls[0][1]?.headers,
    );

    expect(headers.get("X-Guest-Token")).toBe(token);
    expect(headers.get("Authorization")).toBeNull();
  });

    it("preserves the guest token after advancing a round", async () => {
    const nextRound = {
      runId: "run-id",
      roundId: "next-round-id",
      roundNumber: 2,
      attemptDurations: [0.5, 1, 2, 4, 8, 16],
      remainingLives: 6,
      maximumAttempts: 6,
      currentStreak: 1,
      guestToken: null,
    };

    const fetchMock = vi.fn<typeof fetch>()
      .mockResolvedValueOnce(
        new Response(JSON.stringify(nextRound), {
          status: 201,
          headers: {
            "Content-Type": "application/json",
          },
        }),
      )
      .mockResolvedValueOnce(
        new Response("audio", {
          status: 200,
          headers: {
            "Content-Type": "audio/mpeg",
          },
        }),
      );

    vi.stubGlobal("fetch", fetchMock);

    const game = await startNextInfiniteRound(
      "run-id",
      "round-id",
    );

    expect(
      getGuestGameToken("infinite", "run-id"),
    ).toBe("infinite-token");

    await getInfiniteAudioBlob(
      game.runId,
      game.roundId,
    );

    const audioHeaders = new Headers(
      fetchMock.mock.calls[1][1]?.headers,
    );

    expect(
      audioHeaders.get("X-Guest-Token"),
    ).toBe("infinite-token");

    expect(
      String(fetchMock.mock.calls[1][0]),
    ).toContain(
      "/infinite/run-id/rounds/next-round-id/audio",
    );
  });
});

describe("infinite start request", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    localStorage.clear();
  });

  it.each([true, false])(
    "uses the API URL with authenticated=%s",
    async (authenticated) => {
      if (authenticated) {
        saveAccessToken("infinite-access-token");
      }

      const game = {
        runId: "run-id",
        roundId: "round-id",
        roundNumber: 1,
        attemptDurations: [0.5, 1, 2, 4, 8, 16],
        remainingLives: 6,
        maximumAttempts: 6,
        currentStreak: 0,
        guestToken: authenticated ? null : "guest-token",
      };

      const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(
        new Response(JSON.stringify(game), {
          status: 201,
          headers: {
            "Content-Type": "application/json",
          },
        }),
      );

      vi.stubGlobal("fetch", fetchMock);

      const result = await startInfiniteGame();

      expect(fetchMock).toHaveBeenCalledTimes(1);

      const [url, options] = fetchMock.mock.calls[0];
      const apiBaseUrl = (
        import.meta.env.VITE_API_URL ??
        "http://127.0.0.1:8000"
      ).replace(/\/$/, "");

      expect(String(url)).toBe(`${apiBaseUrl}/infinite/start`);
      expect(options?.method).toBe("POST");

      const headers = new Headers(options?.headers);

      expect(headers.get("Authorization")).toBe(
        authenticated ? "Bearer infinite-access-token" : null,
      );
      expect(headers.get("X-Guest-Token")).toBeNull();
      expect(result).toEqual(game);
    },
  );
});

describe("game recovery errors", () => {
  beforeEach(() => {
    localStorage.clear();
    clearAccessToken();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    localStorage.clear();
  });

  const recoveryRequests = [
    {
      name: "daily",
      request: () => resumeDailyChallenge("daily-id"),
    },
    {
      name: "infinite",
      request: () => resumeInfiniteGame("run-id"),
    },
  ];

  describe.each(recoveryRequests)("$name", ({ request }) => {
    it.each([404, 409, 500, 503])(
      "preserves HTTP status %s and the API message",
      async (status) => {
        vi.stubGlobal(
          "fetch",
          vi.fn<typeof fetch>().mockResolvedValue(
            new Response(
              JSON.stringify({
                detail: "Falha ao recuperar a partida.",
              }),
              {
                status,
                headers: {
                  "Content-Type": "application/json",
                },
              },
            ),
          ),
        );

        const result = request();

        await expect(result).rejects.toBeInstanceOf(ApiError);

        await expect(result).rejects.toMatchObject({
          status,
          message: "Falha ao recuperar a partida.",
        });
      },
    );

    it("propagates network failures without an HTTP status", async () => {
      const networkError = new TypeError("Failed to fetch");

      vi.stubGlobal(
        "fetch",
        vi.fn<typeof fetch>().mockRejectedValue(networkError),
      );

      await expect(request()).rejects.toBe(networkError);
    });
  });
});