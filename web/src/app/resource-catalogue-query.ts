export type ResourceSortField =
  | "displayName"
  | "resourceRef"
  | "authorityScopeRef";

export type ResourceCatalogueQuery = {
  search?: string;
  authorityScopeRef?: string;
  siteRef?: string;
  sortBy: ResourceSortField;
  sortDirection: "asc" | "desc";
  page: number;
  pageSize: number;
};

export function serializeResourceCatalogueQuery(
  query: ResourceCatalogueQuery,
): string {
  const params = new URLSearchParams();
  const search = query.search?.trim();
  const authorityScopeRef = query.authorityScopeRef?.trim();
  const siteRef = query.siteRef?.trim();

  if (search) params.set("search", search);
  if (authorityScopeRef) params.set("authorityScopeRef", authorityScopeRef);
  if (siteRef) params.set("siteRef", siteRef);

  params.set("sortBy", query.sortBy);
  params.set("sortDirection", query.sortDirection);
  params.set("page", String(query.page));
  params.set("pageSize", String(query.pageSize));
  return params.toString();
}
