import { Button } from "@/design-system/components/Button"
import {
  DataTable,
  DataTableBody,
  DataTableCell,
  DataTableHeadCell,
  DataTableHeader,
  DataTableHeaderRow,
  DataTableRow,
} from "@/design-system/components/DataTable"
import type { ResourceSetMemberDto } from "@/features/catalogues/api/targetCatalogue"

function scopesSummary(scopes: string[]) {
  if (scopes.length === 0) return "—"
  if (scopes.length <= 2) return scopes.join(", ")
  return `${scopes.slice(0, 2).join(", ")} +${scopes.length - 2}`
}

export function DeploymentResourceSetTable({
  items,
  endingReference,
  ending,
  onRequestEnd,
  onCancelEnd,
  onConfirmEnd,
}: {
  items: ResourceSetMemberDto[]
  endingReference: string | null
  ending: boolean
  onRequestEnd: (bindingReference: string) => void
  onCancelEnd: () => void
  onConfirmEnd: (item: ResourceSetMemberDto) => void
}) {
  return (
    <DataTable minWidth={760}>
      <DataTableHeader>
        <DataTableHeaderRow>
          <DataTableHeadCell>Resource</DataTableHeadCell>
          <DataTableHeadCell>Scope</DataTableHeadCell>
          <DataTableHeadCell className="w-44 text-right">Membership</DataTableHeadCell>
        </DataTableHeaderRow>
      </DataTableHeader>
      <DataTableBody>
        {items.map((item) => (
          <DataTableRow key={item.bindingReference}>
            <DataTableCell className="font-semibold text-[var(--napms-color-text-primary)]">{item.displayName ?? item.resourceReference}</DataTableCell>
            <DataTableCell>{scopesSummary(item.scopeReferences)}</DataTableCell>
            <DataTableCell className="text-right">
              {endingReference === item.bindingReference ? (
                <div className="flex justify-end gap-2">
                  <Button variant="ghost" size="sm" disabled={ending} onClick={onCancelEnd}>Cancel</Button>
                  <Button variant="secondary" size="sm" loading={ending} onClick={() => onConfirmEnd(item)}>Confirm end</Button>
                </div>
              ) : (
                <Button variant="ghost" size="sm" onClick={() => onRequestEnd(item.bindingReference)}>End membership</Button>
              )}
            </DataTableCell>
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  )
}
