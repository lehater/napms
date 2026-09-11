import { ApiError, request } from "@/lib/api"

export { ApiError } from "@/lib/api"
export {
  getConnectivityDecision,
  listConnectivityDecisionInteractions,
  listConnectivityDecisions,
  listConnectivityDecisionScopes,
  recordConnectivityDecision,
  type ConnectivityDecisionDetailResponse,
  type ConnectivityDecisionDto,
  type ConnectivityDecisionListPage,
  type ConnectivityDecisionOutcome,
  type DecisionEvidenceReferenceDto,
} from "@/features/decisions/api"
export {
  declareConnectivityRequirement,
  getConnectivityRequirement,
  getConnectivityRequirementAlignment,
  listConnectivityRequirementAlignment,
  listConnectivityRequirementInteractions,
  listConnectivityRequirements,
  listConnectivityRequirementScopes,
  retireConnectivityRequirement,
  setConnectivityRequirementApplicability,
  setConnectivityRequirementJustification,
  type ConnectivityRequirementDetailResponse,
  type ConnectivityRequirementDto,
  type ConnectivityRequirementListPage,
  type RequirementApplicability,
  type RequirementPolicyAlignmentDetail,
  type RequirementPolicyAlignmentItem,
  type RequirementPolicyAlignmentPage,
  type RequirementPolicyAlignmentStatus,
} from "@/features/requirements/api"

export type Actor = {
  actorId: string
  login: string
}

export type ProposalScope = {
  scope: string
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

export type RuleDto = {
  ruleId: string
  semanticIdentity: ProposalInteraction
  governanceScope: string
  operationalState: "Active" | "Inactive"
  effectiveWindow: { start: string; end: string } | null
  decisionReference: string | null
  catalogue?: CataloguePresentation | null
}

export type RuleStateTransition = {
  fromState: "Active" | "Inactive"
  toState: "Active" | "Inactive"
  actorId: string
  effectiveTime: string
  governanceScope: string
  authorityReference: string
}

export type RuleEffectiveWindowChange = {
  previousWindow: { start: string; end: string } | null
  newWindow: { start: string; end: string } | null
  actorId: string
  effectiveTime: string
  governanceScope: string
  authorityReference: string
}

export type RuleDetailDto = RuleDto & {
  proposalProvenance: {
    actorId: string
    effectiveTime: string
    authorityReference: string
    catalogueReference: string
  }
  stateHistory: RuleStateTransition[]
  effectiveWindowHistory: RuleEffectiveWindowChange[]
}

export type RuleDetailResponse = {
  rule: RuleDetailDto
  capabilities: {
    setOperationalState: "Permitted" | "Denied" | "Unknown"
    setEffectiveWindow: "Permitted" | "Denied" | "Unknown"
  }
}

export type RuleListPage = {
  items: RuleDto[]
  page: number
  pageSize: number
  hasMore: boolean
  ambiguousScopes: ProposalScope[]
}

export type ProposalResult =
  | { outcome: "Materialized" | "Resolved"; rule: RuleDto }
  | { outcome: "NotAllowed"; rule: null }

export async function login(login: string, password: string): Promise<Actor> {
  const result = await request<{ actor: Actor }>("/api/v1/session", {
    method: "POST",
    body: JSON.stringify({ login, password }),
  })
  return result.actor
}

export async function getSession(): Promise<Actor | null> {
  try {
    const result = await request<{ actor: Actor }>("/api/v1/session")
    return result.actor
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      return null
    }
    throw error
  }
}

export async function logout(): Promise<void> {
  await request<void>("/api/v1/session", { method: "DELETE" })
}

export async function listProposalScopes(): Promise<{
  scopes: ProposalScope[]
  ambiguousScopes: ProposalScope[]
}> {
  return request("/api/v1/access-rule-proposals/scopes")
}

export type ProposalInteractionPage = {
  items: ProposalInteraction[]
  page: number
  pageSize: number
  hasMore: boolean
}

