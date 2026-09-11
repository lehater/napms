import { StatusBadge } from "@/design-system/components/StatusBadge"
import type {
  RequirementApplicability,
  RequirementPolicyAlignmentStatus,
} from "@/features/requirements/api"

export function requirementApplicabilityText(value: RequirementApplicability) {
  return value.kind === "Ongoing"
    ? "Ongoing"
    : `${value.start} → ${value.end}`
}

export function RequirementAlignmentStatus({
  status,
}: {
  status: RequirementPolicyAlignmentStatus
}) {
  const tone = {
    Covered: "positive",
    Uncovered: "warning",
    NotCurrent: "neutral",
    Unknown: "critical",
  }[status] as "positive" | "warning" | "neutral" | "critical"

  return (
    <StatusBadge
      tone={tone}
      title={
        status === "Uncovered"
          ? "No exact matching Access Rule contributes effective desired policy at the selected time. This does not mean Denied."
          : undefined
      }
    >
      {status}
    </StatusBadge>
  )
}

export function RequirementLifecycleStatus({
  state,
}: {
  state: "Active" | "Retired"
}) {
  return (
    <StatusBadge tone={state === "Active" ? "positive" : "neutral"}>
      {state}
    </StatusBadge>
  )
}
