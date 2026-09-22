import { api } from "../../app/api";
import {
  type PolicyRuleCatalogueQueryState,
  toPolicyRuleCatalogueQuery,
} from "./policyRuleCatalogueQuery";
import {
  type PolicyRuleCatalogueScreenModel,
  type PolicyRuleDetailScreenModel,
  toPolicyRuleCatalogueScreenModel,
} from "./policyRuleModels";

export async function queryPolicyRules(
  query: PolicyRuleCatalogueQueryState,
): Promise<PolicyRuleCatalogueScreenModel> {
  return toPolicyRuleCatalogueScreenModel(
    await api.listPolicyRules(toPolicyRuleCatalogueQuery(query)),
  );
}

export async function queryPolicyRule(
  policyRuleRef: string,
): Promise<PolicyRuleDetailScreenModel> {
  return api.getPolicyRule(policyRuleRef);
}

export async function setPolicyRuleEffectState(
  model: PolicyRuleDetailScreenModel,
): Promise<PolicyRuleDetailScreenModel> {
  await api.setPolicyRuleState(
    model.policyRuleRef,
    model.version,
    model.effectState === "ACTIVE" ? "INACTIVE" : "ACTIVE",
  );
  return queryPolicyRule(model.policyRuleRef);
}

export async function attachPolicyRuleJustification(
  model: PolicyRuleDetailScreenModel,
  needRef: string,
): Promise<PolicyRuleDetailScreenModel> {
  await api.attachPolicyRuleJustification(
    model.policyRuleRef,
    model.version,
    needRef,
  );
  return queryPolicyRule(model.policyRuleRef);
}
