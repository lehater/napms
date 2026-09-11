import { ApiError } from "@/lib/api"
import type { ResourceDto } from "@/features/catalogues/catalogueApi"

export type ResourceWorkspaceItemDto = ResourceDto & {
  currentFacts: {
    hasRealization: boolean
    hasScopeAffiliation: boolean
    hasResponsibility: boolean
    hasContact: boolean
  }
}

export type ResourceWorkspacePageDto = {
  items: ResourceWorkspaceItemDto[]
  page: number
  pageSize: number
  hasMore: boolean
  asOf: string
  responsibilityScope: string | null
}

async function request<T>(input: RequestInfo | URL, init?: RequestInit): Promise<T> {
  const response = await fetch(input, {
    ...init,
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  })
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

function mutationHeaders(): HeadersInit {
  const key =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random()}`
  return { "Idempotency-Key": key }
}

export function listCatalogueResourceWorkspace(
  page = 1,
  search = "",
  responsibilityScope = "",
): Promise<ResourceWorkspacePageDto> {
  const params = new URLSearchParams({ page: String(page), pageSize: "50" })
  if (search.trim()) params.set("search", search.trim())
  if (responsibilityScope.trim()) {
    params.set("responsibilityScope", responsibilityScope.trim())
  }
  return request(`/api/v1/catalogues/resource-workspace?${params}`)
}

export async function renameCatalogueResource(
  resource: ResourceDto,
  displayName: string,
): Promise<ResourceDto> {
  const response = await request<{ resource: ResourceDto }>(
    `/api/v1/catalogues/resources/${encodeURIComponent(resource.resourceReference)}/rename`,
    {
      method: "POST",
      headers: mutationHeaders(),
      body: JSON.stringify({ displayName, expectedVersion: resource.version }),
    },
  )
  return response.resource
}

export async function retireCatalogueResource(
  resource: ResourceDto,
): Promise<ResourceDto> {
  const response = await request<{ resource: ResourceDto }>(
    `/api/v1/catalogues/resources/${encodeURIComponent(resource.resourceReference)}/retire`,
    {
      method: "POST",
      headers: mutationHeaders(),
      body: JSON.stringify({ expectedVersion: resource.version }),
    },
  )
  return response.resource
}