export async function listProposalInteractions(
  scope: string,
  page: number,
  search?: string,
): Promise<ProposalInteractionPage> {
  const params = new URLSearchParams({
    scope,
    page: String(page),
    pageSize: "50",
  })
  if (search?.trim()) {
    params.set("search", search.trim())
  }
  return request<ProposalInteractionPage>(
    `/api/v1/access-rule-proposals/interactions?${params}`,
  )
}

export async function submitProposal(input: {
  authorityScope: string
  sourceComponentDeploymentId: string
  destinationComponentDeploymentId: string
  dcsContractRevisionId: string
}): Promise<ProposalResult> {
  return request("/api/v1/access-rule-proposals", {
    method: "POST",
    body: JSON.stringify(input),
  })
}

export async function listAccessRules(page: number): Promise<RuleListPage> {
  const params = new URLSearchParams({
    page: String(page),
    pageSize: "50",
  })
  return request<RuleListPage>(`/api/v1/access-rules?${params}`)
}

export async function getAccessRule(ruleId: string): Promise<RuleDetailResponse> {
  return request<RuleDetailResponse>(
    `/api/v1/access-rules/${encodeURIComponent(ruleId)}`,
  )
}

export async function setAccessRuleOperationalState(
  ruleId: string,
  targetState: "Active" | "Inactive",
): Promise<{
  outcome: "Updated" | "AlreadyInRequestedState"
  rule: RuleDto
}> {
  return request(
    `/api/v1/access-rules/${encodeURIComponent(ruleId)}/operational-state`,
    {
      method: "PATCH",
      body: JSON.stringify({ targetState }),
    },
  )
}

export async function setAccessRuleEffectiveWindow(
  ruleId: string,
  window: { start: string; end: string } | null,
): Promise<{
  outcome: "Updated" | "AlreadyInRequestedWindow"
  rule: RuleDto
}> {
  return request(
    `/api/v1/access-rules/${encodeURIComponent(ruleId)}/effective-window`,
    {
      method: "PATCH",
      body: JSON.stringify({ window }),
    },
  )
}

export async function listPolicyViewScopes(asOf: string): Promise<{
  scopes: ProposalScope[]
  ambiguousScopes: ProposalScope[]
}> {
  const params = new URLSearchParams({ asOf })
  return request(`/api/v1/policy-views/scopes?${params}`)
}

export type EffectivePolicyResponse = {
  scope: string
  asOf: string
  authorityReference: string
  rules: RuleDto[]
}

export async function getEffectiveDesiredPolicy(
  scope: string,
  asOf: string,
): Promise<EffectivePolicyResponse> {
  const params = new URLSearchParams({ scope, asOf })
  return request<EffectivePolicyResponse>(
    `/api/v1/effective-desired-policy?${params}`,
  )
}

export type PortConstraintDto = {
  kind: "Any" | "NotApplicable" | "Ranges"
  ranges?: { first: number; last: number }[]
}

export type NormalizedPolicyRow = {
  ruleId: string
  semanticIdentity: ProposalInteraction
  decisionReference: string | null
  governanceScope: string
  operationalState: "Active" | "Inactive"
  effectiveWindow: { start: string; end: string } | null
  snapshotAsOf: string
  readAuthorityReference: string
  source: {
    resourceReference: string
    endpointReference: string
    technicalAddress: string
    factReference: string
    validityReference: string
    provenanceReference: string
  }
  destination: {
    resourceReference: string
    endpointReference: string
    technicalAddress: string
    factReference: string
    validityReference: string
    provenanceReference: string
  }
  traffic: {
    protocol: string
    sourcePorts: PortConstraintDto
    destinationPorts: PortConstraintDto
    serviceReference: string | null
  }
  catalogue?: CataloguePresentation | null
  applicationCommunicationCatalogue: {
    factReference: string
    validityReference: string
    provenanceReference: string
  }
}

export type NormalizedPolicyResponse = {
  scope: string
  asOf: string
  authorityReference: string
  rows: NormalizedPolicyRow[]
}

export async function getNormalizedPolicy(
  scope: string,
  asOf: string,
): Promise<NormalizedPolicyResponse> {
  const params = new URLSearchParams({ scope, asOf })
  return request<NormalizedPolicyResponse>(
    `/api/v1/normalized-policy?${params}`,
  )
}

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
