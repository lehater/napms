import type { CataloguePage, ProcessView } from "../../app/api";

export type BusinessProcessCatalogueItem = {
  processRef: string;
  name: string;
  description: string | null;
  criticalityLabel: string | null;
  organizationExternalReference: string | null;
  organizationDisplayName: string | null;
};

export type BusinessProcessCatalogueScreenModel = {
  processes: BusinessProcessCatalogueItem[];
  total: number;
  page: number;
  pageSize: number;
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

export function toBusinessProcessCatalogueScreenModel(
  page: CataloguePage<ProcessView>,
): BusinessProcessCatalogueScreenModel {
  return {
    processes: page.items.map((process) => ({
      processRef: process.processRef,
      name: process.name,
      description: process.description,
      criticalityLabel: process.criticalityLabel,
      organizationExternalReference: process.organizationExternalReference,
      organizationDisplayName: process.organizationDisplayName,
    })),
    total: page.total,
    page: page.page,
    pageSize: page.pageSize,
  };
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
