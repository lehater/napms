import assert from "node:assert/strict";
import test from "node:test";
import {
  toDeploymentDetailScreenModel,
  toDeploymentScreenModel,
} from "../src/features/deployments/deploymentModels.ts";

test("Deployment Screen Model preserves page and entity identity", () => {
  assert.deepEqual(
    toDeploymentScreenModel({
      items: [
        {
          deploymentRef: "deployment-1",
          componentRef: "component-1",
          resourceRef: "resource-1",
        },
      ],
      total: 3,
      page: 2,
      pageSize: 1,
    }),
    {
      deployments: [
        {
          deploymentRef: "deployment-1",
          componentRef: "component-1",
          resourceRef: "resource-1",
        },
      ],
      total: 3,
      page: 2,
      pageSize: 1,
    },
  );
});

test("Deployment detail model preserves accepted realization facts", () => {
  assert.deepEqual(
    toDeploymentDetailScreenModel({
      deploymentRef: "deployment-1",
      componentRef: "component-1",
      resourceRef: "resource-1",
    }),
    {
      deploymentRef: "deployment-1",
      componentRef: "component-1",
      resourceRef: "resource-1",
    },
  );
});
