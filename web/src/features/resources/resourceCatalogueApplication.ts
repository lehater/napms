import { api } from "../../app/api";
import {
  type ResourceCatalogueScreenModel,
  toResourceCatalogueScreenModel,
} from "./resourceCatalogueModel";

export async function queryResourceCatalogue(): Promise<ResourceCatalogueScreenModel> {
  const resources = await api.listResources();
  return toResourceCatalogueScreenModel(resources);
}
