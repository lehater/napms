import { api } from "../../app/api";
import {
  type ResourceCatalogueScreenModel,
  toResourceCatalogueScreenModel,
} from "./resourceCatalogueModel";

export async function queryResourceCatalogue(): Promise<ResourceCatalogueScreenModel> {
  const resources = await api.listResources();
  return toResourceCatalogueScreenModel(resources);
}


export type CreateResourceInput = {
  displayName: string;
  authorityScopeRef: string;
  siteRef?: string;
};

export async function createResource(
  input: CreateResourceInput,
): Promise<string> {
  const created = await api.createResource(input);
  return created.resourceRef;
}
