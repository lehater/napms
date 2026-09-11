import { DetailRow, DetailSection } from "@/design-system/patterns/detail/Detail"
import {
  CatalogueIdentity,
  trafficAlternativeText,
} from "@/features/catalogues/components/CatalogueIdentity"
import type { RuleDetailResponse } from "@/features/rules/api"

export function AccessRuleDetailSections({ detail, onOpenDecision }: { detail: RuleDetailResponse; onOpenDecision: (decisionId: string) => void }) {
  const rule = detail.rule
  return <>
    <DetailSection title="Semantic identity">
      <div className="grid gap-4 lg:grid-cols-2">
        <DetailRow label="Source Component Deployment"><CatalogueIdentity name={rule.catalogue?.sourceDisplayName} id={rule.semanticIdentity.sourceComponentDeploymentId} /></DetailRow>
        <DetailRow label="Destination Component Deployment"><CatalogueIdentity name={rule.catalogue?.destinationDisplayName} id={rule.semanticIdentity.destinationComponentDeploymentId} /></DetailRow>
        <DetailRow label="DCS revision"><CatalogueIdentity name={rule.catalogue?.dcsDisplayName} id={rule.semanticIdentity.dcsContractRevisionId} />{(rule.catalogue?.trafficAlternatives.length ?? 0) > 0 ? <div className="mt-2 grid gap-1 text-xs text-[#64748B]">{rule.catalogue?.trafficAlternatives.map((alternative, index) => <div key={index}>{trafficAlternativeText(alternative)}</div>)}</div> : null}</DetailRow>
        <DetailRow label="Governance scope">{rule.governanceScope}</DetailRow>
        <DetailRow label="Decision reference">{rule.decisionReference ? <button type="button" className="break-all font-mono text-xs text-[#2563EB] hover:underline" onClick={() => onOpenDecision(rule.decisionReference as string)}>{rule.decisionReference}</button> : "—"}</DetailRow>
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
      {rule.stateHistory.length === 0 ? <p className="text-sm text-[#64748B]">No operational-state transitions have been recorded.</p> : <div className="overflow-x-auto"><table className="w-full min-w-[760px] text-left text-sm"><thead className="text-xs uppercase tracking-wide text-[#64748B]"><tr><th className="pb-3 font-semibold">Transition</th><th className="pb-3 font-semibold">Actor</th><th className="pb-3 font-semibold">Effective time</th><th className="pb-3 font-semibold">Authority</th></tr></thead><tbody>{rule.stateHistory.map((item, index) => <tr key={`${item.effectiveTime}-${index}`} className="border-t border-[#E2E8F0]"><td className="py-3">{item.fromState} → {item.toState}</td><td className="py-3">{item.actorId}</td><td className="py-3">{item.effectiveTime}</td><td className="py-3 font-mono text-xs">{item.authorityReference}</td></tr>)}</tbody></table></div>}
    </DetailSection>

    <DetailSection title="EffectiveWindow history">
      {rule.effectiveWindowHistory.length === 0 ? <p className="text-sm text-[#64748B]">No EffectiveWindow changes have been recorded.</p> : <div className="overflow-x-auto"><table className="w-full min-w-[880px] text-left text-sm"><thead className="text-xs uppercase tracking-wide text-[#64748B]"><tr><th className="pb-3 font-semibold">Previous</th><th className="pb-3 font-semibold">New</th><th className="pb-3 font-semibold">Actor</th><th className="pb-3 font-semibold">Effective time</th><th className="pb-3 font-semibold">Authority</th></tr></thead><tbody>{rule.effectiveWindowHistory.map((item, index) => <tr key={`${item.effectiveTime}-window-${index}`} className="border-t border-[#E2E8F0]"><td className="py-3 text-xs">{item.previousWindow ? `${item.previousWindow.start} → ${item.previousWindow.end}` : "No restriction"}</td><td className="py-3 text-xs">{item.newWindow ? `${item.newWindow.start} → ${item.newWindow.end}` : "No restriction"}</td><td className="py-3">{item.actorId}</td><td className="py-3">{item.effectiveTime}</td><td className="py-3 font-mono text-xs">{item.authorityReference}</td></tr>)}</tbody></table></div>}
    </DetailSection>
  </>
}
