import assert from "node:assert/strict";
import test from "node:test";
import {
  authSession,
  setRuntimeAccessToken,
} from "../src/app/auth-session.ts";

test("auth session is runtime-only and supports explicit recovery clearing", () => {
  setRuntimeAccessToken("runtime-token");
  assert.equal(authSession.accessToken(), "runtime-token");
  setRuntimeAccessToken(null);
  assert.equal(authSession.accessToken(), null);
});
