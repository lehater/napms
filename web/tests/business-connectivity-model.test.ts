import assert from "node:assert/strict";
import test from "node:test";
import {
  toBusinessProcessCatalogueScreenModel,
  toBusinessProcessDetail,
} from "../src/features/business-connectivity/businessConnectivityModels.ts";
import { process } from "./business-connectivity-fixture.ts";

test("Business Process catalogue mapping preserves page and stable identity", () => {
  assert.deepEqual(
    toBusinessProcessCatalogueScreenModel({
      items: [process],
      total: 3,
      page: 2,
      pageSize: 1,
    }),
    {
      processes: [
        {
          processRef: "process-1",
          name: "Order handling",
          description: "Business justification",
          criticalityLabel: "HIGH",
          organizationExternalReference: "ORG-1",
          organizationDisplayName: "Operations",
        },
      ],
      total: 3,
      page: 2,
      pageSize: 1,
    },
  );
});

test("Business Process detail mapping preserves connectivity needs", () => {
  assert.deepEqual(toBusinessProcessDetail(process), process);
});
