import assert from "node:assert/strict";
import test from "node:test";

test("API adapter declares canonical auth, concurrency, idempotency and error mapping", async () => {
  const source = await import("node:fs/promises").then((fs) =>
    fs.readFile(new URL("../src/app/api.ts", import.meta.url), "utf8"),
  );
  assert.match(source, /Authorization.*Bearer/);
  assert.match(source, /If-Match/);
  assert.match(source, /Idempotency-Key/);
  assert.match(source, /statusToErrorKind\(response\.status\)/);
  assert.match(source, /JSON\.stringify/);
});
