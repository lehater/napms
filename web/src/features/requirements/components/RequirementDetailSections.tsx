import { DetailRow, DetailSection } from "@/design-system/patterns/detail/Detail"
import {
  CatalogueIdentity,
  trafficAlternativeText,
} from "@/features/catalogues/components/CatalogueIdentity"
import type {
  ConnectivityRequirementDto,
  RequirementApplicability,
} from "@/features/requirements/api"
import { requirementApplicabilityText } from "@/features/requirements/components/RequirementStatus"

export function RequirementInteractionSection({
  requirement,
}: {
  requirement: ConnectivityRequirementDto
}) {
  const interaction = requirement.requiredInteraction

  return (
    <DetailSection title="Required semantic interaction">
      <div className="grid gap-5 lg:grid-cols-2">
        <DetailRow label="Source">
          <CatalogueIdentity
            name={requirement.catalogue?.sourceDisplayName}
            id={interaction.sourceComponentDeploymentId}
          />
        </DetailRow>
        <DetailRow label="Destination">
          <CatalogueIdentity
            name={requirement.catalogue?.destinationDisplayName}
            id={interaction.destinationComponentDeploymentId}
          />
        </DetailRow>
        <DetailRow label="DCS revision">
          <div>
            <CatalogueIdentity
              name={requirement.catalogue?.dcsDisplayName}
              id={interaction.dcsContractRevisionId}
            />
            {(requirement.catalogue?.trafficAlternatives.length ?? 0) > 0 ? (
              <div className="mt-2 grid gap-1 text-xs text-[var(--napms-color-text-secondary)]">
                {requirement.catalogue?.trafficAlternatives.map((alternative, index) => (
                  <div key={index}>{trafficAlternativeText(alternative)}</div>
                ))}
              </div>
            ) : null}
          </div>
        </DetailRow>
        <DetailRow label="Dependent">
          {requirement.dependentComponentDeploymentId === interaction.sourceComponentDeploymentId ? (
            <CatalogueIdentity
              name={requirement.catalogue?.sourceDisplayName}
              id={requirement.dependentComponentDeploymentId}
            />
          ) : (
            <CatalogueIdentity
              name={requirement.catalogue?.destinationDisplayName}
              id={requirement.dependentComponentDeploymentId}
            />
          )}
        </DetailRow>
        <DetailRow label="Governance scope">{requirement.governanceScope}</DetailRow>
      </div>
    </DetailSection>
  )
}

export function RequirementProvenanceSection({
  requirement,
}: {
  requirement: ConnectivityRequirementDto
}) {
  return (
    <DetailSection title="Declaration provenance">
      <div className="grid gap-1 lg:grid-cols-2 lg:gap-x-8">
        <DetailRow label="Actor">{requirement.declarationProvenance.actorId}</DetailRow>
        <DetailRow label="Effective time">
          {requirement.declarationProvenance.effectiveTime}
        </DetailRow>
        <DetailRow label="Authority">
          <span className="break-all font-mono text-xs">
            {requirement.declarationProvenance.authorityReference}
          </span>
        </DetailRow>
        <DetailRow label="Catalogue">
          <span className="break-all font-mono text-xs">
            {requirement.declarationProvenance.catalogueReference ?? "—"}
          </span>
        </DetailRow>
      </div>
    </DetailSection>
  )
}

function ApplicabilityHistory({
  history,
}: {
  history: ConnectivityRequirementDto["applicabilityHistory"]
}) {
  if (history.length === 0) {
    return <p className="text-sm text-[var(--napms-color-text-secondary)]">No applicability changes have been recorded.</p>
  }
  return (
    <div className="grid gap-3">
      {history.map((change, index) => (
        <div key={`${change.effectiveTime}-app-${index}`} className="rounded-md border border-[var(--napms-color-border)] p-3 text-sm">
          <div>
            {requirementApplicabilityText(change.previousApplicability)} →{" "}
            {requirementApplicabilityText(change.newApplicability)}
          </div>
          <div className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">
            {change.actorId} · {change.effectiveTime} · {change.authorityReference}
          </div>
        </div>
      ))}
    </div>
  )
}

export function RequirementHistorySections({
  requirement,
}: {
  requirement: ConnectivityRequirementDto
}) {
  return (
    <>
      <DetailSection title="Applicability history">
        <ApplicabilityHistory history={requirement.applicabilityHistory} />
      </DetailSection>
      <DetailSection title="Justification history">
        {requirement.justificationHistory.length === 0 ? (
          <p className="text-sm text-[var(--napms-color-text-secondary)]">No justification changes have been recorded.</p>
        ) : (
          <div className="grid gap-3">
            {requirement.justificationHistory.map((change, index) => (
              <div key={`${change.effectiveTime}-reason-${index}`} className="rounded-md border border-[var(--napms-color-border)] p-3 text-sm">
                <div>
                  <span className="text-[var(--napms-color-text-secondary)]">{change.previousJustification}</span>{" "}
                  → {change.newJustification}
                </div>
                <div className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">
                  {change.actorId} · {change.effectiveTime} · {change.authorityReference}
                </div>
              </div>
            ))}
          </div>
        )}
      </DetailSection>
      <DetailSection title="Lifecycle history">
        {requirement.lifecycleHistory.length === 0 ? (
          <p className="text-sm text-[var(--napms-color-text-secondary)]">Requirement has not been retired.</p>
        ) : (
          <div className="grid gap-3">
            {requirement.lifecycleHistory.map((change, index) => (
              <div key={`${change.effectiveTime}-life-${index}`} className="rounded-md border border-[var(--napms-color-border)] p-3 text-sm">
                <div>{change.fromState} → {change.toState}</div>
                <div className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">
                  {change.actorId} · {change.effectiveTime} · {change.authorityReference}
                </div>
              </div>
            ))}
          </div>
        )}
      </DetailSection>
    </>
  )
}

export function applicabilityDisplay(value: RequirementApplicability) {
  return requirementApplicabilityText(value)
}
