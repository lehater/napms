import { StatusIndicator } from "@/design-system/components/StatusIndicator"

export function CatalogueLifecycleStatus({
  value,
}: {
  value: "Active" | "Retired"
}) {
  return (
    <StatusIndicator tone={value === "Active" ? "positive" : "critical"}>
      {value}
    </StatusIndicator>
  )
}
