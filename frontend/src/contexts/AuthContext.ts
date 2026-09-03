import { createContext } from "react";

import type {
  LoginInput,
  RegisterUserInput,
  UserResponse,
} from "../services/deltatuneApi";

export type AuthContextValue = {
  user: UserResponse | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (
    input: LoginInput,
  ) => Promise<void>;
  register: (
    input: RegisterUserInput,
  ) => Promise<void>;
  logout: () => void;
};

export const AuthContext = createContext<
  AuthContextValue | undefined
>(undefined);