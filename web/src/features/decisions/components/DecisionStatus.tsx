import { StatusBadge } from "@/design-system/components/StatusBadge"
import type {
  ConnectivityDecisionDto,
  ConnectivityDecisionOutcome,
} from "@/features/decisions/api"

export function DecisionOutcomeStatus({
  outcome,
}: {
  outcome: ConnectivityDecisionOutcome
}) {
  return (
    <StatusBadge tone={outcome === "Allowed" ? "positive" : "critical"}>
      {outcome}
    </StatusBadge>
  )
}

export function decisionValidityText(decision: ConnectivityDecisionDto) {
  return decision.validity.validUntil
    ? `${decision.validity.validFrom} → ${decision.validity.validUntil}`
    : `${decision.validity.validFrom} → open-ended`
}
