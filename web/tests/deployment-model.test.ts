import assert from "node:assert/strict";
import test from "node:test";
import { toDeploymentScreenModel } from "../src/features/deployments/deploymentModels.ts";

test("Deployment Screen Model preserves Component and Resource identity", () => {
  assert.deepEqual(
    toDeploymentScreenModel([
      {
        deploymentRef: "deployment-1",
        componentRef: "component-1",
        resourceRef: "resource-1",
      },
    ]),
    {
      deployments: [
        {
          deploymentRef: "deployment-1",
          componentRef: "component-1",
          resourceRef: "resource-1",
        },
      ],
    },
  );
});
