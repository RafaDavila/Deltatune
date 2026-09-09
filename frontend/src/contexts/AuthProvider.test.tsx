import {
  act,
  render,
  screen,
} from "@testing-library/react";

import userEvent from
  "@testing-library/user-event";

import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  getCurrentUser,
  loginUser,
} from "../services/deltatuneApi";

import {
  AUTH_SESSION_EXPIRED_EVENT,
  getAccessToken,
  saveAccessToken,
} from "../services/authStorage";

import { useAuth } from "../hooks/useAuth";
import { AuthProvider } from "./AuthProvider";

vi.mock("../services/deltatuneApi", () => ({
  getCurrentUser: vi.fn(),
  loginUser: vi.fn(),
  registerUser: vi.fn(),
}));

vi.mock("../services/authStorage", async (importOriginal) => ({
  ...await importOriginal<typeof import("../services/authStorage")>(),
  clearAccessToken: vi.fn(),
  getAccessToken: vi.fn(),
  saveAccessToken: vi.fn(),
}));

const currentUser = {
  id: "user-id",
  displayName: "Rafael",
  email: "rafael@example.com",
  isActive: true,
  createdAt: "2026-09-03T12:00:00Z",
};

function AuthProbe() {
  const {
    user,
    isLoading,
    login,
  } = useAuth();

  if (isLoading) {
    return <span>Carregando</span>;
  }

  return (
    <>
      <span>
        {user?.displayName ?? "Visitante"}
      </span>

      <button
        type="button"
        onClick={() => {
          void login({
            email: "rafael@example.com",
            password: "Deltarune123!",
          });
        }}
      >
        Entrar
      </button>
    </>
  );
}

describe("AuthProvider", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    vi.mocked(
      getAccessToken,
    ).mockReturnValue(null);
  });

  it("restores the authenticated user", async () => {
    vi.mocked(
      getAccessToken,
    ).mockReturnValue("token-salvo");

    vi.mocked(
      getCurrentUser,
    ).mockResolvedValue(currentUser);

    render(
      <AuthProvider>
        <AuthProbe />
      </AuthProvider>,
    );

    expect(
      await screen.findByText("Rafael"),
    ).toBeInTheDocument();
  });

  it("logs the user in and saves the token", async () => {
    vi.mocked(
      loginUser,
    ).mockResolvedValue({
      accessToken: "novo-token",
      tokenType: "bearer",
    });

    vi.mocked(
      getCurrentUser,
    ).mockResolvedValue(currentUser);

    const tester = userEvent.setup();

    render(
      <AuthProvider>
        <AuthProbe />
      </AuthProvider>,
    );

    await screen.findByText("Visitante");

    await tester.click(
      screen.getByRole(
        "button",
        { name: "Entrar" },
      ),
    );

    expect(
      await screen.findByText("Rafael"),
    ).toBeInTheDocument();

    expect(saveAccessToken).toHaveBeenCalledWith(
      "novo-token",
    );
  });

    it("removes the user when the session expires", async () => {
    vi.mocked(
      getAccessToken,
    ).mockReturnValue("token-salvo");

    vi.mocked(
      getCurrentUser,
    ).mockResolvedValue(currentUser);

    render(
      <AuthProvider>
        <AuthProbe />
      </AuthProvider>,
    );

    expect(
      await screen.findByText("Rafael"),
    ).toBeInTheDocument();

    vi.mocked(
      getAccessToken,
    ).mockReturnValue(null);

    act(() => {
      window.dispatchEvent(
        new Event(AUTH_SESSION_EXPIRED_EVENT),
      );
    });

    expect(
      screen.getByText("Visitante"),
    ).toBeInTheDocument();

    expect(
      screen.queryByText("Rafael"),
    ).not.toBeInTheDocument();
  });

    it("ignores a restoration response after the session expires", async () => {
    vi.mocked(
      getAccessToken,
    ).mockReturnValue("token-antigo");

    let resolveCurrentUser!: (
      user: typeof currentUser,
    ) => void;

    const pendingUser = new Promise<
      typeof currentUser
    >((resolve) => {
      resolveCurrentUser = resolve;
    });

    vi.mocked(
      getCurrentUser,
    ).mockReturnValue(pendingUser);

    render(
      <AuthProvider>
        <AuthProbe />
      </AuthProvider>,
    );

    expect(
      screen.getByText("Carregando"),
    ).toBeInTheDocument();

    vi.mocked(
      getAccessToken,
    ).mockReturnValue(null);

    act(() => {
      window.dispatchEvent(
        new Event(AUTH_SESSION_EXPIRED_EVENT),
      );
    });

    expect(
      screen.getByText("Visitante"),
    ).toBeInTheDocument();

    await act(async () => {
      resolveCurrentUser(currentUser);
      await pendingUser;
    });

    expect(
      screen.getByText("Visitante"),
    ).toBeInTheDocument();

    expect(
      screen.queryByText("Rafael"),
    ).not.toBeInTheDocument();
  });

});
