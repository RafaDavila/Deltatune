const ACCESS_TOKEN_STORAGE_KEY =
  "deltatune-access-token";

export function getAccessToken(): string | null {
  return localStorage.getItem(
    ACCESS_TOKEN_STORAGE_KEY,
  );
}

export function saveAccessToken(
  accessToken: string,
): void {
  localStorage.setItem(
    ACCESS_TOKEN_STORAGE_KEY,
    accessToken,
  );
}

export function clearAccessToken(): void {
  localStorage.removeItem(
    ACCESS_TOKEN_STORAGE_KEY,
  );
}

export const AUTH_SESSION_EXPIRED_EVENT =
  "deltatune:session-expired";

export function expireAccessToken(
  rejectedToken: string,
): void {
  if (getAccessToken() !== rejectedToken) {
    return;
  }

  clearAccessToken();

  window.dispatchEvent(
    new Event(AUTH_SESSION_EXPIRED_EVENT),
  );
}