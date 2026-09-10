export type ResolutionState = "Resolved" | "Ambiguous" | "Unknown" | "Historical"
export type MatchKind = "Exact" | "CoversQuery" | "CoveredByQuery" | "Overlap" | "Unknown"

export type CheckerQuery = {
  sourceAddress: string
  destinationAddress: string
  protocol: string
  port: string
  asOf: string
}

export type ResourceCandidate = {
  resourceReference: string
  endpointReference: string
  technicalAddress: string
  componentNames: string[]
  responsibilityScope: string | null
  provenanceReferences: string[]
}

export type ResourceSide = {
  state: ResolutionState
  address: string
  candidates: ResourceCandidate[]
  responsibilities: Array<{
    resourceReference: string
    role: string
    party: string
    contact: string | null
  }>
}

export type PolicyMatch = {
  sourceComponent: string | null
  destinationComponent: string | null
  dcsReference: string | null
  dcsDisplayName: string | null
  accessSummary: string | null
  requirement: string
  decision: string
  rule: string
  effective: string
  scope: string | null
  partial: boolean
}

export type EvidenceEntry = {
  reference: string
  action: "Permit" | "Block" | "Unknown"
  normalized: string
  match: MatchKind
}

export type NetworkCandidate = {
  deviceReference: string
  logicalFirewallReference: string | null
  attachmentReference: string | null
  relevance: string | null
  provenanceReferences: string[]
  snapshot: null | {
    reference: string
    capturedAt: string | null
    recordedAt: string
    source: string
    entries: EvidenceEntry[]
  }
}

export type CheckerResult = {
  query: CheckerQuery
  source: ResourceSide
  destination: ResourceSide
  policyMatches: PolicyMatch[]
  networkContext: {
    completeForPair: boolean
    knowledgeGaps: string[]
    candidates: NetworkCandidate[]
  }
  findings: string[]
}

export const initialCheckerQuery: CheckerQuery = {
  sourceAddress: "10.10.10.10",
  destinationAddress: "10.20.20.20",
  protocol: "TCP",
  port: "443",
  asOf: new Date().toISOString(),
}
