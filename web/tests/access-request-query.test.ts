import assert from "node:assert/strict";
import test from "node:test";
import { serializeAccessRequestCatalogueQuery } from "../src/app/access-request-catalogue-query.ts";
import {
  defaultAccessRequestCatalogueQuery,
  toAccessRequestCatalogueQuery,
} from "../src/features/access-requests/accessRequestCatalogueQuery.ts";

test("Access Request catalogue query serialization preserves accepted semantics", () => {
  const query = toAccessRequestCatalogueQuery({
    ...defaultAccessRequestCatalogueQuery,
    search: "  request-1  ",
    sourceDeploymentRef: "source-1",
    destinationDeploymentRef: "destination-1",
    decisionResult: "ALLOWED",
    sortBy: "requestRef",
    sortDirection: "desc",
    page: 3,
    pageSize: 50,
  });

  assert.equal(
    serializeAccessRequestCatalogueQuery(query),
    "search=request-1&sourceDeploymentRef=source-1&destinationDeploymentRef=destination-1&decisionResult=ALLOWED&sortBy=requestRef&sortDirection=desc&page=3&pageSize=50",
  );
});

test("Access Request catalogue query omits inactive filters", () => {
  assert.equal(
    serializeAccessRequestCatalogueQuery(
      toAccessRequestCatalogueQuery(defaultAccessRequestCatalogueQuery),
    ),
    "sortBy=submittedAt&sortDirection=asc&page=1&pageSize=25",
  );
});
