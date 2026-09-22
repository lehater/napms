import type {
  AccessRequestCatalogueQuery,
  AccessRequestSortField,
} from "../../app/access-request-catalogue-query";

export type AccessRequestCatalogueQueryState = {
  search: string;
  sourceDeploymentRef: string;
  destinationDeploymentRef: string;
  decisionResult: "" | "ALLOWED" | "DENIED";
  sortBy: AccessRequestSortField;
  sortDirection: "asc" | "desc";
  page: number;
  pageSize: number;
};

export const defaultAccessRequestCatalogueQuery: AccessRequestCatalogueQueryState =
  {
    search: "",
    sourceDeploymentRef: "",
    destinationDeploymentRef: "",
    decisionResult: "",
    sortBy: "submittedAt",
    sortDirection: "asc",
    page: 1,
    pageSize: 25,
  };

export function toAccessRequestCatalogueQuery(
  state: AccessRequestCatalogueQueryState,
): AccessRequestCatalogueQuery {
  return {
    ...(state.search.trim() ? { search: state.search } : {}),
    ...(state.sourceDeploymentRef.trim()
      ? { sourceDeploymentRef: state.sourceDeploymentRef }
      : {}),
    ...(state.destinationDeploymentRef.trim()
      ? { destinationDeploymentRef: state.destinationDeploymentRef }
      : {}),
    ...(state.decisionResult ? { decisionResult: state.decisionResult } : {}),
    sortBy: state.sortBy,
    sortDirection: state.sortDirection,
    page: state.page,
    pageSize: state.pageSize,
  };
}
