import { ApiError } from "@/lib/api"
import type { TrafficAlternativeDto } from "@/features/catalogues/model/interaction"
import type {
  ApplicationComponentDto,
  ApplicationDefinitionDto,
  ApplicationDeploymentDto,
  CatalogueLifecycleState,
  DeploymentInteractionSide,
} from "@/features/catalogues/targetCatalogueApi"

export type DependencyReferenceDto = {
  reference: string
  displayName: string | null
}

export type DependencyGroupDto = {
  kind: string
  count: number
  preview: DependencyReferenceDto[]
}

export class TargetCatalogueApiError extends ApiError {
  constructor(
    status: number,
    code: string,
    message: string,
    correlationId?: string,
    public readonly details?: { dependencies?: DependencyGroupDto[] },
  ) {
    super(status, code, message, correlationId)
  }
}

export type InteractionDefinitionDto = {
  interactionDefinitionId: string
  applicationId: string
  sourceComponentId: string
  destinationComponentId: string
  trafficAlternatives: TrafficAlternativeDto[]
  lifecycleState: CatalogueLifecycleState
  version: number
}

export type BindingDto = {
  bindingReference: string
  deploymentInteractionId: string
  side: DeploymentInteractionSide
  resourceReference: string
  validFrom: string
  validTo: string | null
  version: number
}

async function command<T>(input: RequestInfo | URL, body: object): Promise<T> {
  const key =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random()}`
  const response = await fetch(input, {
    method: "POST",
    credentials: "same-origin",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      "Idempotency-Key": key,
    },
    body: JSON.stringify(body),
  })
  const payload = await response.json()
  if (!response.ok) {
    const error = payload?.error
    throw new TargetCatalogueApiError(
      response.status,
      error?.code ?? "HttpError",
      error?.message ?? "The operation could not be completed.",
      error?.correlationId,
      error?.details,
    )
  }
  return payload as T
}

export async function createInteractionDefinition(
  applicationId: string,
  input: {
    sourceComponentId: string
    destinationComponentId: string
    trafficAlternatives: TrafficAlternativeDto[]
  },
): Promise<InteractionDefinitionDto> {
  const result = await command<{ interaction: InteractionDefinitionDto }>(
    `/api/v1/catalogues/application-definitions/${encodeURIComponent(applicationId)}/interactions`,
    input,
  )
  return result.interaction
}

export async function updateApplicationDefinition(
  definition: ApplicationDefinitionDto,
  input: {
    displayName: string
    description?: string | null
    domain?: string | null
    ownerReference?: string | null
  },
): Promise<ApplicationDefinitionDto> {
  const result = await command<{ definition: ApplicationDefinitionDto }>(
    `/api/v1/catalogues/application-definitions/${encodeURIComponent(definition.applicationId)}/metadata`,
    { ...input, expectedVersion: definition.version },
  )
  return result.definition
}

export async function updateApplicationComponent(
  component: ApplicationComponentDto,
  input: {
    displayName: string
    componentType?: string | null
    description?: string | null
  },
): Promise<ApplicationComponentDto> {
  const result = await command<{ component: ApplicationComponentDto }>(
    `/api/v1/catalogues/application-components/${encodeURIComponent(component.componentId)}/metadata`,
    { ...input, expectedVersion: component.version },
  )
  return result.component
}

export async function updateInteractionEndpoints(
  interaction: InteractionDefinitionDto,
  sourceComponentId: string,
  destinationComponentId: string,
): Promise<InteractionDefinitionDto> {
  const result = await command<{ interaction: InteractionDefinitionDto }>(
    `/api/v1/catalogues/interaction-definitions/${encodeURIComponent(interaction.interactionDefinitionId)}/endpoints`,
    {
      sourceComponentId,
      destinationComponentId,
      expectedVersion: interaction.version,
    },
  )
  return result.interaction
}

export async function updateInteractionTraffic(
  interaction: InteractionDefinitionDto,
  trafficAlternatives: TrafficAlternativeDto[],
): Promise<InteractionDefinitionDto> {
  const result = await command<{ interaction: InteractionDefinitionDto }>(
    `/api/v1/catalogues/interaction-definitions/${encodeURIComponent(interaction.interactionDefinitionId)}/traffic`,
    { trafficAlternatives, expectedVersion: interaction.version },
  )
  return result.interaction
}

export async function updateApplicationDeployment(
  deployment: ApplicationDeploymentDto,
  input: {
    companyReference: string
    environment: string
    scopeReference: string
  },
): Promise<ApplicationDeploymentDto> {
  const result = await command<{ deployment: ApplicationDeploymentDto }>(
    `/api/v1/catalogues/application-deployments/${encodeURIComponent(deployment.applicationDeploymentId)}/context`,
    { ...input, expectedVersion: deployment.version },
  )
  return result.deployment
}

type RetiredSubject = {
  kind: string
  reference: string
  lifecycleState: "Retired"
  version: number
}

async function retire(path: string, expectedVersion: number): Promise<RetiredSubject> {
  const result = await command<{ subject: RetiredSubject }>(path, { expectedVersion })
  return result.subject
}

export function retireApplicationDefinition(definition: ApplicationDefinitionDto) {
  return retire(
    `/api/v1/catalogues/application-definitions/${encodeURIComponent(definition.applicationId)}/retire`,
    definition.version,
  )
}

export function retireApplicationComponent(component: ApplicationComponentDto) {
  return retire(
    `/api/v1/catalogues/application-components/${encodeURIComponent(component.componentId)}/retire`,
    component.version,
  )
}

export function retireInteractionDefinition(interaction: InteractionDefinitionDto) {
  return retire(
    `/api/v1/catalogues/interaction-definitions/${encodeURIComponent(interaction.interactionDefinitionId)}/retire`,
    interaction.version,
  )
}

export function retireApplicationDeployment(deployment: ApplicationDeploymentDto) {
  return retire(
    `/api/v1/catalogues/application-deployments/${encodeURIComponent(deployment.applicationDeploymentId)}/retire`,
    deployment.version,
  )
}

export function retireDeploymentInteraction(
  deploymentInteractionId: string,
  expectedVersion: number,
) {
  return retire(
    `/api/v1/catalogues/deployment-interactions/${encodeURIComponent(deploymentInteractionId)}/retire`,
    expectedVersion,
  )
}

export async function createDeploymentResourceBinding(input: {
  deploymentInteractionId: string
  side: DeploymentInteractionSide
  resourceReference: string
  validFrom: string
  validTo?: string | null
}): Promise<BindingDto> {
  const result = await command<{ binding: BindingDto }>(
    `/api/v1/catalogues/deployment-interactions/${encodeURIComponent(input.deploymentInteractionId)}/resource-bindings`,
    {
      side: input.side,
      resourceReference: input.resourceReference,
      validFrom: input.validFrom,
      validTo: input.validTo ?? null,
    },
  )
  return result.binding
}

export async function endDeploymentResourceBinding(input: {
  deploymentInteractionId: string
  side: DeploymentInteractionSide
  bindingReference: string
  validTo: string
  expectedVersion: number
}): Promise<BindingDto> {
  const result = await command<{ binding: BindingDto }>(
    `/api/v1/catalogues/deployment-interactions/${encodeURIComponent(input.deploymentInteractionId)}/resource-bindings/${encodeURIComponent(input.bindingReference)}/end`,
    {
      side: input.side,
      validTo: input.validTo,
      expectedVersion: input.expectedVersion,
    },
  )
  return result.binding
}
