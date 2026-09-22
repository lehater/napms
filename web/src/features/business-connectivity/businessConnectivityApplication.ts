import { api } from "../../app/api";
import {
  type BusinessProcessCatalogueItem,
  type BusinessProcessDetailScreenModel,
  toBusinessProcessCatalogue,
  toBusinessProcessDetail,
} from "./businessConnectivityModels";

export async function queryBusinessProcesses(): Promise<
  BusinessProcessCatalogueItem[]
> {
  return toBusinessProcessCatalogue(await api.listProcesses());
}

export async function queryBusinessProcess(
  processRef: string,
): Promise<BusinessProcessDetailScreenModel> {
  return toBusinessProcessDetail(await api.getProcess(processRef));
}

export async function createBusinessProcess(input: {
  name: string;
  description?: string;
  criticalityLabel?: string;
}): Promise<string> {
  return (await api.createProcess(input)).processRef;
}

export async function setResponsibleOrganization(
  model: BusinessProcessDetailScreenModel,
  externalReference: string | null,
  displayName: string | null,
): Promise<BusinessProcessDetailScreenModel> {
  await api.setProcessResponsibleOrganization(
    model.processRef,
    model.version,
    externalReference,
    displayName,
  );
  return queryBusinessProcess(model.processRef);
}

export async function setBusinessProcessCriticality(
  model: BusinessProcessDetailScreenModel,
  criticalityLabel: string | null,
): Promise<BusinessProcessDetailScreenModel> {
  await api.setProcessCriticality(
    model.processRef,
    model.version,
    criticalityLabel,
  );
  return queryBusinessProcess(model.processRef);
}

export async function declareBusinessConnectivityNeed(
  model: BusinessProcessDetailScreenModel,
  input: {
    interactionRef: string;
    participantComponentRef: string;
    businessBasis: string;
  },
): Promise<BusinessProcessDetailScreenModel> {
  await api.declareNeed(model.processRef, model.version, input);
  return queryBusinessProcess(model.processRef);
}

export async function retireBusinessConnectivityNeed(
  model: BusinessProcessDetailScreenModel,
  needRef: string,
): Promise<BusinessProcessDetailScreenModel> {
  await api.retireNeed(model.processRef, needRef, model.version);
  return queryBusinessProcess(model.processRef);
}
