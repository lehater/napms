import assert from "node:assert/strict";
import test from "node:test";
import {
  toApplicationCatalogueScreenModel,
  toApplicationDetailScreenModel,
} from "../src/features/applications/applicationModels.ts";

const application = {
  applicationRef: "application-1",
  name: "Payments",
  version: 3,
  components: [
    { componentRef: "component-1", name: "API" },
    { componentRef: "component-2", name: "Worker" },
  ],
  interactions: [
    {
      interactionRef: "interaction-1",
      sourceComponentRef: "component-1",
      destinationComponentRef: "component-2",
      purpose: "Process payment",
      version: 2,
      revisions: [
        {
          interactionRevisionRef: "revision-1",
          revisionNo: 1,
          trafficClauses: [
            {
              ipProtocol: 6,
              sourcePorts: [],
              destinationPorts: [{ from: 443, to: 443 }],
            },
          ],
          createdBySubject: "subject-1",
        },
      ],
    },
  ],
};

test("Application Catalogue Screen Model exposes stable application identity", () => {
  assert.deepEqual(toApplicationCatalogueScreenModel([application]), {
    applications: [
      {
        applicationRef: "application-1",
        name: "Payments",
      },
    ],
  });
});

test("Application Detail Screen Model preserves components and directed interactions", () => {
  const model = toApplicationDetailScreenModel(application);
  assert.equal(model.applicationRef, "application-1");
  assert.equal(model.version, 3);
  assert.deepEqual(model.components, application.components);
  assert.deepEqual(model.interactions, application.interactions);
});
