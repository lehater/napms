export type AccessRequestSortField =
  | "submittedAt"
  | "requestRef"
  | "decisionResult";

export type AccessRequestCatalogueQuery = {
  search?: string;
  sourceDeploymentRef?: string;
  destinationDeploymentRef?: string;
  decisionResult?: "ALLOWED" | "DENIED";
  sortBy: AccessRequestSortField;
  sortDirection: "asc" | "desc";
  page: number;
  pageSize: number;
};

export function serializeAccessRequestCatalogueQuery(
  query: AccessRequestCatalogueQuery,
): string {
  const params = new URLSearchParams();
  const search = query.search?.trim();
  const sourceDeploymentRef = query.sourceDeploymentRef?.trim();
  const destinationDeploymentRef = query.destinationDeploymentRef?.trim();

  if (search) params.set("search", search);
  if (sourceDeploymentRef) {
    params.set("sourceDeploymentRef", sourceDeploymentRef);
  }
  if (destinationDeploymentRef) {
    params.set("destinationDeploymentRef", destinationDeploymentRef);
  }
  if (query.decisionResult) {
    params.set("decisionResult", query.decisionResult);
  }
  params.set("sortBy", query.sortBy);
  params.set("sortDirection", query.sortDirection);
  params.set("page", String(query.page));
  params.set("pageSize", String(query.pageSize));
  return params.toString();
}
