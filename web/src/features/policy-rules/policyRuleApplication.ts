import { api } from "../../app/api";
import {
  type PolicyRuleCatalogueItem,
  type PolicyRuleDetailScreenModel,
  toPolicyRuleCatalogue,
} from "./policyRuleModels";

export async function queryPolicyRules(): Promise<PolicyRuleCatalogueItem[]> {
  return toPolicyRuleCatalogue(await api.listPolicyRules());
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
