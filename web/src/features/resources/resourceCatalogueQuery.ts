import type {
  ResourceCatalogueQuery,
  ResourceSortField,
} from "../../app/resource-catalogue-query";

export type ResourceCatalogueQueryState = {
  search: string;
  authorityScopeRef: string;
  siteRef: string;
  sortBy: ResourceSortField;
  sortDirection: "asc" | "desc";
  page: number;
  pageSize: number;
};

export const defaultResourceCatalogueQuery: ResourceCatalogueQueryState = {
  search: "",
  authorityScopeRef: "",
  siteRef: "",
  sortBy: "displayName",
  sortDirection: "asc",
  page: 1,
  pageSize: 25,
};

export function toResourceCatalogueQuery(
  state: ResourceCatalogueQueryState,
): ResourceCatalogueQuery {
  return {
    ...(state.search.trim() ? { search: state.search } : {}),
    ...(state.authorityScopeRef.trim()
      ? { authorityScopeRef: state.authorityScopeRef }
      : {}),
    ...(state.siteRef.trim() ? { siteRef: state.siteRef } : {}),
    sortBy: state.sortBy,
    sortDirection: state.sortDirection,
    page: state.page,
    pageSize: state.pageSize,
  };
}
