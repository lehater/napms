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
): Promise<ResourceHistoryDto> {
  const response = await fetch(
    `/api/v1/catalogues/resource-history/${encodeURIComponent(resourceReference)}`,
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
