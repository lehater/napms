import { ApiError } from "@/lib/api"
import type { ResourceDto } from "@/features/catalogues/api/catalogue"

export type ResourceWorkspaceDataState =
  | ""
  | "missing-address"
  | "missing-scope"
  | "missing-responsibility"

export type ResourceWorkspaceLifecycle = "active" | "retired" | "all"
export type ResourceWorkspaceSortBy = "name" | "reference" | "lifecycle"
export type ResourceWorkspaceSortDirection = "asc" | "desc"

export type ResourceWorkspaceItemDto = ResourceDto & {
  currentFacts: {
    hasRealization: boolean
    hasScopeAffiliation: boolean
    hasResponsibility: boolean
    hasContact: boolean
  }
  currentAddresses: string[]
  currentScopes: string[]
  technicalOwners: string[]
}

export type ResourceWorkspacePageDto = {
  items: ResourceWorkspaceItemDto[]
  page: number
  pageSize: number
  hasMore: boolean
  total: number
  counts: {
    all: number
    active: number
    retired: number
    missingAddress: number
    missingScope: number
    missingResponsibility: number
  }
  asOf: string
  responsibilityScope: string | null
  dataState: string | null
  lifecycle: ResourceWorkspaceLifecycle
  sortBy: ResourceWorkspaceSortBy
  sortDirection: ResourceWorkspaceSortDirection
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
  options: {
    pageSize?: number
    lifecycle?: ResourceWorkspaceLifecycle
    dataState?: ResourceWorkspaceDataState
    sortBy?: ResourceWorkspaceSortBy
    sortDirection?: ResourceWorkspaceSortDirection
  } = {},
): Promise<ResourceWorkspacePageDto> {
  const params = new URLSearchParams({
    page: String(page),
    pageSize: String(options.pageSize ?? 50),
    lifecycle: options.lifecycle ?? "active",
    sortBy: options.sortBy ?? "name",
    sortDirection: options.sortDirection ?? "asc",
  })
  if (search.trim()) params.set("search", search.trim())
  if (responsibilityScope.trim()) {
    params.set("responsibilityScope", responsibilityScope.trim())
  }
  if (options.dataState) params.set("dataState", options.dataState)
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
