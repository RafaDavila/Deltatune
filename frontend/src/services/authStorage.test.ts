import {
  beforeEach,
  describe,
  expect,
  it,
} from "vitest";

import {
  clearAccessToken,
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
});