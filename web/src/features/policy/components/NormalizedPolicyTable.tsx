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
import type { PortConstraintDto } from "@/features/catalogues/model/interaction"
import type { NormalizedPolicyResponse } from "@/features/policy/api"

function renderPorts(value: PortConstraintDto): string {
  if (value.kind === "Any" || value.kind === "NotApplicable") return value.kind
  return (value.ranges ?? []).map((range) => range.first === range.last ? String(range.first) : `${range.first}-${range.last}`).join(", ")
}

export function NormalizedPolicyTable({ rows }: { rows: NormalizedPolicyResponse["rows"] }) {
  return (
    <DataTable width="extra-wide">
      <DataTableHeader>
        <DataTableHeaderRow>
          <DataTableHeadCell>Rule</DataTableHeadCell>
          <DataTableHeadCell>Source</DataTableHeadCell>
          <DataTableHeadCell>Destination</DataTableHeadCell>
          <DataTableHeadCell>Protocol</DataTableHeadCell>
          <DataTableHeadCell>Source ports</DataTableHeadCell>
          <DataTableHeadCell>Destination ports</DataTableHeadCell>
          <DataTableHeadCell>Service</DataTableHeadCell>
          <DataTableHeadCell>Provenance</DataTableHeadCell>
        </DataTableHeaderRow>
      </DataTableHeader>
      <DataTableBody>
        {rows.map((row, index) => (
          <DataTableRow key={`${row.ruleId}-${row.source.endpointReference}-${row.destination.endpointReference}-${row.traffic.protocol}-${index}`}>
            <DataTableCell>
              <div className="font-mono text-xs">{row.ruleId}</div>
              <div className="mt-1 text-xs font-medium text-[var(--napms-color-text-body)]">{displayName(row.catalogue?.dcsDisplayName, row.semanticIdentity.dcsContractRevisionId)}</div>
              <div className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">decision {row.decisionReference ?? "—"}</div>
            </DataTableCell>
            <DataTableCell>
              <div className="font-medium text-[var(--napms-color-text-primary)]">{displayName(row.catalogue?.sourceDisplayName, row.semanticIdentity.sourceComponentDeploymentId)}</div>
              <div className="mt-1 font-mono text-xs">{row.source.technicalAddress}</div>
              <div className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">{row.source.resourceReference} / {row.source.endpointReference}</div>
            </DataTableCell>
            <DataTableCell>
              <div className="font-medium text-[var(--napms-color-text-primary)]">{displayName(row.catalogue?.destinationDisplayName, row.semanticIdentity.destinationComponentDeploymentId)}</div>
              <div className="mt-1 font-mono text-xs">{row.destination.technicalAddress}</div>
              <div className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">{row.destination.resourceReference} / {row.destination.endpointReference}</div>
            </DataTableCell>
            <DataTableCell className="font-mono text-xs">{row.traffic.protocol}</DataTableCell>
            <DataTableCell className="font-mono text-xs">{renderPorts(row.traffic.sourcePorts)}</DataTableCell>
            <DataTableCell className="font-mono text-xs">{renderPorts(row.traffic.destinationPorts)}</DataTableCell>
            <DataTableCell className="text-xs">{row.traffic.serviceReference ?? "—"}</DataTableCell>
            <DataTableCell>
              <details className="text-xs">
                <summary className="cursor-pointer font-semibold text-[var(--napms-color-primary)]">View</summary>
                <dl className="mt-2 grid gap-1 text-[var(--napms-color-text-body)]">
                  <div><dt className="inline font-semibold">Scope/state: </dt><dd className="inline">{row.governanceScope} / {row.operationalState}</dd></div>
                  <div><dt className="inline font-semibold">Semantic identity: </dt><dd className="inline font-mono">{row.semanticIdentity.sourceComponentDeploymentId} → {row.semanticIdentity.destinationComponentDeploymentId} / {row.semanticIdentity.dcsContractRevisionId}</dd></div>
                  <div><dt className="inline font-semibold">Effective window: </dt><dd className="inline">{row.effectiveWindow ? `${row.effectiveWindow.start} → ${row.effectiveWindow.end}` : "No restriction"}</dd></div>
                  <div><dt className="inline font-semibold">Snapshot asOf: </dt><dd className="inline font-mono">{row.snapshotAsOf}</dd></div>
                  <div><dt className="inline font-semibold">Read authority: </dt><dd className="inline font-mono">{row.readAuthorityReference}</dd></div>
                  <div><dt className="inline font-semibold">ACC fact: </dt><dd className="inline font-mono">{row.applicationCommunicationCatalogue.factReference}</dd></div>
                  <div><dt className="inline font-semibold">ACC validity: </dt><dd className="inline font-mono">{row.applicationCommunicationCatalogue.validityReference}</dd></div>
                  <div><dt className="inline font-semibold">ACC provenance: </dt><dd className="inline font-mono">{row.applicationCommunicationCatalogue.provenanceReference}</dd></div>
                  <div><dt className="inline font-semibold">Source fact: </dt><dd className="inline font-mono">{row.source.factReference}</dd></div>
                  <div><dt className="inline font-semibold">Source validity: </dt><dd className="inline font-mono">{row.source.validityReference}</dd></div>
                  <div><dt className="inline font-semibold">Source provenance: </dt><dd className="inline font-mono">{row.source.provenanceReference}</dd></div>
                  <div><dt className="inline font-semibold">Destination fact: </dt><dd className="inline font-mono">{row.destination.factReference}</dd></div>
                  <div><dt className="inline font-semibold">Destination validity: </dt><dd className="inline font-mono">{row.destination.validityReference}</dd></div>
                  <div><dt className="inline font-semibold">Destination provenance: </dt><dd className="inline font-mono">{row.destination.provenanceReference}</dd></div>
                </dl>
              </details>
            </DataTableCell>
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  )
}
