import assert from "node:assert/strict";
import test from "node:test";
import { parseIpProtocol, parsePortRanges } from "../src/features/applications/traffic.ts";

test("traffic port ranges normalize deterministically", () => {
  assert.deepEqual(parsePortRanges("443, 8000-8080, 53"), [
    { from: 53, to: 53 },
    { from: 443, to: 443 },
    { from: 8000, to: 8080 },
  ]);
});

test("traffic parsing rejects invalid protocol and port ranges", () => {
  assert.throws(() => parseIpProtocol("256"));
  assert.throws(() => parseIpProtocol("6.5"));
  assert.throws(() => parsePortRanges("8080-8000"));
  assert.throws(() => parsePortRanges("-1"));
  assert.throws(() => parsePortRanges("65536"));
  assert.throws(() => parsePortRanges("1-2-3"));
});
