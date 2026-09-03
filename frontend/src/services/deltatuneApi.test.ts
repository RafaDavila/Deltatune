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
  saveAccessToken,
} from "./authStorage";

import {
  getCurrentUser,
} from "./deltatuneApi";

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
});