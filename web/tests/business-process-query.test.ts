import assert from "node:assert/strict";
import test from "node:test";
import { serializeBusinessProcessCatalogueQuery } from "../src/app/business-process-catalogue-query.ts";
import {
  defaultBusinessProcessCatalogueQuery,
  toBusinessProcessCatalogueQuery,
} from "../src/features/business-connectivity/businessProcessCatalogueQuery.ts";

test("Business Process catalogue query serialization preserves accepted server semantics", () => {
  const query = toBusinessProcessCatalogueQuery({
    ...defaultBusinessProcessCatalogueQuery,
    search: "  Orders  ",
    criticalityLabel: "HIGH",
    organizationExternalReference: "ORG-1",
    sortBy: "criticalityLabel",
    sortDirection: "desc",
    page: 3,
    pageSize: 50,
  });

  assert.equal(
    serializeBusinessProcessCatalogueQuery(query),
    "search=Orders&criticalityLabel=HIGH&organizationExternalReference=ORG-1&sortBy=criticalityLabel&sortDirection=desc&page=3&pageSize=50",
  );
});

test("Business Process catalogue query omits inactive filters", () => {
  assert.equal(
    serializeBusinessProcessCatalogueQuery(
      toBusinessProcessCatalogueQuery(defaultBusinessProcessCatalogueQuery),
    ),
    "sortBy=name&sortDirection=asc&page=1&pageSize=25",
  );
});
