import { DeploymentDetailScreen } from "./DeploymentDetailScreen";
import { DeploymentScreen } from "./DeploymentScreen";

export function DeploymentScreens({
  create = false,
  deploymentRef,
}: {
  create?: boolean;
  deploymentRef?: string;
}) {
  if (deploymentRef) {
    return <DeploymentDetailScreen deploymentRef={deploymentRef} />;
  }
  return <DeploymentScreen create={create} />;
}
