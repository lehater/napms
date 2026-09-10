import { ApiError } from "@/api"

export type DeploymentInteractionLifecycleDto = {
  deploymentInteractionId: string
  applicationDeploymentId: string
  interactionDefinitionId: string
  lifecycleState: "Active" | "Retired"
  version: number
}

export async function readDeploymentInteractionLifecycle(
  deploymentInteractionId: string,
): Promise<DeploymentInteractionLifecycleDto> {
  const response = await fetch(
    `/api/v1/catalogues/deployment-interactions/${encodeURIComponent(deploymentInteractionId)}`,
    {
      credentials: "same-origin",
      headers: { Accept: "application/json" },
    },
  )
  const payload = await response.json()
  if (!response.ok) {
    const error = payload?.error
    throw new ApiError(
      response.status,
      error?.code ?? "HttpError",
      error?.message ?? "The Deployment Interaction could not be loaded.",
      error?.correlationId,
    )
  }
  return payload.deploymentInteraction as DeploymentInteractionLifecycleDto
}
