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
import {
  CatalogueIdentity,
  displayName,
  shortId,
} from "@/features/catalogues/components/CatalogueIdentity"
import type { ConnectivityDecisionDto } from "@/features/decisions/api"
import {
  DecisionOutcomeStatus,
  decisionValidityText,
} from "@/features/decisions/components/DecisionStatus"

export function DecisionsTable({
  decisions,
  onOpenDecision,
}: {
  decisions: ConnectivityDecisionDto[]
  onOpenDecision: (decisionId: string) => void
}) {
  return (
    <DataTable width="wide">
      <DataTableHeader>
        <DataTableHeaderRow>
          <DataTableHeadCell>Subject</DataTableHeadCell>
          <DataTableHeadCell>Scope</DataTableHeadCell>
          <DataTableHeadCell>Outcome</DataTableHeadCell>
          <DataTableHeadCell>Validity</DataTableHeadCell>
          <DataTableHeadCell>Supersession</DataTableHeadCell>
          <DataTableHeadCell className="w-12" aria-label="Open" />
        </DataTableHeaderRow>
      </DataTableHeader>
      <DataTableBody>
        {decisions.map((decision) => (
          <DataTableRow key={decision.decisionId}>
            <DataTableCell>
              <div className="grid gap-2">
                <CatalogueIdentity name={decision.catalogue?.sourceDisplayName} id={decision.subject.sourceComponentDeploymentId} />
                <div className="text-xs font-semibold text-[var(--napms-color-text-secondary)]">to</div>
                <CatalogueIdentity name={decision.catalogue?.destinationDisplayName} id={decision.subject.destinationComponentDeploymentId} />
                <div className="text-xs text-[var(--napms-color-text-body)]">Access: {displayName(decision.catalogue?.dcsDisplayName, decision.subject.dcsContractRevisionId)}</div>
              </div>
            </DataTableCell>
            <DataTableCell>{decision.governanceScope}</DataTableCell>
            <DataTableCell><DecisionOutcomeStatus outcome={decision.outcome} /></DataTableCell>
            <DataTableCell className="text-xs text-[var(--napms-color-text-body)]">{decisionValidityText(decision)}</DataTableCell>
            <DataTableCell className="text-xs text-[var(--napms-color-text-body)]">{decision.supersedesDecisionId ? `Supersedes ${shortId(decision.supersedesDecisionId)}` : "Original"}</DataTableCell>
            <DataTableCell>
              <button type="button" aria-label={`Open Decision ${decision.decisionId}`} className="grid size-8 place-items-center rounded-[var(--napms-control-radius)] text-[var(--napms-color-text-secondary)] hover:bg-[var(--napms-color-surface-muted)]" onClick={() => onOpenDecision(decision.decisionId)}>
                <ChevronRight className="size-4" aria-hidden="true" />
              </button>
            </DataTableCell>
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  )
}
