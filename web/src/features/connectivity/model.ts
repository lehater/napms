export type RequestConnectivityContext = {
  scope: string
  localResourceReference: string
  dependentComponentDeploymentId: string
  sourceComponentDeploymentId: string
  destinationComponentDeploymentId: string
  dcsContractRevisionId: string
  needCurrent: "Required" | "None"
}
