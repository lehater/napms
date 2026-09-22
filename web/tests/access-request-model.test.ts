import assert from "node:assert/strict";
import test from "node:test";
import { toAccessRequestCatalogueScreenModel } from "../src/features/access-requests/accessRequestModels.ts";

test("Access Request catalogue mapping preserves page, subject and outcome", () => {
  assert.deepEqual(
    toAccessRequestCatalogueScreenModel({
      items: [
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
      ],
      total: 3,
      page: 2,
      pageSize: 1,
    }),
    {
      requests: [
        {
          requestRef: "request-1",
          sourceDeploymentRef: "deployment-1",
          destinationDeploymentRef: "deployment-2",
          submittedAt: "2026-09-22T00:00:00Z",
          decisionResult: "ALLOWED",
        },
      ],
      total: 3,
      page: 2,
      pageSize: 1,
    },
  );
});
