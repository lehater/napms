export type DecisionDraftContext = {
  scope: string
  sourceComponentDeploymentId: string
  destinationComponentDeploymentId: string
  dcsContractRevisionId: string
  supersedesDecisionId?: string
}
