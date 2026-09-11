import { StatusBadge } from "@/design-system/components/StatusBadge"

export function RealizationAvailabilityStatus({ value }: { value: string }) {
  const normalized = value.toLowerCase()
  const tone = normalized === "available" || normalized === "resolved"
    ? "positive"
    : normalized === "partial" || normalized === "unknown"
      ? "warning"
      : "neutral"
  return <StatusBadge tone={tone}>{value}</StatusBadge>
}
