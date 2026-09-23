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
      sourceComponentName: "API",
      destinationComponentRef: "component-2",
      destinationComponentName: "Worker",
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

test("Application Catalogue Screen Model preserves page and stable identity", () => {
  assert.deepEqual(
    toApplicationCatalogueScreenModel({
      items: [application],
      total: 17,
      page: 2,
      pageSize: 10,
    }),
    {
      applications: [
        {
          applicationRef: "application-1",
          name: "Payments",
          components: "API, Worker",
        },
      ],
      total: 17,
      page: 2,
      pageSize: 10,
    },
  );
});

test("Application Detail Screen Model preserves components and directed interactions", () => {
  const model = toApplicationDetailScreenModel(application);
  assert.equal(model.applicationRef, "application-1");
  assert.equal(model.version, 3);
  assert.deepEqual(model.components, application.components);
  assert.deepEqual(model.interactions, application.interactions);
});
