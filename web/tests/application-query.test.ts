import assert from "node:assert/strict";
import test from "node:test";
import { serializeApplicationCatalogueQuery } from "../src/app/application-catalogue-query.ts";
import {
  defaultApplicationCatalogueQuery,
  toApplicationCatalogueQuery,
} from "../src/features/applications/applicationCatalogueQuery.ts";

test("Application catalogue query serialization preserves accepted server semantics", () => {
  const query = toApplicationCatalogueQuery({
    ...defaultApplicationCatalogueQuery,
    search: "  payments  ",
    componentRef: "00000000-0000-0000-0000-000000000123",
    sortBy: "applicationRef",
    sortDirection: "desc",
    page: 3,
    pageSize: 50,
  });

  assert.equal(
    serializeApplicationCatalogueQuery(query),
    "search=payments&componentRef=00000000-0000-0000-0000-000000000123&sortBy=applicationRef&sortDirection=desc&page=3&pageSize=50",
  );
});

test("Application catalogue query omits inactive filters", () => {
  assert.equal(
    serializeApplicationCatalogueQuery(
      toApplicationCatalogueQuery(defaultApplicationCatalogueQuery),
    ),
    "sortBy=name&sortDirection=asc&page=1&pageSize=25",
  );
});
