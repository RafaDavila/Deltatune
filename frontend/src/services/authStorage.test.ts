import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  AUTH_SESSION_EXPIRED_EVENT,
  clearAccessToken,
  expireAccessToken,
  getAccessToken,
  saveAccessToken,
} from "./authStorage";

describe("authStorage", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("starts without an access token", () => {
    expect(getAccessToken()).toBeNull();
  });

  it("saves the access token", () => {
    saveAccessToken("token-de-teste");

    expect(getAccessToken()).toBe(
      "token-de-teste",
    );
  });

  it("clears the access token", () => {
    saveAccessToken("token-de-teste");

    clearAccessToken();

    expect(getAccessToken()).toBeNull();
  });

    it("removes the rejected token and notifies the interface", () => {
    saveAccessToken("token-antigo");

    const onExpired = vi.fn();

    window.addEventListener(
      AUTH_SESSION_EXPIRED_EVENT,
      onExpired,
    );

    try {
      expireAccessToken("token-antigo");

      expect(getAccessToken()).toBeNull();
      expect(onExpired).toHaveBeenCalledOnce();
    } finally {
      window.removeEventListener(
        AUTH_SESSION_EXPIRED_EVENT,
        onExpired,
      );
    }
  });

  it("preserves a new token when an old request is rejected", () => {
    saveAccessToken("token-novo");

    const onExpired = vi.fn();

    window.addEventListener(
      AUTH_SESSION_EXPIRED_EVENT,
      onExpired,
    );

    try {
      expireAccessToken("token-antigo");

      expect(getAccessToken()).toBe("token-novo");
      expect(onExpired).not.toHaveBeenCalled();
    } finally {
      window.removeEventListener(
        AUTH_SESSION_EXPIRED_EVENT,
        onExpired,
      );
    }
  });

});