import { DeploymentScreen } from "./DeploymentScreen";

export function DeploymentScreens({ create = false }: { create?: boolean }) {
  return <DeploymentScreen create={create} />;
}
