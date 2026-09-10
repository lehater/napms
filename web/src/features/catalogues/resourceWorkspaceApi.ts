import { ApiError } from "@/api"
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

async function request<T>(input: RequestInfo | URL): Promise<T> {
  const response = await fetch(input, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" },
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
