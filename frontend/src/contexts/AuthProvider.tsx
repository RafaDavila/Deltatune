import {
  useEffect,
  useState,
} from "react";

import type {
  ReactNode,
} from "react";

import {
  AuthContext,
} from "./AuthContext";

import {
  getCurrentUser,
  loginUser,
  registerUser,
} from "../services/deltatuneApi";

import type {
  LoginInput,
  RegisterUserInput,
  UserResponse,
} from "../services/deltatuneApi";

import {
  AUTH_SESSION_EXPIRED_EVENT,
  clearAccessToken,
  getAccessToken,
  saveAccessToken,
} from "../services/authStorage";

type AuthProviderProps = {
  children: ReactNode;
};

export function AuthProvider({
  children,
}: AuthProviderProps) {
  const [user, setUser] =
    useState<UserResponse | null>(null);

  const [isLoading, setIsLoading] =
    useState(true);

  const [sessionExpired, setSessionExpired] =
    useState(false);

  useEffect(() => {
    function handleSessionExpired() {
      setUser(null);
      setIsLoading(false);
      setSessionExpired(true);
    }

    window.addEventListener(
      AUTH_SESSION_EXPIRED_EVENT,
      handleSessionExpired,
    );

    return () => {
      window.removeEventListener(
        AUTH_SESSION_EXPIRED_EVENT,
        handleSessionExpired,
      );
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function restoreAuthentication() {
      const restoringToken = getAccessToken();

      if (restoringToken === null) {
        if (!cancelled) {
          setIsLoading(false);
        }

        return;
      }

      try {
        const currentUser =
          await getCurrentUser();

        if (
          !cancelled &&
          getAccessToken() === restoringToken
        ) {
          setUser(currentUser);
          setSessionExpired(false);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

        void restoreAuthentication().catch(() => {
      // A sessão rejeitada com 401 já é tratada em apiFetch.
      // Uma falha de rede preserva o token para tentar depois.
    });

    return () => {
      cancelled = true;
    };
  }, []);

  async function login(
    input: LoginInput,
  ): Promise<void> {
    const token = await loginUser(
      input,
    );

    saveAccessToken(
      token.accessToken,
    );

    try {
      const currentUser =
        await getCurrentUser();

      setUser(currentUser);
    } catch (error) {
      clearAccessToken();
      throw error;
    }
  }

  async function register(
    input: RegisterUserInput,
  ): Promise<void> {
    await registerUser(input);

    await login({
      email: input.email,
      password: input.password,
    });
  }

  function logout(): void {
    clearAccessToken();
    setUser(null);
    setSessionExpired(false);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: user !== null,
        isLoading,
        login,
        register,
        logout,
        sessionExpired,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}