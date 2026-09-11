import { ChevronRight } from "lucide-react"

import {
  DataTable,
  DataTableBody,
  DataTableCell,
  DataTableHeadCell,
  DataTableHeader,
  DataTableHeaderRow,
  DataTableRow,
} from "@/design-system/components/DataTable"
import { displayName } from "@/features/catalogues/components/CatalogueIdentity"
import type {
  ConnectivityRequirementDto,
  RequirementPolicyAlignmentStatus,
} from "@/features/requirements/api"
import {
  RequirementAlignmentStatus,
  RequirementLifecycleStatus,
  requirementApplicabilityText,
} from "@/features/requirements/components/RequirementStatus"

export function RequirementsTable({
  requirements,
  alignmentById,
  loadingAlignment,
  onOpenRequirement,
}: {
  requirements: ConnectivityRequirementDto[]
  alignmentById: Record<string, RequirementPolicyAlignmentStatus>
  loadingAlignment: boolean
  onOpenRequirement: (requirementId: string) => void
}) {
  return (
    <DataTable minWidth={980}>
      <DataTableHeader>
        <DataTableHeaderRow>
          <DataTableHeadCell>Interaction</DataTableHeadCell>
          <DataTableHeadCell>Dependent</DataTableHeadCell>
          <DataTableHeadCell>Scope</DataTableHeadCell>
          <DataTableHeadCell>Applicability</DataTableHeadCell>
          <DataTableHeadCell>Policy coverage</DataTableHeadCell>
          <DataTableHeadCell>Lifecycle</DataTableHeadCell>
          <DataTableHeadCell className="w-12" aria-label="Open" />
        </DataTableHeaderRow>
      </DataTableHeader>
      <DataTableBody>
        {requirements.map((item) => {
          const interaction = item.requiredInteraction
          const dependentName = item.dependentComponentDeploymentId === interaction.sourceComponentDeploymentId
            ? displayName(item.catalogue?.sourceDisplayName, interaction.sourceComponentDeploymentId)
            : displayName(item.catalogue?.destinationDisplayName, interaction.destinationComponentDeploymentId)
          const alignment = alignmentById[item.requirementId]
          return (
            <DataTableRow key={item.requirementId}>
              <DataTableCell>
                <div className="font-medium text-[var(--napms-color-text-primary)]">
                  {displayName(item.catalogue?.sourceDisplayName, interaction.sourceComponentDeploymentId)} → {displayName(item.catalogue?.destinationDisplayName, interaction.destinationComponentDeploymentId)}
                </div>
                <div className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">{displayName(item.catalogue?.dcsDisplayName, interaction.dcsContractRevisionId)}</div>
              </DataTableCell>
              <DataTableCell>{dependentName}</DataTableCell>
              <DataTableCell>{item.governanceScope}</DataTableCell>
              <DataTableCell className="text-xs text-[var(--napms-color-text-body)]">{requirementApplicabilityText(item.applicability)}</DataTableCell>
              <DataTableCell>{alignment ? <RequirementAlignmentStatus status={alignment} /> : <span className="text-xs text-[var(--napms-color-text-secondary)]">{loadingAlignment ? "Loading…" : "—"}</span>}</DataTableCell>
              <DataTableCell><RequirementLifecycleStatus state={item.lifecycleState} /></DataTableCell>
              <DataTableCell>
                <button type="button" aria-label={`Open Requirement ${item.requirementId}`} className="grid size-8 place-items-center rounded-[var(--napms-control-radius)] text-[var(--napms-color-text-secondary)] hover:bg-[var(--napms-color-surface-muted)]" onClick={() => onOpenRequirement(item.requirementId)}>
                  <ChevronRight className="size-4" aria-hidden="true" />
                </button>
              </DataTableCell>
            </DataTableRow>
          )
        })}
      </DataTableBody>
    </DataTable>
  )
}
