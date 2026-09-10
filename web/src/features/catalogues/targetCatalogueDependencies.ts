import type { DependencyReferenceDto } from "@/features/catalogues/targetCatalogueCommands"
import { TargetCatalogueApiError } from "@/features/catalogues/targetCatalogueCommands"

export type RetirementSubjectPath =
  | "application-definition"
  | "component"
  | "interaction-definition"
  | "application-deployment"
  | "deployment-interaction"

export type DependencyPage = {
  items: DependencyReferenceDto[]
  page: number
  pageSize: number
  total: number
  kind: string
  asOf: string
}

export async function listRetirementDependencyPage(input: {
  subjectKind: RetirementSubjectPath
  subjectId: string
  dependencyKind: string
  page: number
  pageSize?: number
}): Promise<DependencyPage> {
  const params = new URLSearchParams({
    page: String(input.page),
    pageSize: String(input.pageSize ?? 50),
  })
  const response = await fetch(
    `/api/v1/catalogues/retirement-dependencies/${input.subjectKind}/${encodeURIComponent(input.subjectId)}/${encodeURIComponent(input.dependencyKind)}?${params}`,
    {
      credentials: "same-origin",
      headers: { Accept: "application/json" },
    },
  )
  const payload = await response.json()
  if (!response.ok) {
    const error = payload?.error
    throw new TargetCatalogueApiError(
      response.status,
      error?.code ?? "HttpError",
      error?.message ?? "Dependencies could not be loaded.",
      error?.correlationId,
      error?.details,
    )
  }
  return payload as DependencyPage
}
