export type PolicyRuleSortField = "policyRuleRef" | "effectState";

export type PolicyRuleCatalogueQuery = {
  search?: string;
  sourceDeploymentRef?: string;
  destinationDeploymentRef?: string;
  effectState?: "ACTIVE" | "INACTIVE";
  sortBy: PolicyRuleSortField;
  sortDirection: "asc" | "desc";
  page: number;
  pageSize: number;
};

export function serializePolicyRuleCatalogueQuery(
  query: PolicyRuleCatalogueQuery,
): string {
  const params = new URLSearchParams();
  const search = query.search?.trim();
  const sourceDeploymentRef = query.sourceDeploymentRef?.trim();
  const destinationDeploymentRef = query.destinationDeploymentRef?.trim();

  if (search) params.set("search", search);
  if (sourceDeploymentRef) {
    params.set("sourceDeploymentRef", sourceDeploymentRef);
  }
  if (destinationDeploymentRef) {
    params.set("destinationDeploymentRef", destinationDeploymentRef);
  }
  if (query.effectState) params.set("effectState", query.effectState);
  params.set("sortBy", query.sortBy);
  params.set("sortDirection", query.sortDirection);
  params.set("page", String(query.page));
  params.set("pageSize", String(query.pageSize));
  return params.toString();
}
