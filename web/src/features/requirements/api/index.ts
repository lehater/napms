import type { CataloguePresentation, ProposalInteraction, ProposalInteractionPage } from "@/features/catalogues/model/interaction"
import { request } from "@/lib/api"

type ProposalScope = { scope: string }

export type RequirementApplicability =
  | { kind: "Ongoing" }
  | { kind: "AbsoluteWindow"; start: string; end: string }

export type ConnectivityRequirementDto = {
  requirementId: string
  governanceScope: string
  dependentComponentDeploymentId: string
  requiredInteraction: ProposalInteraction
  applicability: RequirementApplicability
  justification: string
  lifecycleState: "Active" | "Retired"
  version: number
  declarationProvenance: {
    actorId: string
    effectiveTime: string
    authorityReference: string
    catalogueReference: string | null
  }
  applicabilityHistory: {
    previousApplicability: RequirementApplicability
    newApplicability: RequirementApplicability
    actorId: string
    effectiveTime: string
    governanceScope: string
    authorityReference: string
  }[]
  justificationHistory: {
    previousJustification: string
    newJustification: string
    actorId: string
    effectiveTime: string
    governanceScope: string
    authorityReference: string
  }[]
  lifecycleHistory: {
    fromState: "Active"
    toState: "Retired"
    actorId: string
    effectiveTime: string
    governanceScope: string
    authorityReference: string
  }[]
  catalogue?: CataloguePresentation | null
}

export type ConnectivityRequirementListPage = {
  items: ConnectivityRequirementDto[]
  page: number
  pageSize: number
  hasMore: boolean
  ambiguousScopes: ProposalScope[]
}

export type ConnectivityRequirementDetailResponse = {
  requirement: ConnectivityRequirementDto
  capabilities: {
    setApplicability: "Permitted" | "Denied" | "Unknown"
    setJustification: "Permitted" | "Denied" | "Unknown"
    retire: "Permitted" | "Denied" | "Unknown"
  }
}

export async function listConnectivityRequirementScopes(): Promise<{
  scopes: ProposalScope[]
  ambiguousScopes: ProposalScope[]
}> {
  return request("/api/v1/connectivity-requirements/scopes")
}

export async function listConnectivityRequirementInteractions(
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
  return request(
    `/api/v1/connectivity-requirements/interactions?${params}`,
  )
}

export async function declareConnectivityRequirement(input: {
  authorityScope: string
  dependentComponentDeploymentId: string
  sourceComponentDeploymentId: string
  destinationComponentDeploymentId: string
  dcsContractRevisionId: string
  applicability: RequirementApplicability
  justification: string
}): Promise<{
  outcome: "Declared" | "Resolved"
  requirement: ConnectivityRequirementDto
}> {
  return request("/api/v1/connectivity-requirements", {
    method: "POST",
    body: JSON.stringify(input),
  })
}

export async function listConnectivityRequirements(
  page: number,
): Promise<ConnectivityRequirementListPage> {
  const params = new URLSearchParams({
    page: String(page),
    pageSize: "50",
  })
  return request(`/api/v1/connectivity-requirements?${params}`)
}

export async function getConnectivityRequirement(
  requirementId: string,
): Promise<ConnectivityRequirementDetailResponse> {
  return request(
    `/api/v1/connectivity-requirements/${encodeURIComponent(requirementId)}`,
  )
}

export async function setConnectivityRequirementApplicability(
  requirementId: string,
  applicability: RequirementApplicability,
): Promise<{
  outcome: "Updated" | "AlreadyInRequestedValue"
  requirement: ConnectivityRequirementDto
}> {
  return request(
    `/api/v1/connectivity-requirements/${encodeURIComponent(requirementId)}/applicability`,
    {
      method: "PATCH",
      body: JSON.stringify({ applicability }),
    },
  )
}

export async function setConnectivityRequirementJustification(
  requirementId: string,
  justification: string,
): Promise<{
  outcome: "Updated" | "AlreadyInRequestedValue"
  requirement: ConnectivityRequirementDto
}> {
  return request(
    `/api/v1/connectivity-requirements/${encodeURIComponent(requirementId)}/justification`,
    {
      method: "PATCH",
      body: JSON.stringify({ justification }),
    },
  )
}

export async function retireConnectivityRequirement(
  requirementId: string,
): Promise<{
  outcome: "Retired" | "AlreadyRetired"
  requirement: ConnectivityRequirementDto
}> {
  return request(
    `/api/v1/connectivity-requirements/${encodeURIComponent(requirementId)}/retirement`,
    { method: "POST" },
  )
}

export type RequirementPolicyAlignmentStatus =
  | "Covered"
  | "Uncovered"
  | "NotCurrent"
  | "Unknown"

export type RequirementPolicyAlignmentItem = {
  requirementId: string
  asOf?: string
  status: RequirementPolicyAlignmentStatus
  semanticIdentity: {
    sourceComponentDeploymentId: string
    destinationComponentDeploymentId: string
    dcsContractRevisionId: string
  }
}

export type RequirementPolicyAlignmentPage = {
  asOf: string
  items: RequirementPolicyAlignmentItem[]
  page: number
  pageSize: number
  hasMore: boolean
  ambiguousScopes: ProposalScope[]
}

export type RequirementPolicyAlignmentDetail =
  RequirementPolicyAlignmentItem & {
    asOf: string
    requirementReadAuthorityReference: string | null
  }

export async function listConnectivityRequirementAlignment(
  asOf: string,
  page: number,
): Promise<RequirementPolicyAlignmentPage> {
  const params = new URLSearchParams({
    asOf,
    page: String(page),
    pageSize: "50",
  })
  return request(
    `/api/v1/connectivity-requirements/alignment?${params}`,
  )
}

export async function getConnectivityRequirementAlignment(
  requirementId: string,
  asOf: string,
): Promise<RequirementPolicyAlignmentDetail> {
  const params = new URLSearchParams({ asOf })
  return request(
    `/api/v1/connectivity-requirements/${encodeURIComponent(requirementId)}/alignment?${params}`,
  )
}
