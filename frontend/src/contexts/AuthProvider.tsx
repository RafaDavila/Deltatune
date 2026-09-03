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

  useEffect(() => {
    let cancelled = false;

    async function restoreAuthentication() {
      if (getAccessToken() === null) {
        if (!cancelled) {
          setIsLoading(false);
        }

        return;
      }

      try {
        const currentUser =
          await getCurrentUser();

        if (!cancelled) {
          setUser(currentUser);
        }
      } catch {
        clearAccessToken();
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void restoreAuthentication();

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
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}