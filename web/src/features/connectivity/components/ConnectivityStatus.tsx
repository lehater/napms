import { StatusBadge } from "@/design-system/components/StatusBadge"
import type {
  ScopedConnectivityDecisionSummary,
  ScopedConnectivityNeedSummary,
  ScopedConnectivityPolicySummary,
} from "@/features/connectivity/api"

export function ConnectivityNeedStatus({
  value,
}: {
  value: ScopedConnectivityNeedSummary
}) {
  const need =
    value.current === "Required" ? (
      <StatusBadge tone="positive">Required</StatusBadge>
    ) : value.current === "Unknown" ? (
      <StatusBadge tone="unknown">Unknown need</StatusBadge>
    ) : value.historicalOnly ? (
      <StatusBadge>Not current</StatusBadge>
    ) : (
      <StatusBadge>No current need</StatusBadge>
    )

  const coverage =
    value.coverage === "Covered" ? (
      <StatusBadge tone="positive">Covered</StatusBadge>
    ) : value.coverage === "Uncovered" ? (
      <StatusBadge
        tone="warning"
        title="No exact matching Rule contributes effective desired policy. This does not mean Denied."
      >
        Uncovered
      </StatusBadge>
    ) : value.coverage === "Unknown" ? (
      <StatusBadge tone="unknown">Coverage unknown</StatusBadge>
    ) : value.coverage === "NotCurrent" ? (
      <StatusBadge>Not current</StatusBadge>
    ) : null

  return (
    <div className="flex flex-wrap gap-1.5">
      {need}
      {coverage}
    </div>
  )
}

export function ConnectivityDecisionStatus({
  value,
}: {
  value: ScopedConnectivityDecisionSummary
}) {
  switch (value.state) {
    case "Allowed":
      return <StatusBadge tone="positive">Allowed</StatusBadge>
    case "NotAllowed":
      return <StatusBadge tone="critical">Not allowed</StatusBadge>
    case "NoFinalDecision":
      return <StatusBadge>No final decision</StatusBadge>
    case "Unknown":
      return (
        <StatusBadge
          tone="unknown"
          title="The final Decision cannot currently be established. This is not a Pending decision state."
        >
          Unknown
        </StatusBadge>
      )
  }
}

export function ConnectivityPolicyStatus({
  value,
}: {
  value: ScopedConnectivityPolicySummary
}) {
  if (value.ruleExists === "Unknown") {
    return <StatusBadge tone="unknown">Unknown</StatusBadge>
  }
  if (value.ruleExists === "No") {
    return <StatusBadge>No rule</StatusBadge>
  }
  if (value.operationalState === "Inactive") {
    return <StatusBadge>Inactive</StatusBadge>
  }
  if (value.operationalState === "Active" && value.effectiveAtAsOf === "Yes") {
    return <StatusBadge tone="positive">Active · effective</StatusBadge>
  }
  if (value.operationalState === "Active" && value.effectiveAtAsOf === "No") {
    return <StatusBadge tone="warning">Active · not effective</StatusBadge>
  }
  return <StatusBadge tone="unknown">Unknown</StatusBadge>
}
