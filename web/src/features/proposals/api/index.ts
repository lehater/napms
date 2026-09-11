import type { ProposalInteractionPage } from "@/features/catalogues/model/interaction"
import type { ProposalResult } from "@/features/proposals/model/result"
import { request } from "@/lib/api"

type ProposalScope = { scope: string }

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
  const params = new URLSearchParams({ scope, page: String(page), pageSize: "50" })
  if (search?.trim()) params.set("search", search.trim())
  return request(`/api/v1/access-rule-proposals/interactions?${params}`)
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
