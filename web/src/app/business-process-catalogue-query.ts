export type BusinessProcessSortField =
  | "name"
  | "processRef"
  | "criticalityLabel";

export type BusinessProcessCatalogueQuery = {
  search?: string;
  criticalityLabel?: string;
  organizationExternalReference?: string;
  sortBy: BusinessProcessSortField;
  sortDirection: "asc" | "desc";
  page: number;
  pageSize: number;
};

export function serializeBusinessProcessCatalogueQuery(
  query: BusinessProcessCatalogueQuery,
): string {
  const params = new URLSearchParams();
  const search = query.search?.trim();
  const criticalityLabel = query.criticalityLabel?.trim();
  const organizationExternalReference =
    query.organizationExternalReference?.trim();

  if (search) params.set("search", search);
  if (criticalityLabel) params.set("criticalityLabel", criticalityLabel);
  if (organizationExternalReference) {
    params.set("organizationExternalReference", organizationExternalReference);
  }
  params.set("sortBy", query.sortBy);
  params.set("sortDirection", query.sortDirection);
  params.set("page", String(query.page));
  params.set("pageSize", String(query.pageSize));
  return params.toString();
}
