import { IssueIndicator } from "@/design-system/components/IssueIndicator"
import type { ResourceWorkspaceItemDto } from "@/features/catalogues/api/resourceWorkspace"

export function ResourceDataState({ item }: { item: ResourceWorkspaceItemDto }) {
  const missing: Array<{ label: string; tone: "warning" | "danger" }> = []
  if (!item.currentFacts.hasRealization) missing.push({ label: "No address", tone: "danger" })
  if (!item.currentFacts.hasScopeAffiliation) missing.push({ label: "No scope", tone: "warning" })
  if (!item.currentFacts.hasResponsibility) missing.push({ label: "No responsibility", tone: "warning" })

  if (missing.length === 0) {
    return <IssueIndicator tone="success">No missing facts</IssueIndicator>
  }

  return (
    <div className="grid gap-0.5">
      {missing.map(({ label, tone }) => (
        <IssueIndicator key={label} tone={tone}>{label}</IssueIndicator>
      ))}
    </div>
  )
}
