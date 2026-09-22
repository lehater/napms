import { api } from "../../app/api";
import {
  type ResourceCatalogueScreenModel,
  toResourceCatalogueScreenModel,
} from "./resourceCatalogueModel";
import {
  type ResourceCatalogueQueryState,
  toResourceCatalogueQuery,
} from "./resourceCatalogueQuery";

export async function queryResourceCatalogue(
  query: ResourceCatalogueQueryState,
): Promise<ResourceCatalogueScreenModel> {
  const resources = await api.listResources(toResourceCatalogueQuery(query));
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
