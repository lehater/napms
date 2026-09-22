import type {
  ApplicationCatalogueQuery,
  ApplicationSortField,
} from "../../app/application-catalogue-query";

export type ApplicationCatalogueQueryState = {
  search: string;
  componentRef: string;
  sortBy: ApplicationSortField;
  sortDirection: "asc" | "desc";
  page: number;
  pageSize: number;
};

export const defaultApplicationCatalogueQuery: ApplicationCatalogueQueryState =
  {
    search: "",
    componentRef: "",
    sortBy: "name",
    sortDirection: "asc",
    page: 1,
    pageSize: 25,
  };

export function toApplicationCatalogueQuery(
  state: ApplicationCatalogueQueryState,
): ApplicationCatalogueQuery {
  return {
    ...(state.search.trim() ? { search: state.search } : {}),
    ...(state.componentRef.trim() ? { componentRef: state.componentRef } : {}),
    sortBy: state.sortBy,
    sortDirection: state.sortDirection,
    page: state.page,
    pageSize: state.pageSize,
  };
}
