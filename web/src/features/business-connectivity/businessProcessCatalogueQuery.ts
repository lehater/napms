import type {
  BusinessProcessCatalogueQuery,
  BusinessProcessSortField,
} from "../../app/business-process-catalogue-query";

export type BusinessProcessCatalogueQueryState = {
  search: string;
  criticalityLabel: string;
  organizationExternalReference: string;
  sortBy: BusinessProcessSortField;
  sortDirection: "asc" | "desc";
  page: number;
  pageSize: number;
};

export const defaultBusinessProcessCatalogueQuery: BusinessProcessCatalogueQueryState =
  {
    search: "",
    criticalityLabel: "",
    organizationExternalReference: "",
    sortBy: "name",
    sortDirection: "asc",
    page: 1,
    pageSize: 25,
  };

export function toBusinessProcessCatalogueQuery(
  state: BusinessProcessCatalogueQueryState,
): BusinessProcessCatalogueQuery {
  return {
    ...(state.search.trim() ? { search: state.search } : {}),
    ...(state.criticalityLabel.trim()
      ? { criticalityLabel: state.criticalityLabel }
      : {}),
    ...(state.organizationExternalReference.trim()
      ? { organizationExternalReference: state.organizationExternalReference }
      : {}),
    sortBy: state.sortBy,
    sortDirection: state.sortDirection,
    page: state.page,
    pageSize: state.pageSize,
  };
}
