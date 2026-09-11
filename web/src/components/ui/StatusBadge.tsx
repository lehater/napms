import { StatusBadge as DesignStatusBadge } from "@/design-system/components/StatusBadge"

export function StatusBadge({
  value,
}: {
  value: "Active" | "Inactive" | "Permitted" | "Denied" | "Unknown"
}) {
  const tone = {
    Active: "positive",
    Inactive: "neutral",
    Permitted: "positive",
    Denied: "critical",
    Unknown: "unknown",
  }[value] as "positive" | "neutral" | "critical" | "unknown"

  return <DesignStatusBadge tone={tone}>{value}</DesignStatusBadge>
}
