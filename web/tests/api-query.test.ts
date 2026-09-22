import assert from "node:assert/strict";
import test from "node:test";
import { serializeCatalogueQuery } from "../src/app/api.ts";
import {
  defaultResourceCatalogueQuery,
  toResourceCatalogueQuery,
} from "../src/features/resources/resourceCatalogueApplication.ts";

test("Resource catalogue query serialization preserves accepted server semantics", () => {
  const query = toResourceCatalogueQuery({
    ...defaultResourceCatalogueQuery,
    search: "  edge gateway  ",
    authorityScopeRef: "scope-1",
    siteRef: "site-1",
    sortBy: "resourceRef",
    sortDirection: "desc",
    page: 3,
    pageSize: 50,
  });

  assert.equal(
    serializeCatalogueQuery(query),
    "search=edge+gateway&authorityScopeRef=scope-1&siteRef=site-1&sortBy=resourceRef&sortDirection=desc&page=3&pageSize=50",
  );
});

test("Resource catalogue query omits inactive filters", () => {
  assert.equal(
    serializeCatalogueQuery(
      toResourceCatalogueQuery(defaultResourceCatalogueQuery),
    ),
    "sortBy=displayName&sortDirection=asc&page=1&pageSize=25",
  );
});
