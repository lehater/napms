import type { ProcessView } from "../src/app/api.ts";

export const process: ProcessView = {
  processRef: "process-1",
  name: "Order handling",
  description: "Business justification",
  criticalityLabel: "HIGH",
  organizationExternalReference: "ORG-1",
  organizationDisplayName: "Operations",
  version: 4,
  needs: [
    {
      needRef: "need-1",
      interactionRef: "interaction-1",
      participantComponentRef: "component-1",
      businessBasis: "Required for orders",
      status: "ACTIVE",
    },
  ],
};
