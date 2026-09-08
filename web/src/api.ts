export type Actor = {
  actorId: string
  login: string
}

export type ProposalScope = {
  scope: string
}

export type ProposalInteraction = {
  sourceComponentDeploymentId: string
  destinationComponentDeploymentId: string
  dcsContractRevisionId: string
}

export type RuleDto = {
  ruleId: string
  semanticIdentity: ProposalInteraction
  governanceScope: string
  operationalState: "Active" | "Inactive"
  effectiveWindow: { start: string; end: string } | null
  decisionReference: string | null
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

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
    public readonly correlationId?: string,
  ) {
    super(message)
  }
}

async function request<T>(input: RequestInfo | URL, init?: RequestInit): Promise<T> {
  const response = await fetch(input, {
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  })

  if (response.status === 204) {
    return undefined as T
  }

  const payload = await response.json()
  if (!response.ok) {
    const error = payload?.error
    throw new ApiError(
      response.status,
      error?.code ?? "HttpError",
      error?.message ?? "The operation could not be completed.",
      error?.correlationId,
    )
  }
  return payload as T
}

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
): Promise<ProposalInteractionPage> {
  const params = new URLSearchParams({
    scope,
    page: String(page),
    pageSize: "50",
  })
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
