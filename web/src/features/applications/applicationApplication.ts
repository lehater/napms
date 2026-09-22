import { api } from "../../app/api";
import {
  toApplicationCatalogueScreenModel,
  toApplicationDetailScreenModel,
  type ApplicationCatalogueScreenModel,
  type ApplicationDetailScreenModel,
} from "./applicationModels";
import { parseIpProtocol, parsePortRanges } from "./traffic";

export async function queryApplicationCatalogue(): Promise<ApplicationCatalogueScreenModel> {
  return toApplicationCatalogueScreenModel(await api.listApplications());
}

export async function createApplication(name: string): Promise<string> {
  const created = await api.createApplication(name);
  return created.applicationRef;
}

export async function queryApplicationDetail(
  applicationRef: string,
): Promise<ApplicationDetailScreenModel> {
  return toApplicationDetailScreenModel(await api.getApplication(applicationRef));
}

export async function addApplicationComponent(
  model: ApplicationDetailScreenModel,
  name: string,
): Promise<ApplicationDetailScreenModel> {
  await api.addComponent(model.applicationRef, model.version, name);
  return queryApplicationDetail(model.applicationRef);
}

export async function createApplicationInteraction(input: {
  sourceComponentRef: string;
  destinationComponentRef: string;
  purpose?: string;
}): Promise<string> {
  const created = await api.createInteraction(input);
  return created.interactionRef;
}

export async function queryInteractionVersion(
  interactionRef: string,
): Promise<number> {
  return (await api.getInteraction(interactionRef)).version;
}

export async function publishInteractionRevision(input: {
  interactionRef: string;
  version: number;
  protocol: string;
  sourcePorts: string;
  destinationPorts: string;
}): Promise<void> {
  await api.publishRevision(input.interactionRef, input.version, [
    {
      ipProtocol: parseIpProtocol(input.protocol),
      sourcePorts: parsePortRanges(input.sourcePorts),
      destinationPorts: parsePortRanges(input.destinationPorts),
    },
  ]);
}
