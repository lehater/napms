import { api } from "../../app/api";
import {
  type ResourceDetailScreenModel,
  toResourceDetailScreenModel,
} from "./resourceDetailModel";

export async function queryResourceDetail(
  resourceRef: string,
): Promise<ResourceDetailScreenModel> {
  return toResourceDetailScreenModel(await api.getResource(resourceRef));
}

export async function addResourceEndpoint(
  model: ResourceDetailScreenModel,
): Promise<ResourceDetailScreenModel> {
  return toResourceDetailScreenModel(
    await api.addResourceEndpoint(model.resourceRef, model.version),
  );
}

export async function setResourceSite(
  model: ResourceDetailScreenModel,
  siteRef: string | null,
): Promise<ResourceDetailScreenModel> {
  return toResourceDetailScreenModel(
    await api.setResourceSite(model.resourceRef, model.version, siteRef),
  );
}

export async function setResourceAddress(
  model: ResourceDetailScreenModel,
  endpointRef: string,
  address: { kind: string; value: string },
): Promise<ResourceDetailScreenModel> {
  return toResourceDetailScreenModel(
    await api.setResourceAddress(
      model.resourceRef,
      endpointRef,
      model.version,
      address,
    ),
  );
}

export async function clearResourceAddress(
  model: ResourceDetailScreenModel,
  endpointRef: string,
): Promise<ResourceDetailScreenModel> {
  await api.clearResourceAddress(model.resourceRef, endpointRef, model.version);
  return queryResourceDetail(model.resourceRef);
}

export async function setResourceResponsibility(
  model: ResourceDetailScreenModel,
  role: "OWNER" | "ADMINISTRATOR",
  organizationRef: string | null,
): Promise<ResourceDetailScreenModel> {
  return toResourceDetailScreenModel(
    await api.setResourceResponsibility(
      model.resourceRef,
      role,
      model.version,
      organizationRef,
    ),
  );
}
