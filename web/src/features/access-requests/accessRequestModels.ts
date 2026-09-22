import type { AccessRequestView, CataloguePage } from "../../app/api";

export type AccessRequestCatalogueItem = {
  requestRef: string;
  sourceDeploymentRef: string;
  destinationDeploymentRef: string;
  submittedAt: string;
  decisionResult: "ALLOWED" | "DENIED" | null;
};

export type AccessRequestCatalogueScreenModel = {
  requests: AccessRequestCatalogueItem[];
  total: number;
  page: number;
  pageSize: number;
};

export type AccessRequestDetailScreenModel = AccessRequestView;

export function toAccessRequestCatalogueScreenModel(
  page: CataloguePage<AccessRequestView>,
): AccessRequestCatalogueScreenModel {
  return {
    requests: page.items.map((request) => ({
      requestRef: request.requestRef,
      sourceDeploymentRef: request.sourceDeploymentRef,
      destinationDeploymentRef: request.destinationDeploymentRef,
      submittedAt: request.submittedAt,
      decisionResult: request.decisionResult,
    })),
    total: page.total,
    page: page.page,
    pageSize: page.pageSize,
  };
}
