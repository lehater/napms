import type {
  DeploymentCatalogueQuery,
  DeploymentSortField,
} from "../../app/deployment-catalogue-query";

export type DeploymentCatalogueQueryState = {
  search: string;
  componentRef: string;
  resourceRef: string;
  sortBy: DeploymentSortField;
  sortDirection: "asc" | "desc";
  page: number;
  pageSize: number;
};

export const defaultDeploymentCatalogueQuery: DeploymentCatalogueQueryState = {
  search: "",
  componentRef: "",
  resourceRef: "",
  sortBy: "deploymentRef",
  sortDirection: "asc",
  page: 1,
  pageSize: 25,
};

export function toDeploymentCatalogueQuery(
  state: DeploymentCatalogueQueryState,
): DeploymentCatalogueQuery {
  return {
    ...(state.search.trim() ? { search: state.search } : {}),
    ...(state.componentRef.trim() ? { componentRef: state.componentRef } : {}),
    ...(state.resourceRef.trim() ? { resourceRef: state.resourceRef } : {}),
    sortBy: state.sortBy,
    sortDirection: state.sortDirection,
    page: state.page,
    pageSize: state.pageSize,
  };
}
