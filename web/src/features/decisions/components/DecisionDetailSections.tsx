import { DetailRow, DetailSection } from "@/design-system/patterns/detail/Detail"
import {
  CatalogueIdentity,
  shortId,
} from "@/features/catalogues/components/CatalogueIdentity"
import type { ConnectivityDecisionDetailResponse } from "@/features/decisions/api"
import {
  DecisionOutcomeStatus,
  decisionValidityText,
} from "@/features/decisions/components/DecisionStatus"

export function DecisionSubjectSection({
  detail,
}: {
  detail: ConnectivityDecisionDetailResponse
}) {
  const decision = detail.decision
  return (
    <DetailSection title="Exact subject">
      <div className="grid gap-5 md:grid-cols-3">
        <div>
          <div className="mb-2 text-xs uppercase tracking-wide text-[var(--napms-color-text-secondary)]">Source</div>
          <CatalogueIdentity
            name={decision.catalogue?.sourceDisplayName}
            id={decision.subject.sourceComponentDeploymentId}
          />
        </div>
        <div>
          <div className="mb-2 text-xs uppercase tracking-wide text-[var(--napms-color-text-secondary)]">Destination</div>
          <CatalogueIdentity
            name={decision.catalogue?.destinationDisplayName}
            id={decision.subject.destinationComponentDeploymentId}
          />
        </div>
        <div>
          <div className="mb-2 text-xs uppercase tracking-wide text-[var(--napms-color-text-secondary)]">DCS / Access</div>
          <CatalogueIdentity
            name={decision.catalogue?.dcsDisplayName}
            id={decision.subject.dcsContractRevisionId}
          />
        </div>
      </div>
      <div className="mt-6 grid gap-1 border-t border-[var(--napms-color-border)] pt-5 md:grid-cols-2 md:gap-x-8">
        <DetailRow label="Governance scope">{decision.governanceScope}</DetailRow>
        <DetailRow label="Decision ID">
          <span className="break-all font-mono text-xs">{decision.decisionId}</span>
        </DetailRow>
      </div>
    </DetailSection>
  )
}

export function DecisionReasonSection({
  detail,
}: {
  detail: ConnectivityDecisionDetailResponse
}) {
  const decision = detail.decision
  return (
    <DetailSection title="Reason and validity">
      <div className="grid gap-1">
        <DetailRow label="Outcome">
          <DecisionOutcomeStatus outcome={decision.outcome} />
        </DetailRow>
        <DetailRow label="Reason code">{decision.reason.code}</DetailRow>
        <DetailRow label="Reason">
          <span className="whitespace-pre-wrap">{decision.reason.text}</span>
        </DetailRow>
        <DetailRow label="Validity">{decisionValidityText(decision)}</DetailRow>
      </div>
    </DetailSection>
  )
}

export function DecisionEvidenceSection({
  detail,
  onOpenRequirement,
}: {
  detail: ConnectivityDecisionDetailResponse
  onOpenRequirement: (requirementId: string) => void
}) {
  const references = detail.decision.evidenceReferences
  return (
    <DetailSection title="Evidence references">
      {references.length === 0 ? (
        <p className="text-sm text-[var(--napms-color-text-secondary)]">No evidence references were recorded.</p>
      ) : (
        <div className="grid gap-3">
          {references.map((item, index) => (
            <DetailRow key={`${item.kind}-${item.reference}-${index}`} label={item.kind}>
              {item.kind === "ConnectivityRequirement" ? (
                <button
                  type="button"
                  className="break-all font-mono text-xs font-semibold text-[var(--napms-color-primary)] hover:underline"
                  onClick={() => onOpenRequirement(item.reference)}
                >
                  {item.reference}
                </button>
              ) : (
                <span className="break-all">{item.reference}</span>
              )}
            </DetailRow>
          ))}
        </div>
      )}
    </DetailSection>
  )
}

export function DecisionProvenanceSection({
  detail,
}: {
  detail: ConnectivityDecisionDetailResponse
}) {
  const decision = detail.decision
  return (
    <DetailSection title="Authority provenance">
      <div className="grid gap-1 md:grid-cols-2 md:gap-x-8">
        <DetailRow label="Deciding actor">{decision.provenance.actorId}</DetailRow>
        <DetailRow label="Decided at">{decision.provenance.decidedAt}</DetailRow>
        <DetailRow label="Decide authority">
          <span className="break-all font-mono text-xs">{decision.provenance.authorityReference}</span>
        </DetailRow>
        <DetailRow label="Read authority">
          <span className="break-all font-mono text-xs">{detail.readAuthorityReference}</span>
        </DetailRow>
      </div>
    </DetailSection>
  )
}

export function DecisionSupersessionSection({
  detail,
  onOpenDecision,
}: {
  detail: ConnectivityDecisionDetailResponse
  onOpenDecision: (decisionId: string) => void
}) {
  const previous = detail.decision.supersedesDecisionId
  return (
    <DetailSection title="Supersession">
      {previous ? (
        <p className="text-sm text-[var(--napms-color-text-body)]">
          This Decision explicitly supersedes{" "}
          <button
            type="button"
            className="font-mono text-xs font-semibold text-[var(--napms-color-primary)] hover:underline"
            onClick={() => onOpenDecision(previous)}
          >
            {shortId(previous)}
          </button>
          .
        </p>
      ) : (
        <p className="text-sm text-[var(--napms-color-text-secondary)]">This Decision does not supersede an earlier Decision.</p>
      )}
    </DetailSection>
  )
}
