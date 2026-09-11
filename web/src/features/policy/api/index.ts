import type { CataloguePresentation, PortConstraintDto, ProposalInteraction } from "@/features/catalogues/model/interaction"
import type { RuleDto } from "@/features/rules/model/rule"
import { request } from "@/lib/api"

type ProposalScope = { scope: string }

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
