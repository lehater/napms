import {
  DataTable,
  DataTableBody,
  DataTableCell,
  DataTableHeadCell,
  DataTableHeader,
  DataTableHeaderRow,
  DataTableRow,
} from "@/design-system/components/DataTable"
import { CatalogueIdentity, shortId } from "@/features/catalogues/components/CatalogueIdentity"
import type { EffectivePolicyResponse } from "@/features/policy/api"
import { RuleOperationalStatus } from "@/features/rules/components/RuleStatus"

export function EffectivePolicyTable({
  rules,
  onOpenRule,
}: {
  rules: EffectivePolicyResponse["rules"]
  onOpenRule: (ruleId: string) => void
}) {
  return (
    <DataTable minWidth={980}>
      <DataTableHeader>
        <DataTableHeaderRow>
          <DataTableHeadCell>Rule</DataTableHeadCell>
          <DataTableHeadCell>Source</DataTableHeadCell>
          <DataTableHeadCell>Destination</DataTableHeadCell>
          <DataTableHeadCell>DCS revision</DataTableHeadCell>
          <DataTableHeadCell>State</DataTableHeadCell>
          <DataTableHeadCell>Effective window</DataTableHeadCell>
        </DataTableHeaderRow>
      </DataTableHeader>
      <DataTableBody>
        {rules.map((rule) => (
          <DataTableRow key={rule.ruleId}>
            <DataTableCell>
              <button type="button" className="font-mono text-xs text-[var(--napms-color-primary)] hover:underline" onClick={() => onOpenRule(rule.ruleId)}>{shortId(rule.ruleId)}</button>
            </DataTableCell>
            <DataTableCell><CatalogueIdentity name={rule.catalogue?.sourceDisplayName} id={rule.semanticIdentity.sourceComponentDeploymentId} /></DataTableCell>
            <DataTableCell><CatalogueIdentity name={rule.catalogue?.destinationDisplayName} id={rule.semanticIdentity.destinationComponentDeploymentId} /></DataTableCell>
            <DataTableCell><CatalogueIdentity name={rule.catalogue?.dcsDisplayName} id={rule.semanticIdentity.dcsContractRevisionId} /></DataTableCell>
            <DataTableCell><RuleOperationalStatus state={rule.operationalState} /></DataTableCell>
            <DataTableCell className="text-xs text-[var(--napms-color-text-body)]">{rule.effectiveWindow ? `${rule.effectiveWindow.start} → ${rule.effectiveWindow.end}` : "No restriction"}</DataTableCell>
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  )
}
