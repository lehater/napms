export type InteractionCatalogueQuery = {
  search?: string;
  page: number;
  pageSize: number;
};

export function serializeInteractionCatalogueQuery(
  query: InteractionCatalogueQuery,
): string {
  const params = new URLSearchParams();
  if (query.search?.trim()) params.set("search", query.search.trim());
  params.set("page", String(query.page));
  params.set("pageSize", String(query.pageSize));
  return params.toString();
}
