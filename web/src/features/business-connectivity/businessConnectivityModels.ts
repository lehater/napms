import type { ProcessView } from "../../app/api";

export type BusinessProcessCatalogueItem = {
  processRef: string;
  name: string;
  description: string | null;
  criticalityLabel: string | null;
};

export type BusinessProcessDetailScreenModel = {
  processRef: string;
  name: string;
  description: string | null;
  criticalityLabel: string | null;
  organizationExternalReference: string | null;
  organizationDisplayName: string | null;
  version: number;
  needs: ProcessView["needs"];
};

export function toBusinessProcessCatalogue(
  processes: readonly ProcessView[],
): BusinessProcessCatalogueItem[] {
  return processes.map((process) => ({
    processRef: process.processRef,
    name: process.name,
    description: process.description,
    criticalityLabel: process.criticalityLabel,
  }));
}

export function toBusinessProcessDetail(
  process: ProcessView,
): BusinessProcessDetailScreenModel {
  return {
    processRef: process.processRef,
    name: process.name,
    description: process.description,
    criticalityLabel: process.criticalityLabel,
    organizationExternalReference: process.organizationExternalReference,
    organizationDisplayName: process.organizationDisplayName,
    version: process.version,
    needs: process.needs,
  };
}
