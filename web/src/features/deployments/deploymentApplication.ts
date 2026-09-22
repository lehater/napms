import { api } from "../../app/api";
import {
  type DeploymentCatalogueQueryState,
  toDeploymentCatalogueQuery,
} from "./deploymentCatalogueQuery";
import {
  type DeploymentDetailScreenModel,
  type DeploymentScreenModel,
  toDeploymentDetailScreenModel,
  toDeploymentScreenModel,
} from "./deploymentModels";

export async function queryDeployments(
  query: DeploymentCatalogueQueryState,
): Promise<DeploymentScreenModel> {
  return toDeploymentScreenModel(
    await api.listDeployments(toDeploymentCatalogueQuery(query)),
  );
}

export async function queryDeploymentDetail(
  deploymentRef: string,
): Promise<DeploymentDetailScreenModel> {
  return toDeploymentDetailScreenModel(await api.getDeployment(deploymentRef));
}

export async function createDeployment(input: {
  componentRef: string;
  resourceRef: string;
}): Promise<string> {
  const created = await api.createDeployment(
    input.componentRef,
    input.resourceRef,
  );
  return created.deploymentRef;
}
