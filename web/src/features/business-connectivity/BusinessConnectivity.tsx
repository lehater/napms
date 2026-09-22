import { BusinessConnectivityScreen } from "./BusinessConnectivityScreen";

export function BusinessConnectivity({
  create = false,
  processRef,
}: {
  create?: boolean;
  processRef?: string;
}) {
  return <BusinessConnectivityScreen create={create} processRef={processRef} />;
}
