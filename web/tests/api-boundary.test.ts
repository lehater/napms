import assert from "node:assert/strict";
import test from "node:test";
import { request } from "../src/app/api.ts";
import { setRuntimeAccessToken } from "../src/app/auth-session.ts";

test("API boundary emits bearer auth and preserves caller concurrency/idempotency headers", async () => {
  const originalFetch = globalThis.fetch;
  let captured: { path: string; init: RequestInit } | undefined;
  globalThis.fetch = (async (path: string | URL | Request, init?: RequestInit) => {
    captured = { path: String(path), init: init ?? {} };
    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }) as typeof fetch;
  setRuntimeAccessToken("runtime-token");
  try {
    await request("/v1/example", {
      method: "POST",
      headers: { "If-Match": "7", "Idempotency-Key": "stable-key" },
      body: JSON.stringify({ resourceRef: "r-1" }),
    });
    assert.equal(captured?.path, "/v1/example");
    const headers = new Headers(captured?.init.headers);
    assert.equal(headers.get("Authorization"), "Bearer runtime-token");
    assert.equal(headers.get("If-Match"), "7");
    assert.equal(headers.get("Idempotency-Key"), "stable-key");
    assert.equal(headers.get("Content-Type"), "application/json");
    assert.equal(captured?.init.body, '{"resourceRef":"r-1"}');
  } finally {
    setRuntimeAccessToken(null);
    globalThis.fetch = originalFetch;
  }
});

test("API boundary maps canonical error status without collapsing 401 and 403", async () => {
  const originalFetch = globalThis.fetch;
  try {
    for (const [status, kind] of [
      [401, "unauthenticated"],
      [403, "forbidden"],
      [409, "conflict"],
      [422, "rejected"],
      [503, "unavailable"],
    ] as const) {
      globalThis.fetch = (async () => new Response(null, { status })) as typeof fetch;
      await assert.rejects(request("/v1/example"), (error: unknown) => {
        return error instanceof Error && error.message === kind;
      });
    }
  } finally {
    globalThis.fetch = originalFetch;
  }
});
