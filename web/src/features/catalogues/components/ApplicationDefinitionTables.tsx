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
import type {
  ApplicationComponentDto,
  ApplicationDeploymentSummaryDto,
  InteractionDefinitionSummaryDto,
} from "@/features/catalogues/api/targetCatalogue"
import { trafficSummary } from "@/features/catalogues/model/targetPresentation"

export function ApplicationComponentsTable({
  items,
  onEdit,
}: {
  items: ApplicationComponentDto[]
  onEdit: (item: ApplicationComponentDto) => void
}) {
  return (
    <DataTable width="compact">
      <DataTableHeader>
        <DataTableHeaderRow>
          <DataTableHeadCell>Name</DataTableHeadCell>
          <DataTableHeadCell>Type</DataTableHeadCell>
          <DataTableHeadCell>Description</DataTableHeadCell>
          <DataTableHeadCell className="w-20" />
        </DataTableHeaderRow>
      </DataTableHeader>
      <DataTableBody>
        {items.map((item) => (
          <DataTableRow key={item.componentId}>
            <DataTableCell className="font-semibold text-[var(--napms-color-text-primary)]">{item.displayName}</DataTableCell>
            <DataTableCell>{item.componentType ?? "—"}</DataTableCell>
            <DataTableCell>{item.description ?? "—"}</DataTableCell>
            <DataTableCell><Button variant="ghost" size="sm" onClick={() => onEdit(item)}>Edit</Button></DataTableCell>
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  )
}

export function InteractionDefinitionsTable({
  items,
  onEdit,
}: {
  items: InteractionDefinitionSummaryDto[]
  onEdit: (item: InteractionDefinitionSummaryDto) => void
}) {
  return (
    <DataTable width="standard">
      <DataTableHeader>
        <DataTableHeaderRow>
          <DataTableHeadCell>Source</DataTableHeadCell>
          <DataTableHeadCell>Destination</DataTableHeadCell>
          <DataTableHeadCell>Traffic</DataTableHeadCell>
          <DataTableHeadCell className="text-right">Deployments</DataTableHeadCell>
          <DataTableHeadCell className="w-20" />
        </DataTableHeaderRow>
      </DataTableHeader>
      <DataTableBody>
        {items.map((item) => (
          <DataTableRow key={item.interactionDefinitionId}>
            <DataTableCell className="font-semibold text-[var(--napms-color-text-primary)]">{item.sourceComponentName}</DataTableCell>
            <DataTableCell className="font-semibold text-[var(--napms-color-text-primary)]">{item.destinationComponentName}</DataTableCell>
            <DataTableCell>{trafficSummary(item.trafficAlternatives)}</DataTableCell>
            <DataTableCell className="text-right tabular-nums">{item.activeDeploymentCount}</DataTableCell>
            <DataTableCell><Button variant="ghost" size="sm" onClick={() => onEdit(item)}>Edit</Button></DataTableCell>
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  )
}

export function ApplicationDeploymentsTable({
  items,
  onOpen,
}: {
  items: ApplicationDeploymentSummaryDto[]
  onOpen: (deploymentId: string) => void
}) {
  return (
    <DataTable width="compact">
      <DataTableHeader>
        <DataTableHeaderRow>
          <DataTableHeadCell>Company</DataTableHeadCell>
          <DataTableHeadCell>Environment</DataTableHeadCell>
          <DataTableHeadCell>Scope</DataTableHeadCell>
          <DataTableHeadCell className="text-right">Interactions</DataTableHeadCell>
        </DataTableHeaderRow>
      </DataTableHeader>
      <DataTableBody>
        {items.map((item) => (
          <DataTableRow key={item.applicationDeploymentId} onClick={() => onOpen(item.applicationDeploymentId)}>
            <DataTableCell className="font-semibold text-[var(--napms-color-text-primary)]">{item.companyReference}</DataTableCell>
            <DataTableCell>{item.environment}</DataTableCell>
            <DataTableCell>{item.scopeReference}</DataTableCell>
            <DataTableCell className="text-right tabular-nums">{item.selectedInteractionCount} / {item.definedInteractionCount}</DataTableCell>
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  )
}
