import type { PolicyRuleView } from "../../app/api";

export type PolicyRuleCatalogueItem = {
  policyRuleRef: string;
  effectState: "ACTIVE" | "INACTIVE";
};

export type PolicyRuleDetailScreenModel = PolicyRuleView;

export function toPolicyRuleCatalogue(
  rules: readonly PolicyRuleView[],
): PolicyRuleCatalogueItem[] {
  return rules.map((rule) => ({
    policyRuleRef: rule.policyRuleRef,
    effectState: rule.effectState,
  }));
}
