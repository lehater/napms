import assert from "node:assert/strict";
import test from "node:test";
import { parseRoute } from "../src/app/router.ts";

test("canonical static routes resolve to their workspace ids", () => {
  const cases = [
    ["/resources", "resources"],
    ["/resources/new", "resource-new"],
    ["/applications", "applications"],
    ["/applications/new", "application-new"],
    ["/interactions/new", "interaction-new"],
    ["/deployments", "deployments"],
    ["/deployments/new", "deployment-new"],
    ["/business-processes", "processes"],
    ["/business-processes/new", "process-new"],
    ["/access-requests", "access-requests"],
    ["/access-requests/new", "access-request-new"],
    ["/policy-rules", "policy-rules"],
    ["/policy-materializations/new", "policy-export"],
  ] as const;
  for (const [path, id] of cases) assert.equal(parseRoute(path).id, id);
});

test("canonical reference routes decode stable references", () => {
  assert.deepEqual(parseRoute("/resources/r%201"), {
    id: "resource-detail",
    path: "/resources/r%201",
    resourceRef: "r 1",
  });
  assert.equal(parseRoute("/applications/app-1/components/new").id, "component-new");
  assert.equal(parseRoute("/applications/app-1").id, "application-detail");
  assert.equal(parseRoute("/interactions/i-1/revisions/new").id, "revision-new");
  assert.deepEqual(parseRoute("/deployments/d%201"), {
    id: "deployment-detail",
    path: "/deployments/d%201",
    deploymentRef: "d 1",
  });
  assert.equal(parseRoute("/business-processes/p-1").id, "process-detail");
  assert.equal(parseRoute("/access-requests/a-1/decision").id, "access-request-decision");
  assert.equal(parseRoute("/policy-rules/rule-1").id, "policy-rule-detail");
});
