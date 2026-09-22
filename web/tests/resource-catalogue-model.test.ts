import assert from "node:assert/strict";
import test from "node:test";
import { toResourceCatalogueScreenModel } from "../src/features/resources/resourceCatalogueModel.ts";

test("Resource Catalogue Screen Model maps backend-confirmed page without adding capabilities", () => {
  const model = toResourceCatalogueScreenModel({
    items: [
      {
        resourceRef: "resource-1",
        displayName: "Edge gateway",
        authorityScopeRef: "scope-1",
        version: 3,
        current: {
          siteRef: "site-1",
          endpoints: [
            {
              endpointRef: "endpoint-1",
              address: { kind: "HOST", value: "edge.example.net" },
            },
          ],
          responsibilities: [
            { role: "OWNER", organizationRef: "org-1" },
          ],
        },
        history: {
          sites: [],
          endpointAddresses: [],
          responsibilities: [],
        },
      },
    ],
    total: 31,
    page: 2,
    pageSize: 25,
  });

  assert.deepEqual(model, {
    resources: [
      {
        resourceRef: "resource-1",
        displayName: "Edge gateway",
        authorityScopeRef: "scope-1",
        site: "site-1",
        endpoints: "HOST edge.example.net",
        responsibilities: "OWNER: org-1",
      },
    ],
    total: 31,
    page: 2,
    pageSize: 25,
  });
});
