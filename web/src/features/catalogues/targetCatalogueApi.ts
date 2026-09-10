import { ApiError } from "@/api"

export type TargetPage<T> = {
  items: T[]
  page: number
  pageSize: number
  total: number
}

export type CatalogueLifecycleState = "Active" | "Retired"

export type ApplicationDefinitionDto = {
  applicationId: string
  displayName: string
  description: string | null
  domain: string | null
  ownerReference: string | null
  lifecycleState: CatalogueLifecycleState
  version: number
}

export type ApplicationDefinitionSummaryDto = ApplicationDefinitionDto & {
  componentCount: number
  interactionCount: number
  deploymentCount: number
}

export type ApplicationComponentDto = {
  componentId: string
  applicationId: string
  displayName: string
  componentType: string | null
  description: string | null
  lifecycleState: CatalogueLifecycleState
  version: number
}

export type PortConstraintDto = {
  kind: "Any" | "Ranges" | "NotApplicable"
  ranges?: Array<{ first: number; last: number }>
}

export type TrafficAlternativeDto = {
  protocol: string
  sourcePorts: PortConstraintDto
  destinationPorts: PortConstraintDto
  serviceReference: string | null
}

export type InteractionDefinitionSummaryDto = {
  interactionDefinitionId: string
  applicationId: string
  sourceComponentId: string
  destinationComponentId: string
  trafficAlternatives: TrafficAlternativeDto[]
  lifecycleState: CatalogueLifecycleState
  version: number
  sourceComponentName: string
  destinationComponentName: string
  activeDeploymentCount: number
}

export type ApplicationDeploymentDto = {
  applicationDeploymentId: string
  applicationId: string
  companyReference: string
  environment: string
  scopeReference: string
  lifecycleState: CatalogueLifecycleState
  version: number
}

export type ApplicationDeploymentSummaryDto = ApplicationDeploymentDto & {
  applicationName: string
  selectedInteractionCount: number
  definedInteractionCount: number
}

export type DeploymentConnectivityDto = {
  deploymentInteractionId: string
  interactionDefinitionId: string
  sourceComponent: {
    componentId: string
    displayName: string
    resourceCount: number
  }
  destinationComponent: {
    componentId: string
    displayName: string
    resourceCount: number
  }
  trafficAlternatives: TrafficAlternativeDto[]
}

export type DeploymentConnectivityPage = TargetPage<DeploymentConnectivityDto> & {
  asOf: string
}

type DefinitionResponse = { definition: ApplicationDefinitionDto }
type DeploymentResponse = {
  deployment: ApplicationDeploymentDto
  applicationName: string | null
}

async function request<T>(input: RequestInfo | URL): Promise<T> {
  const response = await fetch(input, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
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

function addOptional(params: URLSearchParams, key: string, value?: string | null) {
  const normalized = value?.trim()
  if (normalized) params.set(key, normalized)
}

export function listApplicationDefinitions(input: {
  page: number
  pageSize?: number
  search?: string
  domain?: string
  ownerReference?: string
  sort?: string
}): Promise<TargetPage<ApplicationDefinitionSummaryDto>> {
  const params = new URLSearchParams({
    page: String(input.page),
    pageSize: String(input.pageSize ?? 50),
    sort: input.sort ?? "name",
  })
  addOptional(params, "search", input.search)
  addOptional(params, "domain", input.domain)
  addOptional(params, "ownerReference", input.ownerReference)
  return request(`/api/v1/catalogues/application-definitions?${params}`)
}

export function readApplicationDefinition(
  applicationId: string,
): Promise<DefinitionResponse> {
  return request(
    `/api/v1/catalogues/application-definitions/${encodeURIComponent(applicationId)}`,
  )
}

export function listApplicationComponents(input: {
  applicationId: string
  page: number
  pageSize?: number
  search?: string
  componentType?: string
  sort?: string
}): Promise<TargetPage<ApplicationComponentDto>> {
  const params = new URLSearchParams({
    page: String(input.page),
    pageSize: String(input.pageSize ?? 50),
    sort: input.sort ?? "name",
  })
  addOptional(params, "search", input.search)
  addOptional(params, "componentType", input.componentType)
  return request(
    `/api/v1/catalogues/application-definitions/${encodeURIComponent(input.applicationId)}/components?${params}`,
  )
}

export function listInteractionDefinitions(input: {
  applicationId: string
  page: number
  pageSize?: number
  search?: string
  protocol?: string
  sort?: string
}): Promise<TargetPage<InteractionDefinitionSummaryDto>> {
  const params = new URLSearchParams({
    page: String(input.page),
    pageSize: String(input.pageSize ?? 50),
    sort: input.sort ?? "source",
  })
  addOptional(params, "search", input.search)
  addOptional(params, "protocol", input.protocol)
  return request(
    `/api/v1/catalogues/application-definitions/${encodeURIComponent(input.applicationId)}/interactions?${params}`,
  )
}

export function listApplicationDeployments(input: {
  page: number
  pageSize?: number
  applicationId?: string
  search?: string
  companyReference?: string
  environment?: string
  scopeReference?: string
  sort?: string
}): Promise<TargetPage<ApplicationDeploymentSummaryDto>> {
  const params = new URLSearchParams({
    page: String(input.page),
    pageSize: String(input.pageSize ?? 50),
    sort: input.sort ?? "application",
  })
  addOptional(params, "applicationId", input.applicationId)
  addOptional(params, "search", input.search)
  addOptional(params, "companyReference", input.companyReference)
  addOptional(params, "environment", input.environment)
  addOptional(params, "scopeReference", input.scopeReference)
  return request(`/api/v1/catalogues/application-deployments?${params}`)
}

export function readApplicationDeployment(
  applicationDeploymentId: string,
): Promise<DeploymentResponse> {
  return request(
    `/api/v1/catalogues/application-deployments/${encodeURIComponent(applicationDeploymentId)}`,
  )
}

export function listDeploymentConnectivity(input: {
  applicationDeploymentId: string
  page: number
  pageSize?: number
  search?: string
  protocol?: string
  sort?: string
  asOf?: string
}): Promise<DeploymentConnectivityPage> {
  const params = new URLSearchParams({
    page: String(input.page),
    pageSize: String(input.pageSize ?? 50),
    sort: input.sort ?? "source",
  })
  addOptional(params, "search", input.search)
  addOptional(params, "protocol", input.protocol)
  addOptional(params, "asOf", input.asOf)
  return request(
    `/api/v1/catalogues/application-deployments/${encodeURIComponent(input.applicationDeploymentId)}/connectivity?${params}`,
  )
}
