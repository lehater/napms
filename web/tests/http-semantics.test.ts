import assert from "node:assert/strict";
import test from "node:test";
import { statusToErrorKind } from "../src/app/http-semantics.ts";

test("HTTP status semantics keep authentication, authorization, conflict and rejection distinct", () => {
  assert.equal(statusToErrorKind(401), "unauthenticated");
  assert.equal(statusToErrorKind(403), "forbidden");
  assert.equal(statusToErrorKind(404), "not-found");
  assert.equal(statusToErrorKind(409), "conflict");
  assert.equal(statusToErrorKind(422), "rejected");
  assert.equal(statusToErrorKind(503), "unavailable");
  assert.equal(statusToErrorKind(500), "technical");
});
