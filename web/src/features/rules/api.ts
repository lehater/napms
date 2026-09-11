import type { RuleDto } from "@/features/rules/model/rule"
import { request } from "@/lib/api"

type ProposalScope = { scope: string }

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
