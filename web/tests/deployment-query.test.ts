import assert from "node:assert/strict";
import test from "node:test";
import { serializeDeploymentCatalogueQuery } from "../src/app/deployment-catalogue-query.ts";
import {
  defaultDeploymentCatalogueQuery,
  toDeploymentCatalogueQuery,
} from "../src/features/deployments/deploymentCatalogueQuery.ts";

test("Deployment catalogue query serialization preserves accepted server semantics", () => {
  const query = toDeploymentCatalogueQuery({
    ...defaultDeploymentCatalogueQuery,
    search: "  0003  ",
    componentRef: "component-1",
    resourceRef: "resource-1",
    sortBy: "resourceRef",
    sortDirection: "desc",
    page: 3,
    pageSize: 50,
  });

  assert.equal(
    serializeDeploymentCatalogueQuery(query),
    "search=0003&componentRef=component-1&resourceRef=resource-1&sortBy=resourceRef&sortDirection=desc&page=3&pageSize=50",
  );
});

test("Deployment catalogue query omits inactive filters", () => {
  assert.equal(
    serializeDeploymentCatalogueQuery(
      toDeploymentCatalogueQuery(defaultDeploymentCatalogueQuery),
    ),
    "sortBy=deploymentRef&sortDirection=asc&page=1&pageSize=25",
  );
});
