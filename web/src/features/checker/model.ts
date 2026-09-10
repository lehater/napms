export type ResolutionState = "Resolved" | "Ambiguous" | "Unknown" | "Historical"
export type MatchKind = "Exact" | "CoversQuery" | "CoveredByQuery" | "Overlap" | "Unknown"

export type CheckerQuery = {
  sourceAddress: string
  destinationAddress: string
  protocol: string
  port: string
  asOf: string
}

export type ResourceSide = {
  state: ResolutionState
  address: string
  endpointReference: string | null
  resourceReference: string | null
  componentName: string | null
  serviceName: string | null
  responsibilityScope: string | null
  responsibilities: Array<{
    role: string
    party: string
    contact: string | null
  }>
}

export type EvidenceEntry = {
  reference: string
  action: "Permit" | "Block" | "Unknown"
  normalized: string
  match: MatchKind
}

export type NetworkCandidate = {
  deviceReference: string
  logicalFirewallReference: string | null
  attachmentReference: string | null
  relevance: string | null
  provenanceReferences: string[]
  snapshot: null | {
    reference: string
    capturedAt: string | null
    recordedAt: string
    source: string
    entries: EvidenceEntry[]
  }
}

export type CheckerResult = {
  query: CheckerQuery
  source: ResourceSide
  destination: ResourceSide
  connectivity: {
    sourceComponent: string | null
    destinationComponent: string | null
    dcs: string | null
    access: string | null
  }
  policy: {
    requirement: string
    requirementReference: string | null
    decision: string
    decisionReference: string | null
    rule: string
    ruleReference: string | null
    effective: string
  }
  networkContext: {
    completeForPair: boolean
    knowledgeGaps: string[]
    candidates: NetworkCandidate[]
  }
  findings: string[]
}

export const initialCheckerQuery: CheckerQuery = {
  sourceAddress: "10.10.10.10",
  destinationAddress: "10.20.20.20",
  protocol: "TCP",
  port: "443",
  asOf: new Date().toISOString(),
}

export function checkerFixture(query: CheckerQuery): CheckerResult {
  const happy =
    query.sourceAddress.trim() === "10.10.10.10" &&
    query.destinationAddress.trim() === "10.20.20.20" &&
    query.protocol.trim().toUpperCase() === "TCP" &&
    query.port.trim() === "443"

  if (!happy) {
    return {
      query,
      source: unresolvedSide(query.sourceAddress),
      destination: unresolvedSide(query.destinationAddress),
      connectivity: {
        sourceComponent: null,
        destinationComponent: null,
        dcs: null,
        access: null,
      },
      policy: {
        requirement: "Unknown",
        requirementReference: null,
        decision: "Unknown",
        decisionReference: null,
        rule: "Unknown",
        ruleReference: null,
        effective: "Unknown",
      },
      networkContext: {
        completeForPair: false,
        knowledgeGaps: ["No deterministic local fixture matches this traffic tuple."],
        candidates: [],
      },
      findings: ["Technical-to-domain resolution is unavailable for this fixture."],
    }
  }

  return {
    query,
    source: {
      state: "Resolved",
      address: query.sourceAddress,
      endpointReference: "local-demo-source:endpoint",
      resourceReference: "local-demo-source",
      componentName: "Demo Web Frontend",
      serviceName: "Demo Web Frontend",
      responsibilityScope: "local-demo",
      responsibilities: [
        {
          role: "Service owner",
          party: "Demo Application Team",
          contact: "demo-app-ops",
        },
        {
          role: "Operations contact",
          party: "Demo Application Operations",
          contact: "demo-app-ops",
        },
      ],
    },
    destination: {
      state: "Resolved",
      address: query.destinationAddress,
      endpointReference: "local-demo-destination:endpoint",
      resourceReference: "local-demo-destination",
      componentName: "Demo Orders API",
      serviceName: "Demo Orders API",
      responsibilityScope: "local-demo",
      responsibilities: [
        {
          role: "Service owner",
          party: "Demo Orders Team",
          contact: "demo-orders-ops",
        },
      ],
    },
    connectivity: {
      sourceComponent: "Demo Web Frontend",
      destinationComponent: "Demo Orders API",
      dcs: "HTTPS Orders API",
      access: "TCP/443",
    },
    policy: {
      requirement: "Required",
      requirementReference: "fixture:requirement",
      decision: "Allowed",
      decisionReference: "fixture:decision",
      rule: "Active",
      ruleReference: "fixture:access-rule",
      effective: "Effective",
    },
    networkContext: {
      completeForPair: false,
      knowledgeGaps: [
        "Candidate enumeration is best-effort and may contain false positives.",
      ],
      candidates: [
        {
          deviceReference: "fw-demo-edge",
          logicalFirewallReference: "lf-demo-edge",
          attachmentReference: "attachment-demo-edge",
          relevance: "Strong",
          provenanceReferences: ["local-demo:network-context:edge"],
          snapshot: {
            reference: "fixture:tae:edge",
            capturedAt: "2026-09-10T00:00:00Z",
            recordedAt: "2026-09-10T00:05:00Z",
            source: "local-demo-firewall-import",
            entries: [
              {
                reference: "ACL-DEMO-100",
                action: "Permit",
                normalized: "10.10.10.0/24 → 10.20.20.0/24 TCP/443",
                match: "CoversQuery",
              },
            ],
          },
        },
        {
          deviceReference: "fw-demo-core",
          logicalFirewallReference: "lf-demo-core",
          attachmentReference: null,
          relevance: "Possible",
          provenanceReferences: ["local-demo:network-context:core"],
          snapshot: {
            reference: "fixture:tae:core",
            capturedAt: "2026-09-09T22:00:00Z",
            recordedAt: "2026-09-09T22:04:00Z",
            source: "local-demo-firewall-import",
            entries: [
              {
                reference: "CORE-DEMO-200",
                action: "Permit",
                normalized: "10.10.0.0/16 → 10.20.0.0/16 TCP/443",
                match: "CoversQuery",
              },
            ],
          },
        },
        {
          deviceReference: "fw-demo-legacy",
          logicalFirewallReference: null,
          attachmentReference: null,
          relevance: "Possible",
          provenanceReferences: ["local-demo:network-context:legacy"],
          snapshot: null,
        },
      ],
    },
    findings: [
      "Network Context contains possible candidates; candidate membership is not path proof.",
      "fw-demo-legacy has no applicable stored configured-evidence snapshot.",
    ],
  }
}

function unresolvedSide(address: string): ResourceSide {
  return {
    state: "Unknown",
    address,
    endpointReference: null,
    resourceReference: null,
    componentName: null,
    serviceName: null,
    responsibilityScope: null,
    responsibilities: [],
  }
}
