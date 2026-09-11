import { ApiError } from "@/lib/api"
import type {
  ResourceDto,
  ResourceRealizationDto,
  ResourceResponsibilityDto,
  ResourceScopeAffiliationDto,
} from "@/features/catalogues/api/catalogue"

export type ResourceHistoryDto = {
  resource: ResourceDto
  asOf: string
  realizations: ResourceRealizationDto[]
  scopeAffiliations: ResourceScopeAffiliationDto[]
  responsibilities: ResourceResponsibilityDto[]
}

export async function readCatalogueResourceHistory(
  resourceReference: string,
  asOf?: string | null,
): Promise<ResourceHistoryDto> {
  const params = new URLSearchParams()
  if (asOf) params.set("asOf", asOf)
  const suffix = params.size > 0 ? `?${params}` : ""
  const response = await fetch(
    `/api/v1/catalogues/resource-history/${encodeURIComponent(resourceReference)}${suffix}`,
    { credentials: "same-origin" },
  )
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
  return payload as ResourceHistoryDto
}
