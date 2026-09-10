import { ApiError } from "@/api"

export type Availability = "Available" | "NotAvailable" | "Unknown"

export type NetworkOperatorRealizationResponse = {
  scope: string
  asOf: string
  authorityReference: string
  desired: {
    availability: Availability
    status: string | null
    ruleReferences: string[]
    targets: Array<{
      logicalFirewallId: string
      enforcementAttachmentId: string
      placementProvenanceReferences: string[]
    }>
    reason: string | null
  }
  reconciliation: {
    availability: Availability
    status: string | null
    requiredChange: string | null
    reason: string | null
  }
  rendering: {
    availability: Availability
    artifacts: Array<{
      status: string
      logicalFirewallId: string
      enforcementAttachmentId: string
      rendererName: string
      rendererContractVersion: string
      content: string | null
      reason: string | null
    }>
    reason: string | null
  }
  operation: {
    availability: Availability
    operationId: string | null
    outcome: string | null
    provenanceReferences: string[]
    reason: string | null
  }
}

export async function getNetworkOperatorRealization(
  scope: string,
  asOf: string,
): Promise<NetworkOperatorRealizationResponse> {
  const params = new URLSearchParams({ scope, asOf })
  const response = await fetch(`/api/v1/network-operator-realization?${params}`, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" },
  })
  const payload = await response.json()
  if (!response.ok) {
    const error = payload?.error
    throw new ApiError(
      response.status,
      error?.code ?? "HttpError",
      error?.message ?? payload?.detail ?? "Operator realization could not be loaded.",
      error?.correlationId,
    )
  }
  return payload as NetworkOperatorRealizationResponse
}
