import assert from "node:assert/strict";
import test from "node:test";
import { toPolicyRuleCatalogueScreenModel } from "../src/features/policy-rules/policyRuleModels.ts";

test("Policy Rule catalogue mapping preserves page, subject and state", () => {
  assert.deepEqual(
    toPolicyRuleCatalogueScreenModel({
      items: [
        {
          policyRuleRef: "rule-1",
          version: 2,
          effectState: "ACTIVE",
          effectiveWindow: { effectiveFrom: null, effectiveUntil: null },
          sourceDeploymentRef: "source-1",
          destinationDeploymentRef: "destination-1",
          interactionRevisionRef: "revision-1",
          authorizationEvidence: [],
          justifications: [],
          operationalHistory: [],
        },
      ],
      total: 3,
      page: 2,
      pageSize: 1,
    }),
    {
      rules: [
        {
          policyRuleRef: "rule-1",
          effectState: "ACTIVE",
          sourceDeploymentRef: "source-1",
          destinationDeploymentRef: "destination-1",
          interactionRevisionRef: "revision-1",
        },
      ],
      total: 3,
      page: 2,
      pageSize: 1,
    },
  );
});
