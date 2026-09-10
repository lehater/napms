import { ApiError } from "@/api"

export type CatalogueLifecycle = "Active" | "Retired"

export type ApplicationDto = {
  applicationId: string
  displayName: string
  lifecycle: CatalogueLifecycle
  version: number
  provenanceReference: string
  retirementProvenanceReference: string | null
}

export type ComponentDto = {
  componentId: string
  applicationId: string
  displayName: string
  lifecycle: CatalogueLifecycle
  version: number
  provenanceReference: string
  retirementProvenanceReference: string | null
}

export type ComponentDeploymentDto = {
  componentDeploymentId: string
  componentId: string
  displayName: string | null
  lifecycle: CatalogueLifecycle
  version: number
  provenanceReference: string
  retirementProvenanceReference: string | null
}

export type DeploymentResourceBindingDto = {
  bindingReference: string
  componentDeploymentId: string
  resourceReference: string
  validFrom: string
  validTo: string | null
  version: number
  provenanceReference: string
  endProvenanceReference: string | null
}

export type DcsRevisionSummaryDto = {
  revisionId: string
  sourceComponentDeploymentId: string
  destinationComponentDeploymentId: string
  displayName: string | null
  provenanceReference: string
}

export type ApplicationCatalogueParticipantDto = {
  applicationId: string
  applicationDisplayName: string
  componentId: string
  componentDisplayName: string
  componentDeploymentId: string
  deploymentDisplayName: string | null
}

export type ApplicationTreeDto = {
  application: ApplicationDto
  asOf: string
  components: Array<
    ComponentDto & {
      deployments: Array<
        ComponentDeploymentDto & {
          effectiveResourceBindings: DeploymentResourceBindingDto[]
          dcsRevisions: DcsRevisionSummaryDto[]
        }
      >
    }
  >
}

export type ResourceDto = {
  resourceReference: string
  displayName: string | null
  lifecycle: CatalogueLifecycle
  version: number
  provenanceReference: string
  retirementProvenanceReference: string | null
}

export type ResourceRealizationDto = {
  factReference: string
  resourceReference: string
  technicalAddresses: Array<{
    endpointReference: string
    technicalAddress: string
  }>
  validFrom: string
  validTo: string | null
  version: number
  provenanceReference: string
  endProvenanceReference: string | null
}

export type ResourceScopeAffiliationDto = {
  affiliationReference: string
  resourceReference: string
  responsibilityScope: string
  validFrom: string
  validTo: string | null
  version: number
  provenanceReference: string
  endProvenanceReference: string | null
}

export type ResourceResponsibilityDto = {
  assignmentReference: string
  resourceReference: string
  partyReference: string
  partyKind: "Person" | "Team"
  role: "ServiceOwner" | "TechnicalOwner" | "OperationsContact" | "BusinessOwner"
  displayName: string
  contact: string | null
  validFrom: string
  validTo: string | null
  version: number
  provenanceReference: string
  endProvenanceReference: string | null
}

export type ResourceDetailDto = {
  resource: ResourceDto
  asOf: string
  effectiveRealizations: ResourceRealizationDto[]
  effectiveScopeAffiliations: ResourceScopeAffiliationDto[]
  effectiveResponsibilities: ResourceResponsibilityDto[]
}

