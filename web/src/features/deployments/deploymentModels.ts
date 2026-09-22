import type { CataloguePage, DeploymentView } from "../../app/api";

export type DeploymentCatalogueItem = {
  deploymentRef: string;
  componentRef: string;
  resourceRef: string;
};

export type DeploymentScreenModel = {
  deployments: DeploymentCatalogueItem[];
  total: number;
  page: number;
  pageSize: number;
};

export type DeploymentDetailScreenModel = DeploymentCatalogueItem;

export function toDeploymentScreenModel(
  page: CataloguePage<DeploymentView>,
): DeploymentScreenModel {
  return {
    deployments: page.items.map((deployment) => ({
      deploymentRef: deployment.deploymentRef,
      componentRef: deployment.componentRef,
      resourceRef: deployment.resourceRef,
    })),
    total: page.total,
    page: page.page,
    pageSize: page.pageSize,
  };
}

export function toDeploymentDetailScreenModel(
  deployment: DeploymentView,
): DeploymentDetailScreenModel {
  return {
    deploymentRef: deployment.deploymentRef,
    componentRef: deployment.componentRef,
    resourceRef: deployment.resourceRef,
  };
}
