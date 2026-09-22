import assert from "node:assert/strict";
import test from "node:test";
import { toAccessRequestCatalogue } from "../src/features/access-requests/accessRequestModels.ts";

test("Access Request catalogue mapping preserves immutable request identity and outcome", () => {
  assert.deepEqual(
    toAccessRequestCatalogue([
      {
        requestRef: "request-1",
        version: 2,
        sourceDeploymentRef: "deployment-1",
        destinationDeploymentRef: "deployment-2",
        interactionRevisionRef: "revision-1",
        needRef: "need-1",
        submittedAt: "2026-09-22T00:00:00Z",
        decisionResult: "ALLOWED",
      },
    ]),
    [{ requestRef: "request-1", decisionResult: "ALLOWED" }],
  );
});
