export type PortConstraintDto = {
  kind: "Any" | "NotApplicable" | "Ranges"
  ranges?: { first: number; last: number }[]
}

export type TrafficAlternativeDto = {
  protocol: string
  sourcePorts: PortConstraintDto
  destinationPorts: PortConstraintDto
  serviceReference: string | null
}

export type CataloguePresentation = {
  sourceDisplayName: string | null
  destinationDisplayName: string | null
  dcsDisplayName: string | null
  trafficAlternatives: TrafficAlternativeDto[]
  dcsProvenanceReference: string | null
}

export type ProposalInteraction = {
  sourceComponentDeploymentId: string
  destinationComponentDeploymentId: string
  dcsContractRevisionId: string
  catalogue?: CataloguePresentation | null
}

export type ProposalInteractionPage = {
  items: ProposalInteraction[]
  page: number
  pageSize: number
  hasMore: boolean
}
