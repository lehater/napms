import { api } from "../../app/api";
import {
  type DeploymentScreenModel,
  toDeploymentScreenModel,
} from "./deploymentModels";

export async function queryDeployments(): Promise<DeploymentScreenModel> {
  return toDeploymentScreenModel(await api.listDeployments());
}

export async function createDeployment(input: {
  componentRef: string;
  resourceRef: string;
}): Promise<void> {
  await api.createDeployment(input.componentRef, input.resourceRef);
}
