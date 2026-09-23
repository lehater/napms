import assert from "node:assert/strict";
import test from "node:test";
import { serializeComponentCatalogueQuery } from "../src/app/component-catalogue-query.ts";
import { serializeInteractionCatalogueQuery } from "../src/app/interaction-catalogue-query.ts";
import { serializeResourceCatalogueQuery } from "../src/app/resource-catalogue-query.ts";
import {
  defaultResourceCatalogueQuery,
  toResourceCatalogueQuery,
} from "../src/features/resources/resourceCatalogueQuery.ts";

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
    serializeResourceCatalogueQuery(query),
    "search=edge+gateway&authorityScopeRef=scope-1&siteRef=site-1&sortBy=resourceRef&sortDirection=desc&page=3&pageSize=50",
  );
});

test("Resource catalogue query omits inactive filters", () => {
  assert.equal(
    serializeResourceCatalogueQuery(
      toResourceCatalogueQuery(defaultResourceCatalogueQuery),
    ),
    "sortBy=displayName&sortDirection=asc&page=1&pageSize=25",
  );
});

test("Component candidate query serializes server-backed search and paging", () => {
  assert.equal(
    serializeComponentCatalogueQuery({
      search: "payments api",
      page: 2,
      pageSize: 20,
    }),
    "search=payments+api&page=2&pageSize=20",
  );
});

test("Interaction candidate query serializes server-backed search and paging", () => {
  assert.equal(
    serializeInteractionCatalogueQuery({
      search: "identity flow",
      page: 1,
      pageSize: 20,
    }),
    "search=identity+flow&page=1&pageSize=20",
  );
});
