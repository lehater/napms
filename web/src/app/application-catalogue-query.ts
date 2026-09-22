export type ApplicationSortField = "name" | "applicationRef";

export type ApplicationCatalogueQuery = {
  search?: string;
  componentRef?: string;
  sortBy: ApplicationSortField;
  sortDirection: "asc" | "desc";
  page: number;
  pageSize: number;
};

export function serializeApplicationCatalogueQuery(
  query: ApplicationCatalogueQuery,
): string {
  const params = new URLSearchParams();
  const search = query.search?.trim();
  const componentRef = query.componentRef?.trim();

  if (search) params.set("search", search);
  if (componentRef) params.set("componentRef", componentRef);

  params.set("sortBy", query.sortBy);
  params.set("sortDirection", query.sortDirection);
  params.set("page", String(query.page));
  params.set("pageSize", String(query.pageSize));
  return params.toString();
}
