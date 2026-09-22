import type {
  PolicyRuleCatalogueQuery,
  PolicyRuleSortField,
} from "../../app/policy-rule-catalogue-query";

export type PolicyRuleCatalogueQueryState = {
  search: string;
  sourceDeploymentRef: string;
  destinationDeploymentRef: string;
  effectState: "" | "ACTIVE" | "INACTIVE";
  sortBy: PolicyRuleSortField;
  sortDirection: "asc" | "desc";
  page: number;
  pageSize: number;
};

export const defaultPolicyRuleCatalogueQuery: PolicyRuleCatalogueQueryState = {
  search: "",
  sourceDeploymentRef: "",
  destinationDeploymentRef: "",
  effectState: "",
  sortBy: "policyRuleRef",
  sortDirection: "asc",
  page: 1,
  pageSize: 25,
};

export function toPolicyRuleCatalogueQuery(
  state: PolicyRuleCatalogueQueryState,
): PolicyRuleCatalogueQuery {
  return {
    ...(state.search.trim() ? { search: state.search } : {}),
    ...(state.sourceDeploymentRef.trim()
      ? { sourceDeploymentRef: state.sourceDeploymentRef }
      : {}),
    ...(state.destinationDeploymentRef.trim()
      ? { destinationDeploymentRef: state.destinationDeploymentRef }
      : {}),
    ...(state.effectState ? { effectState: state.effectState } : {}),
    sortBy: state.sortBy,
    sortDirection: state.sortDirection,
    page: state.page,
    pageSize: state.pageSize,
  };
}
