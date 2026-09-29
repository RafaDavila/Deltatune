export type GuestGameMode = "daily" | "infinite";

function getStorageKey(
  mode: GuestGameMode,
  gameId: string,
): string {
  return `deltatune-guest-token-${mode}-${gameId}`;
}

export function saveGuestGameToken(
  mode: GuestGameMode,
  gameId: string,
  token: string,
): void {
  localStorage.setItem(
    getStorageKey(mode, gameId),
    token,
  );
}

export function getGuestGameToken(
  mode: GuestGameMode,
  gameId: string,
): string | null {
  return localStorage.getItem(
    getStorageKey(mode, gameId),
  );
}