type Page<T> = {
  items: T[]
  page: number
  pageSize: number
  hasMore: boolean
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

export function listCatalogueApplications(
  page = 1,
  search = "",
): Promise<Page<ApplicationDto>> {
  const params = new URLSearchParams({ page: String(page), pageSize: "50" })
  if (search.trim()) params.set("search", search.trim())
  return request(`/api/v1/catalogues/applications?${params}`)
}

export function listCatalogueApplicationParticipants(
  page = 1,
  search = "",
): Promise<Page<ApplicationCatalogueParticipantDto>> {
  const params = new URLSearchParams({ page: String(page), pageSize: "200" })
  if (search.trim()) params.set("search", search.trim())
  return request(`/api/v1/catalogues/application-participants?${params}`)
}

export async function createCatalogueApplication(
  displayName: string,
): Promise<ApplicationDto> {
  const response = await request<{ application: ApplicationDto }>(
    "/api/v1/catalogues/applications",
    {
      method: "POST",
      headers: mutationHeaders(),
      body: JSON.stringify({ displayName }),
    },
  )
  return response.application
}

export function readCatalogueApplication(
  applicationId: string,
): Promise<ApplicationTreeDto> {
  return request(`/api/v1/catalogues/applications/${encodeURIComponent(applicationId)}`)
}

export async function createCatalogueComponent(
  applicationId: string,
  displayName: string,
): Promise<ComponentDto> {
  const response = await request<{ component: ComponentDto }>(
    `/api/v1/catalogues/applications/${encodeURIComponent(applicationId)}/components`,
    {
      method: "POST",
      headers: mutationHeaders(),
      body: JSON.stringify({ displayName }),
    },
  )
  return response.component
}

export async function createCatalogueDeployment(
  componentId: string,
  displayName: string | null,
): Promise<ComponentDeploymentDto> {
  const response = await request<{ deployment: ComponentDeploymentDto }>(
    `/api/v1/catalogues/components/${encodeURIComponent(componentId)}/deployments`,
    {
      method: "POST",
      headers: mutationHeaders(),
      body: JSON.stringify({ displayName: displayName || null }),
    },
  )
  return response.deployment
}

export async function createCatalogueDeploymentResourceBinding(
  deploymentId: string,
  resourceReference: string,
  validFrom: string,
): Promise<DeploymentResourceBindingDto> {
  const response = await request<{ binding: DeploymentResourceBindingDto }>(
    `/api/v1/catalogues/deployments/${encodeURIComponent(deploymentId)}/resource-bindings`,
    {
      method: "POST",
      headers: mutationHeaders(),
      body: JSON.stringify({ resourceReference, validFrom, validTo: null }),
    },
  )
  return response.binding
}

export async function endCatalogueDeploymentResourceBinding(
  binding: DeploymentResourceBindingDto,
  validTo: string,
): Promise<DeploymentResourceBindingDto> {
  const response = await request<{ binding: DeploymentResourceBindingDto }>(
    `/api/v1/catalogues/deployment-resource-bindings/${encodeURIComponent(binding.bindingReference)}/end`,
    {
      method: "POST",
      headers: mutationHeaders(),
      body: JSON.stringify({ validTo, expectedVersion: binding.version }),
    },
  )
  return response.binding
}

export async function createCatalogueDcsRevision(input: {
  sourceComponentDeploymentId: string
  destinationComponentDeploymentId: string
  displayName: string | null
  protocol: "tcp" | "udp"
  destinationPort: number
  serviceReference: string | null
}): Promise<DcsRevisionSummaryDto> {
  const response = await request<{ dcsRevision: DcsRevisionSummaryDto }>(
    "/api/v1/catalogues/dcs-revisions",
    {
      method: "POST",
      headers: mutationHeaders(),
      body: JSON.stringify({
        sourceComponentDeploymentId: input.sourceComponentDeploymentId,
        destinationComponentDeploymentId: input.destinationComponentDeploymentId,
        displayName: input.displayName,
        trafficAlternatives: [
          {
            protocol: input.protocol,
            sourcePorts: { kind: "Any", ranges: [] },
            destinationPorts: {
              kind: "Ranges",
              ranges: [
                { first: input.destinationPort, last: input.destinationPort },
              ],
            },
            serviceReference: input.serviceReference,
          },
        ],
      }),
    },
  )
  return response.dcsRevision
}

export function listCatalogueResources(
  page = 1,
  search = "",
): Promise<Page<ResourceDto>> {
  const params = new URLSearchParams({ page: String(page), pageSize: "50" })
  if (search.trim()) params.set("search", search.trim())
  return request(`/api/v1/catalogues/resources?${params}`)
}

export async function createCatalogueResource(
  displayName: string | null,
): Promise<ResourceDto> {
  const response = await request<{ resource: ResourceDto }>(
    "/api/v1/catalogues/resources",
    {
      method: "POST",
      headers: mutationHeaders(),
      body: JSON.stringify({ displayName: displayName || null }),
    },
  )
  return response.resource
}

export function readCatalogueResource(
  resourceReference: string,
): Promise<ResourceDetailDto> {
  return request(
    `/api/v1/catalogues/resources/${encodeURIComponent(resourceReference)}`,
  )
}

export async function createCatalogueResourceRealization(
  resourceReference: string,
  technicalAddresses: string[],
  validFrom: string,
): Promise<ResourceRealizationDto> {
  const response = await request<{ realization: ResourceRealizationDto }>(
    `/api/v1/catalogues/resources/${encodeURIComponent(resourceReference)}/realizations`,
    {
      method: "POST",
      headers: mutationHeaders(),
      body: JSON.stringify({
        technicalAddresses,
        validFrom,
        validTo: null,
      }),
    },
  )
  return response.realization
}

export async function replaceCatalogueResourceRealization(
  realization: ResourceRealizationDto,
  technicalAddresses: string[],
  validFrom: string,
): Promise<ResourceRealizationDto> {
  const response = await request<{ realization: ResourceRealizationDto }>(
    `/api/v1/catalogues/resource-realizations/${encodeURIComponent(realization.factReference)}/replacement`,
    {
      method: "POST",
      headers: mutationHeaders(),
      body: JSON.stringify({
        technicalAddresses,
        validFrom,
        validTo: null,
        expectedVersion: realization.version,
      }),
    },
  )
  return response.realization
}

export async function createCatalogueResourceScopeAffiliation(
  resourceReference: string,
  responsibilityScope: string,
  validFrom: string,
): Promise<ResourceScopeAffiliationDto> {
  const response = await request<{ scopeAffiliation: ResourceScopeAffiliationDto }>(
    `/api/v1/catalogues/resources/${encodeURIComponent(resourceReference)}/scope-affiliations`,
    {
      method: "POST",
      headers: mutationHeaders(),
      body: JSON.stringify({ responsibilityScope, validFrom, validTo: null }),
    },
  )
  return response.scopeAffiliation
}

export async function endCatalogueResourceScopeAffiliation(
  affiliation: ResourceScopeAffiliationDto,
  validTo: string,
): Promise<ResourceScopeAffiliationDto> {
  const response = await request<{ scopeAffiliation: ResourceScopeAffiliationDto }>(
    `/api/v1/catalogues/resource-scope-affiliations/${encodeURIComponent(affiliation.affiliationReference)}/end`,
    {
      method: "POST",
      headers: mutationHeaders(),
      body: JSON.stringify({ validTo, expectedVersion: affiliation.version }),
    },
  )
  return response.scopeAffiliation
}

export async function createCatalogueResourceResponsibility(
  resourceReference: string,
  input: {
    partyReference: string
    partyKind: "Person" | "Team"
    role: "ServiceOwner" | "TechnicalOwner" | "OperationsContact" | "BusinessOwner"
    displayName: string
    contact: string | null
    validFrom: string
  },
): Promise<ResourceResponsibilityDto> {
  const response = await request<{ responsibility: ResourceResponsibilityDto }>(
    `/api/v1/catalogues/resources/${encodeURIComponent(resourceReference)}/responsibilities`,
    {
      method: "POST",
      headers: mutationHeaders(),
      body: JSON.stringify({ ...input, validTo: null }),
    },
  )
  return response.responsibility
}

export async function endCatalogueResourceResponsibility(
  responsibility: ResourceResponsibilityDto,
  validTo: string,
): Promise<ResourceResponsibilityDto> {
  const response = await request<{ responsibility: ResourceResponsibilityDto }>(
    `/api/v1/catalogues/resource-responsibilities/${encodeURIComponent(responsibility.assignmentReference)}/end`,
    {
      method: "POST",
      headers: mutationHeaders(),
      body: JSON.stringify({ validTo, expectedVersion: responsibility.version }),
    },
  )
  return response.responsibility
}
