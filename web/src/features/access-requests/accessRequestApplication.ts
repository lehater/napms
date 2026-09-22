import { api } from "../../app/api";
import {
  type AccessRequestCatalogueItem,
  type AccessRequestDetailScreenModel,
  toAccessRequestCatalogue,
} from "./accessRequestModels";

export async function queryAccessRequests(): Promise<
  AccessRequestCatalogueItem[]
> {
  return toAccessRequestCatalogue(await api.listAccessRequests());
}

export async function queryAccessRequest(
  requestRef: string,
): Promise<AccessRequestDetailScreenModel> {
  return api.getAccessRequest(requestRef);
}

export async function submitAccessRequest(input: {
  sourceDeploymentRef: string;
  destinationDeploymentRef: string;
  interactionRevisionRef: string;
  needRef: string;
}): Promise<string> {
  return (await api.submitAccessRequest(input)).requestRef;
}

export async function decideAccessRequest(
  model: AccessRequestDetailScreenModel,
  result: "ALLOWED" | "DENIED",
  externalDecisionRef?: string,
): Promise<{
  policyRuleRef?: string | null;
  request: AccessRequestDetailScreenModel;
}> {
  const decision = await api.decideAccessRequest(
    model.requestRef,
    model.version,
    result,
    externalDecisionRef,
  );
  return {
    policyRuleRef: decision.policyRuleRef,
    request: await queryAccessRequest(model.requestRef),
  };
}
