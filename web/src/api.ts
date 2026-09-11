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
export {
  getAccessRule,
  listAccessRules,
  setAccessRuleEffectiveWindow,
  setAccessRuleOperationalState,
  type RuleDetailDto,
  type RuleDetailResponse,
  type RuleEffectiveWindowChange,
  type RuleListPage,
  type RuleStateTransition,
} from "@/features/rules/api"
export {
  getEffectiveDesiredPolicy,
  getNormalizedPolicy,
  listPolicyViewScopes,
  type EffectivePolicyResponse,
  type NormalizedPolicyResponse,
  type NormalizedPolicyRow,
} from "@/features/policy/api"
export {
  getScopedConnectivityInventory,
  listScopedConnectivityScopes,
  type ScopedConnectivityComponent,
  type ScopedConnectivityDecisionSummary,
  type ScopedConnectivityInventoryPage,
  type ScopedConnectivityNeedSummary,
  type ScopedConnectivityPolicySummary,
  type ScopedConnectivityRelationship,
  type ScopedConnectivityResource,
  type ScopedConnectivityResourceItem,
  type ScopedConnectivityScopeResponse,
} from "@/features/connectivity/api"

export type Actor = {
  actorId: string
  login: string
}

export type ProposalScope = {
  scope: string
}

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

export type RuleDto = {
  ruleId: string
  semanticIdentity: ProposalInteraction
  governanceScope: string
  operationalState: "Active" | "Inactive"
  effectiveWindow: { start: string; end: string } | null
  decisionReference: string | null
  catalogue?: CataloguePresentation | null
}

export type ProposalResult =
  | { outcome: "Materialized" | "Resolved"; rule: RuleDto }
  | { outcome: "NotAllowed"; rule: null }

export type ProposalInteractionPage = {
  items: ProposalInteraction[]
  page: number
  pageSize: number
  hasMore: boolean
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
