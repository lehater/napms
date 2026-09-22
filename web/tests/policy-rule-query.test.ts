import assert from "node:assert/strict";
import test from "node:test";
import { serializePolicyRuleCatalogueQuery } from "../src/app/policy-rule-catalogue-query.ts";
import {
  defaultPolicyRuleCatalogueQuery,
  toPolicyRuleCatalogueQuery,
} from "../src/features/policy-rules/policyRuleCatalogueQuery.ts";

test("Policy Rule catalogue query serialization preserves accepted semantics", () => {
  const query = toPolicyRuleCatalogueQuery({
    ...defaultPolicyRuleCatalogueQuery,
    search: "  rule-1  ",
    sourceDeploymentRef: "source-1",
    destinationDeploymentRef: "destination-1",
    effectState: "ACTIVE",
    sortBy: "effectState",
    sortDirection: "desc",
    page: 3,
    pageSize: 50,
  });

  assert.equal(
    serializePolicyRuleCatalogueQuery(query),
    "search=rule-1&sourceDeploymentRef=source-1&destinationDeploymentRef=destination-1&effectState=ACTIVE&sortBy=effectState&sortDirection=desc&page=3&pageSize=50",
  );
});

test("Policy Rule catalogue query omits inactive filters", () => {
  assert.equal(
    serializePolicyRuleCatalogueQuery(
      toPolicyRuleCatalogueQuery(defaultPolicyRuleCatalogueQuery),
    ),
    "sortBy=policyRuleRef&sortDirection=asc&page=1&pageSize=25",
  );
});
