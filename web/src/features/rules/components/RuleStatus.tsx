import { StatusBadge } from "@/design-system/components/StatusBadge"
import type { RuleDto } from "@/features/rules/model/rule"

export function RuleOperationalStatus({ state }: { state: RuleDto["operationalState"] }) {
  return <StatusBadge tone={state === "Active" ? "positive" : "neutral"}>{state}</StatusBadge>
}
