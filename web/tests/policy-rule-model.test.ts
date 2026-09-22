import assert from "node:assert/strict";
import test from "node:test";
import { toPolicyRuleCatalogue } from "../src/features/policy-rules/policyRuleModels.ts";

test("Policy Rule catalogue mapping preserves authoritative operational state", () => {
  assert.deepEqual(
    toPolicyRuleCatalogue([
      {
        policyRuleRef: "rule-1",
        version: 3,
        effectState: "ACTIVE",
        effectiveWindow: {
          effectiveFrom: null,
          effectiveUntil: null,
        },
        sourceDeploymentRef: "deployment-1",
        destinationDeploymentRef: "deployment-2",
        interactionRevisionRef: "revision-1",
        authorizationEvidence: [],
        justifications: [],
        operationalHistory: [],
      },
    ]),
    [{ policyRuleRef: "rule-1", effectState: "ACTIVE" }],
  );
});
