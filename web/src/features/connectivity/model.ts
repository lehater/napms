export type RequestConnectivityContext = {
  scope: string
  dependentComponentDeploymentId: string
  sourceComponentDeploymentId: string
  destinationComponentDeploymentId: string
  dcsContractRevisionId: string
  needCurrent: "Required" | "None"
}
