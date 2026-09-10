import { ApiError } from "@/api"
import type {
  CheckerQuery,
  CheckerResult,
  NetworkCandidate,
  ResourceSide,
} from "@/features/checker/model"

type ApiResolution = {
  state: ResourceSide["state"]
  address: string
  resources: Array<{
    resourceReference: string
    endpointReference: string
    technicalAddress: string
    componentNames: string[]
    responsibilityScope: string | null
    provenanceReferences: string[]
  }>
}

type ApiResponsibility = {
  resourceReference: string
  role: string
  partyReference: string
  partyKind: string
  displayName: string
  contact: string | null
  provenanceReference: string
}

type TrafficAnalysisResponse = {
  query: CheckerQuery
  source: ApiResolution
  destination: ApiResolution
  policyMatches: Array<{
    sourceComponent: string | null
    destinationComponent: string | null
    dcsReference: string | null
    dcsDisplayName: string | null
    accessSummary: string | null
    requirement: string
    decision: string
    rule: string
    effective: string
    scope: string | null
    partial: boolean
  }>
  sourceResponsibilities: ApiResponsibility[]
  destinationResponsibilities: ApiResponsibility[]
  networkContext: {
    completeForPair: boolean
    knowledgeGaps: string[]
    candidates: Array<{
      providerNamespace: string
      deviceReference: string
      logicalFirewallReference: string | null
      enforcementAttachmentReference: string | null
      pathAttachmentReference: string | null
      sourceRelevance: string | null
      provenanceReferences: string[]
      evidence: null | {
        evidenceSetReference: string
        sourceReference: string
        sourceScopeReference: string
        capturedAt: string | null
        recordedAt: string
        provenanceReferences: string[]
        matches: Array<{
          entryReference: string
          action: "Permit" | "Block" | "Unknown"
          normalized: string
          matchKind: "Exact" | "CoversQuery" | "CoveredByQuery" | "Overlap" | "Unknown"
        }>
      }
    }>
  }
  findings: string[]
}

export async function getTrafficAnalysis(query: CheckerQuery): Promise<CheckerResult> {
  const params = new URLSearchParams({
    source: query.sourceAddress,
    destination: query.destinationAddress,
    protocol: query.protocol,
    port: query.port,
    asOf: query.asOf,
  })
  const response = await fetch(`/api/v1/traffic-analysis?${params}`, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" },
  })
  const payload = await response.json()
  if (!response.ok) {
    const error = payload?.error
    throw new ApiError(
      response.status,
      error?.code ?? "HttpError",
      error?.message ?? payload?.detail ?? "Traffic analysis could not be loaded.",
      error?.correlationId,
    )
  }
  return adaptTrafficAnalysis(payload as TrafficAnalysisResponse)
}

function adaptTrafficAnalysis(payload: TrafficAnalysisResponse): CheckerResult {
  const policy = payload.policyMatches[0]
  return {
    query: payload.query,
    source: adaptSide(payload.source, payload.sourceResponsibilities),
    destination: adaptSide(payload.destination, payload.destinationResponsibilities),
    connectivity: {
      sourceComponent: policy?.sourceComponent ?? null,
      destinationComponent: policy?.destinationComponent ?? null,
      dcs: policy?.dcsDisplayName ?? policy?.dcsReference ?? null,
      access: policy?.accessSummary ?? null,
    },
    policy: {
      requirement: policy?.requirement ?? "Unknown",
      requirementReference: null,
      decision: policy?.decision ?? "Unknown",
      decisionReference: null,
      rule: policy?.rule ?? "Unknown",
      ruleReference: null,
      effective: policy?.effective ?? "Unknown",
    },
    networkContext: {
      completeForPair: payload.networkContext.completeForPair,
      knowledgeGaps: payload.networkContext.knowledgeGaps,
      candidates: payload.networkContext.candidates.map(adaptCandidate),
    },
    findings: [
      ...payload.findings,
      ...(payload.policyMatches.length > 1
        ? [`${payload.policyMatches.length} policy projections match this traffic tuple.`]
        : []),
    ],
  }
}

function adaptSide(
  resolution: ApiResolution,
  responsibilities: ApiResponsibility[],
): ResourceSide {
  const primary = resolution.resources[0]
  return {
    state: resolution.state,
    address: resolution.address,
    endpointReference: primary?.endpointReference ?? null,
    resourceReference: primary?.resourceReference ?? null,
    componentName: primary?.componentNames[0] ?? null,
    serviceName: primary?.componentNames[0] ?? null,
    responsibilityScope: primary?.responsibilityScope ?? null,
    responsibilities: responsibilities.map((item) => ({
      role: humanizeRole(item.role),
      party: item.displayName,
      contact: item.contact,
    })),
  }
}

function adaptCandidate(
  item: TrafficAnalysisResponse["networkContext"]["candidates"][number],
): NetworkCandidate {
  return {
    deviceReference: item.deviceReference,
    logicalFirewallReference: item.logicalFirewallReference,
    attachmentReference: item.enforcementAttachmentReference,
    relevance: item.sourceRelevance,
    provenanceReferences: item.provenanceReferences,
    snapshot: item.evidence
      ? {
          reference: item.evidence.evidenceSetReference,
          capturedAt: item.evidence.capturedAt,
          recordedAt: item.evidence.recordedAt,
          source: item.evidence.sourceReference,
          entries: item.evidence.matches.map((entry) => ({
            reference: entry.entryReference,
            action: entry.action,
            normalized: entry.normalized,
            match: entry.matchKind,
          })),
        }
      : null,
  }
}

function humanizeRole(value: string) {
  return value.replace(/([a-z])([A-Z])/g, "$1 $2").replace(/^./, (item) => item.toUpperCase())
}
