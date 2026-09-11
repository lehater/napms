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
import type { DeploymentConnectivityDto, DeploymentInteractionSide } from "@/features/catalogues/api/targetCatalogue"
import { resourceCount, trafficSummary } from "@/features/catalogues/model/targetPresentation"

export function DeploymentConnectivityTable({
  items,
  removingId,
  removing,
  onOpenResources,
  onRequestRemove,
  onCancelRemove,
  onConfirmRemove,
}: {
  items: DeploymentConnectivityDto[]
  removingId: string | null
  removing: boolean
  onOpenResources: (deploymentInteractionId: string, side: DeploymentInteractionSide) => void
  onRequestRemove: (deploymentInteractionId: string) => void
  onCancelRemove: () => void
  onConfirmRemove: (deploymentInteractionId: string) => void
}) {
  return (
    <DataTable minWidth={1120}>
      <DataTableHeader>
        <DataTableHeaderRow>
          <DataTableHeadCell>Source component</DataTableHeadCell>
          <DataTableHeadCell className="text-right">Source resources</DataTableHeadCell>
          <DataTableHeadCell>Destination component</DataTableHeadCell>
          <DataTableHeadCell className="text-right">Destination resources</DataTableHeadCell>
          <DataTableHeadCell>Traffic</DataTableHeadCell>
          <DataTableHeadCell className="w-44" />
        </DataTableHeaderRow>
      </DataTableHeader>
      <DataTableBody>
        {items.map((item) => (
          <DataTableRow key={item.deploymentInteractionId}>
            <DataTableCell className="font-semibold text-[var(--napms-color-text-primary)]">{item.sourceComponent.displayName}</DataTableCell>
            <DataTableCell className="text-right tabular-nums">
              <button type="button" className="font-semibold text-[var(--napms-color-primary)] hover:underline" onClick={() => onOpenResources(item.deploymentInteractionId, "Source")}>
                {resourceCount(item.sourceComponent.resourceCount)}
              </button>
            </DataTableCell>
            <DataTableCell className="font-semibold text-[var(--napms-color-text-primary)]">{item.destinationComponent.displayName}</DataTableCell>
            <DataTableCell className="text-right tabular-nums">
              <button type="button" className="font-semibold text-[var(--napms-color-primary)] hover:underline" onClick={() => onOpenResources(item.deploymentInteractionId, "Destination")}>
                {resourceCount(item.destinationComponent.resourceCount)}
              </button>
            </DataTableCell>
            <DataTableCell>{trafficSummary(item.trafficAlternatives)}</DataTableCell>
            <DataTableCell className="text-right">
              {removingId === item.deploymentInteractionId ? (
                <div className="flex justify-end gap-2">
                  <Button variant="ghost" size="sm" disabled={removing} onClick={onCancelRemove}>Cancel</Button>
                  <Button variant="secondary" size="sm" loading={removing} onClick={() => onConfirmRemove(item.deploymentInteractionId)}>Confirm remove</Button>
                </div>
              ) : (
                <Button variant="ghost" size="sm" onClick={() => onRequestRemove(item.deploymentInteractionId)}>Remove from deployment</Button>
              )}
            </DataTableCell>
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  )
}
