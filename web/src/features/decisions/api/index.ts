import type { CataloguePresentation, ProposalInteractionPage } from "@/features/catalogues/model/interaction"
import { request } from "@/lib/api"

type ProposalScope = { scope: string }

export type ConnectivityDecisionOutcome = "Allowed" | "NotAllowed"

export type DecisionEvidenceReferenceDto = {
  kind: string
  reference: string
}

export type ConnectivityDecisionDto = {
  decisionId: string
  governanceScope: string
  subject: {
    sourceComponentDeploymentId: string
    destinationComponentDeploymentId: string
    dcsContractRevisionId: string
  }
  outcome: ConnectivityDecisionOutcome
  validity: {
    validFrom: string
    validUntil: string | null
  }
  reason: {
    code: string
    text: string
  }
  evidenceReferences: DecisionEvidenceReferenceDto[]
  provenance: {
    actorId: string
    decidedAt: string
    authorityReference: string
  }
  supersedesDecisionId: string | null
  catalogue?: CataloguePresentation | null
}

export type ConnectivityDecisionListPage = {
  items: ConnectivityDecisionDto[]
  page: number
  pageSize: number
  hasMore: boolean
  ambiguousScopes: ProposalScope[]
}

export type ConnectivityDecisionDetailResponse = {
  decision: ConnectivityDecisionDto
  readAuthorityReference: string
}

export async function listConnectivityDecisionScopes(): Promise<{
  scopes: ProposalScope[]
  ambiguousScopes: ProposalScope[]
}> {
  return request("/api/v1/connectivity-decisions/scopes")
}

export async function listConnectivityDecisionInteractions(
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
    `/api/v1/connectivity-decisions/interactions?${params}`,
  )
}

export async function listConnectivityDecisions(
  page: number,
): Promise<ConnectivityDecisionListPage> {
  const params = new URLSearchParams({
    page: String(page),
    pageSize: "50",
  })
  return request<ConnectivityDecisionListPage>(
    `/api/v1/connectivity-decisions?${params}`,
  )
}

export async function getConnectivityDecision(
  decisionId: string,
): Promise<ConnectivityDecisionDetailResponse> {
  return request<ConnectivityDecisionDetailResponse>(
    `/api/v1/connectivity-decisions/${encodeURIComponent(decisionId)}`,
  )
}

export async function recordConnectivityDecision(input: {
  authorityScope: string
  sourceComponentDeploymentId: string
  destinationComponentDeploymentId: string
  dcsContractRevisionId: string
  outcome: ConnectivityDecisionOutcome
  validFrom: string
  validUntil: string | null
  reasonCode: string
  reasonText: string
  evidenceReferences: DecisionEvidenceReferenceDto[]
  supersedesDecisionId?: string | null
}): Promise<{
  outcome: "Recorded" | "Resolved"
  decision: ConnectivityDecisionDto
}> {
  return request("/api/v1/connectivity-decisions", {
    method: "POST",
    body: JSON.stringify(input),
  })
}
