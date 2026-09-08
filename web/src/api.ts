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
