export type DeploymentSortField =
  | "deploymentRef"
  | "componentRef"
  | "resourceRef";

export type DeploymentCatalogueQuery = {
  search?: string;
  componentRef?: string;
  resourceRef?: string;
  sortBy: DeploymentSortField;
  sortDirection: "asc" | "desc";
  page: number;
  pageSize: number;
};

export function serializeDeploymentCatalogueQuery(
  query: DeploymentCatalogueQuery,
): string {
  const params = new URLSearchParams();
  const search = query.search?.trim();
  const componentRef = query.componentRef?.trim();
  const resourceRef = query.resourceRef?.trim();

  if (search) params.set("search", search);
  if (componentRef) params.set("componentRef", componentRef);
  if (resourceRef) params.set("resourceRef", resourceRef);

  params.set("sortBy", query.sortBy);
  params.set("sortDirection", query.sortDirection);
  params.set("page", String(query.page));
  params.set("pageSize", String(query.pageSize));
  return params.toString();
}
