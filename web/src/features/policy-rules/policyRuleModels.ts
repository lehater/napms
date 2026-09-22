import type { CataloguePage, PolicyRuleView } from "../../app/api";

export type PolicyRuleCatalogueItem = {
  policyRuleRef: string;
  effectState: "ACTIVE" | "INACTIVE";
  sourceDeploymentRef: string;
  destinationDeploymentRef: string;
  interactionRevisionRef: string;
};

export type PolicyRuleCatalogueScreenModel = {
  rules: PolicyRuleCatalogueItem[];
  total: number;
  page: number;
  pageSize: number;
};

export type PolicyRuleDetailScreenModel = PolicyRuleView;

export function toPolicyRuleCatalogueScreenModel(
  page: CataloguePage<PolicyRuleView>,
): PolicyRuleCatalogueScreenModel {
  return {
    rules: page.items.map((rule) => ({
      policyRuleRef: rule.policyRuleRef,
      effectState: rule.effectState,
      sourceDeploymentRef: rule.sourceDeploymentRef,
      destinationDeploymentRef: rule.destinationDeploymentRef,
      interactionRevisionRef: rule.interactionRevisionRef,
    })),
    total: page.total,
    page: page.page,
    pageSize: page.pageSize,
  };
}
