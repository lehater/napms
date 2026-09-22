import assert from "node:assert/strict";
import test from "node:test";
import {
  toBusinessProcessCatalogue,
  toBusinessProcessDetail,
} from "../src/features/business-connectivity/businessConnectivityModels.ts";

const process = {
  processRef: "process-1",
  name: "Order handling",
  description: "Business justification",
  criticalityLabel: "HIGH",
  organizationExternalReference: "ORG-1",
  organizationDisplayName: "Operations",
  version: 4,
  needs: [
    {
      needRef: "need-1",
      interactionRef: "interaction-1",
      participantComponentRef: "component-1",
      businessBasis: "Required for orders",
      status: "ACTIVE",
    },
  ],
};

test("Business Process catalogue mapping keeps stable identity", () => {
  assert.deepEqual(toBusinessProcessCatalogue([process]), [
    {
      processRef: "process-1",
      name: "Order handling",
      description: "Business justification",
      criticalityLabel: "HIGH",
    },
  ]);
});

test("Business Process detail mapping preserves connectivity needs", () => {
  assert.deepEqual(toBusinessProcessDetail(process), process);
});
