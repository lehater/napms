import type { DeploymentView } from "../../app/api";

export type DeploymentScreenModel = {
  deployments: readonly {
    deploymentRef: string;
    componentRef: string;
    resourceRef: string;
  }[];
};

export function toDeploymentScreenModel(
  deployments: readonly DeploymentView[],
): DeploymentScreenModel {
  return {
    deployments: deployments.map((deployment) => ({
      deploymentRef: deployment.deploymentRef,
      componentRef: deployment.componentRef,
      resourceRef: deployment.resourceRef,
    })),
  };
}
