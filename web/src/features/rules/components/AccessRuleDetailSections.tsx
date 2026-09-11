import {
  DataTable,
  DataTableBody,
  DataTableCell,
  DataTableHeadCell,
  DataTableHeader,
  DataTableHeaderRow,
  DataTableRow,
} from "@/design-system/components/DataTable"
import { DetailRow, DetailSection } from "@/design-system/patterns/detail/Detail"
import { CatalogueIdentity, trafficAlternativeText } from "@/features/catalogues/components/CatalogueIdentity"
import type { RuleDetailResponse } from "@/features/rules/api"

export function AccessRuleDetailSections({ detail, onOpenDecision }: { detail: RuleDetailResponse; onOpenDecision: (decisionId: string) => void }) {
  const rule = detail.rule
  return <>
    <DetailSection title="Semantic identity">
      <div className="grid gap-4 lg:grid-cols-2">
        <DetailRow label="Source Component Deployment"><CatalogueIdentity name={rule.catalogue?.sourceDisplayName} id={rule.semanticIdentity.sourceComponentDeploymentId} /></DetailRow>
        <DetailRow label="Destination Component Deployment"><CatalogueIdentity name={rule.catalogue?.destinationDisplayName} id={rule.semanticIdentity.destinationComponentDeploymentId} /></DetailRow>
        <DetailRow label="DCS revision"><CatalogueIdentity name={rule.catalogue?.dcsDisplayName} id={rule.semanticIdentity.dcsContractRevisionId} />{(rule.catalogue?.trafficAlternatives.length ?? 0) > 0 ? <div className="mt-2 grid gap-1 text-xs text-[var(--napms-color-text-secondary)]">{rule.catalogue?.trafficAlternatives.map((alternative, index) => <div key={index}>{trafficAlternativeText(alternative)}</div>)}</div> : null}</DetailRow>
        <DetailRow label="Governance scope">{rule.governanceScope}</DetailRow>
        <DetailRow label="Decision reference">{rule.decisionReference ? <button type="button" className="break-all font-mono text-xs text-[var(--napms-color-primary)] hover:underline" onClick={() => onOpenDecision(rule.decisionReference as string)}>{rule.decisionReference}</button> : "—"}</DetailRow>
        <DetailRow label="Effective window">{rule.effectiveWindow ? `${rule.effectiveWindow.start} → ${rule.effectiveWindow.end}` : "No restriction"}</DetailRow>
      </div>
    </DetailSection>

    <DetailSection title="Proposal provenance">
      <div className="grid gap-4 lg:grid-cols-2">
        <DetailRow label="Actor">{rule.proposalProvenance.actorId}</DetailRow>
        <DetailRow label="Effective time">{rule.proposalProvenance.effectiveTime}</DetailRow>
        <DetailRow label="Authority reference"><span className="break-all font-mono text-xs">{rule.proposalProvenance.authorityReference}</span></DetailRow>
        <DetailRow label="Catalogue reference"><span className="break-all font-mono text-xs">{rule.proposalProvenance.catalogueReference}</span></DetailRow>
      </div>
    </DetailSection>

    <DetailSection title="State history">
      {rule.stateHistory.length === 0 ? <p className="text-sm text-[var(--napms-color-text-secondary)]">No operational-state transitions have been recorded.</p> : (
        <DataTable minWidth={760}>
          <DataTableHeader><DataTableHeaderRow><DataTableHeadCell>Transition</DataTableHeadCell><DataTableHeadCell>Actor</DataTableHeadCell><DataTableHeadCell>Effective time</DataTableHeadCell><DataTableHeadCell>Authority</DataTableHeadCell></DataTableHeaderRow></DataTableHeader>
          <DataTableBody>{rule.stateHistory.map((item, index) => <DataTableRow key={`${item.effectiveTime}-${index}`}><DataTableCell>{item.fromState} → {item.toState}</DataTableCell><DataTableCell>{item.actorId}</DataTableCell><DataTableCell>{item.effectiveTime}</DataTableCell><DataTableCell className="font-mono text-xs">{item.authorityReference}</DataTableCell></DataTableRow>)}</DataTableBody>
        </DataTable>
      )}
    </DetailSection>

    <DetailSection title="EffectiveWindow history">
      {rule.effectiveWindowHistory.length === 0 ? <p className="text-sm text-[var(--napms-color-text-secondary)]">No EffectiveWindow changes have been recorded.</p> : (
        <DataTable minWidth={880}>
          <DataTableHeader><DataTableHeaderRow><DataTableHeadCell>Previous</DataTableHeadCell><DataTableHeadCell>New</DataTableHeadCell><DataTableHeadCell>Actor</DataTableHeadCell><DataTableHeadCell>Effective time</DataTableHeadCell><DataTableHeadCell>Authority</DataTableHeadCell></DataTableHeaderRow></DataTableHeader>
          <DataTableBody>{rule.effectiveWindowHistory.map((item, index) => <DataTableRow key={`${item.effectiveTime}-window-${index}`}><DataTableCell className="text-xs">{item.previousWindow ? `${item.previousWindow.start} → ${item.previousWindow.end}` : "No restriction"}</DataTableCell><DataTableCell className="text-xs">{item.newWindow ? `${item.newWindow.start} → ${item.newWindow.end}` : "No restriction"}</DataTableCell><DataTableCell>{item.actorId}</DataTableCell><DataTableCell>{item.effectiveTime}</DataTableCell><DataTableCell className="font-mono text-xs">{item.authorityReference}</DataTableCell></DataTableRow>)}</DataTableBody>
        </DataTable>
      )}
    </DetailSection>
  </>
}
