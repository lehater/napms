import { request } from "@/lib/api"

type ProposalScope = { scope: string }

export type ScopedConnectivityResource = {
  resourceReference: string
  realizationState: "Resolved" | "Unresolved" | "Unknown"
  endpoints: {
    endpointReference: string
    technicalAddress: string
  }[]
}

export type ScopedConnectivityNeedSummary = {
  current: "Required" | "None" | "Unknown"
  historicalOnly: boolean | null
  coverage:
    | "Covered"
    | "Uncovered"
    | "NotCurrent"
    | "Unknown"
    | "NotApplicable"
}

export type ScopedConnectivityDecisionSummary = {
  state: "Allowed" | "NotAllowed" | "NoFinalDecision" | "Unknown"
}

export type ScopedConnectivityPolicySummary = {
  ruleExists: "Yes" | "No" | "Unknown"
  operationalState: "Active" | "Inactive" | "Unavailable"
  effectiveAtAsOf: "Yes" | "No" | "Unknown" | "Unavailable"
}

export type ScopedConnectivityRelationship = {
  semanticIdentity: {
    sourceComponentDeploymentId: string
    destinationComponentDeploymentId: string
    dcsContractRevisionId: string
  }
  direction: "Outgoing" | "Incoming"
  remoteComponent: {
    componentDeploymentId: string
    displayName: string | null
  }
  dcsDisplayName: string | null
  accessSummary: string | null
  remoteResourcesKnown: boolean
  remoteResources: ScopedConnectivityResource[]
  need: ScopedConnectivityNeedSummary
  decision: ScopedConnectivityDecisionSummary
  policy: ScopedConnectivityPolicySummary
}

export type ScopedConnectivityComponent = {
  componentDeploymentId: string
  displayName: string | null
  relationshipsKnown: boolean
  relationships: ScopedConnectivityRelationship[]
}

export type ScopedConnectivityResourceItem = {
  resource: ScopedConnectivityResource
  componentsKnown: boolean
  components: ScopedConnectivityComponent[]
}

export type ScopedConnectivityInventoryPage = {
  scope: string
  asOf: string
  items: ScopedConnectivityResourceItem[]
  page: number
  pageSize: number
  hasMore: boolean
  partial: boolean
}

export type ScopedConnectivityScopeResponse = {
  asOf: string
  scopes: ProposalScope[]
  ambiguousScopes: ProposalScope[]
}

export async function listScopedConnectivityScopes(
  asOf: string,
): Promise<ScopedConnectivityScopeResponse> {
  const params = new URLSearchParams({ asOf })
  return request<ScopedConnectivityScopeResponse>(
    `/api/v1/connectivity/scopes?${params}`,
  )
}

export async function getScopedConnectivityInventory(
  scope: string,
  asOf: string,
  page: number,
  search?: string,
): Promise<ScopedConnectivityInventoryPage> {
  const params = new URLSearchParams({
    scope,
    asOf,
    page: String(page),
    pageSize: "50",
  })
  if (search?.trim()) {
    params.set("search", search.trim())
  }
  return request<ScopedConnectivityInventoryPage>(
    `/api/v1/connectivity?${params}`,
  )
}
