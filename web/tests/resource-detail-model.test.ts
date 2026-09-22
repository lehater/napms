import assert from "node:assert/strict";
import test from "node:test";
import {
  hasEmptyCurrent,
  toResourceDetailScreenModel,
} from "../src/features/resources/resourceDetailModel.ts";

test("Resource Detail Screen Model preserves current/history truth without provider semantics", () => {
  const model = toResourceDetailScreenModel({
    resourceRef: "resource-1",
    displayName: "Edge gateway",
    authorityScopeRef: "scope-1",
    version: 4,
    current: {
      siteRef: "site-1",
      endpoints: [
        {
          endpointRef: "endpoint-1",
          address: { kind: "HOST", value: "edge.example.net" },
        },
      ],
      responsibilities: [{ role: "OWNER", organizationRef: "org-1" }],
    },
    history: {
      sites: [{ version: 1 }],
      endpointAddresses: [{ version: 2 }],
      responsibilities: [{ version: 3 }],
    },
  });

  assert.equal(hasEmptyCurrent(model), false);
  assert.deepEqual(model, {
    resourceRef: "resource-1",
    displayName: "Edge gateway",
    authorityScopeRef: "scope-1",
    version: 4,
    siteRef: "site-1",
    endpoints: [
      {
        endpointRef: "endpoint-1",
        addressSummary: "HOST edge.example.net",
      },
    ],
    responsibilities: [{ role: "OWNER", organizationRef: "org-1" }],
    history: {
      sites: [{ version: 1 }],
      endpointAddresses: [{ version: 2 }],
      responsibilities: [{ version: 3 }],
    },
  });
});

test("Resource Detail Screen Model exposes empty-current when a fact category is absent", () => {
  const model = toResourceDetailScreenModel({
    resourceRef: "resource-2",
    displayName: "Empty resource",
    authorityScopeRef: "scope-1",
    version: 1,
    current: {
      siteRef: null,
      endpoints: [],
      responsibilities: [],
    },
    history: {
      sites: [],
      endpointAddresses: [],
      responsibilities: [],
    },
  });

  assert.equal(hasEmptyCurrent(model), true);
});
