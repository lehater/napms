import { StatusIndicator } from "@/design-system/components/StatusIndicator"
import {
  DetailRow,
  DetailSection,
} from "@/design-system/patterns/detail/Detail"
import type { ResourceDetailDto } from "@/features/catalogues/api/catalogue"
import { shortId } from "@/features/catalogues/components/CatalogueIdentity"
import type { ResourceHistoryDto } from "@/features/catalogues/api/resourceHistory"

export function formatResourceDate(value: string) {
  return new Date(value).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

type HistoryEvent = {
  key: string
  at: string
  title: string
  summary: string
  detail?: string
}

function roleLabel(role: ResourceDetailDto["effectiveResponsibilities"][number]["role"]) {
  return {
    TechnicalOwner: "Technical owner",
    ServiceOwner: "Service owner",
    OperationsContact: "Operations contact",
    BusinessOwner: "Business owner",
  }[role]
}

function historyEvents(history: ResourceHistoryDto | null): HistoryEvent[] {
  if (!history) return []
  const values: HistoryEvent[] = []

  for (const item of history.realizations) {
    const addresses = item.technicalAddresses.map((value) => value.technicalAddress).join(", ")
    values.push({
      key: `realization-start:${item.factReference}`,
      at: item.validFrom,
      title: "Technical realization started",
      summary: addresses || "Technical addresses recorded",
      detail: `Fact ${shortId(item.factReference)} · v${item.version}`,
    })
    if (item.validTo) {
      values.push({
        key: `realization-end:${item.factReference}`,
        at: item.validTo,
        title: "Technical realization ended",
        summary: addresses || "Technical addresses ended",
      })
    }
  }

  for (const item of history.scopeAffiliations) {
    values.push({
      key: `scope-start:${item.affiliationReference}`,
      at: item.validFrom,
      title: "Scope affiliation added",
      summary: item.responsibilityScope,
    })
    if (item.validTo) {
      values.push({
        key: `scope-end:${item.affiliationReference}`,
        at: item.validTo,
        title: "Scope affiliation ended",
        summary: item.responsibilityScope,
      })
    }
  }

  for (const item of history.responsibilities) {
    values.push({
      key: `responsibility-start:${item.assignmentReference}`,
      at: item.validFrom,
      title: "Responsibility assigned",
      summary: `${roleLabel(item.role)} · ${item.displayName}`,
      detail: item.contact || undefined,
    })
    if (item.validTo) {
      values.push({
        key: `responsibility-end:${item.assignmentReference}`,
        at: item.validTo,
        title: "Responsibility ended",
        summary: `${roleLabel(item.role)} · ${item.displayName}`,
      })
    }
  }

  return values.sort((a, b) => new Date(b.at).getTime() - new Date(a.at).getTime())
}

export function ResourceBasicInformation({
  detail,
}: {
  detail: ResourceDetailDto
}) {
  const resourceActive = detail.resource.lifecycle === "Active"
  const currentName = detail.resource.displayName || shortId(detail.resource.resourceReference)

  return (
    <DetailSection title="Basic information">
      <DetailRow label="Name">{currentName}</DetailRow>
      <DetailRow label="Reference">
        <span className="font-mono text-xs">{detail.resource.resourceReference}</span>
      </DetailRow>
      <DetailRow label="Lifecycle">
        <StatusIndicator tone={resourceActive ? "positive" : "critical"}>
          {detail.resource.lifecycle}
        </StatusIndicator>
      </DetailRow>
      <DetailRow label="Current as of">{formatResourceDate(detail.asOf)}</DetailRow>
    </DetailSection>
  )
}

export function ResourceHistorySection({
  history,
}: {
  history: ResourceHistoryDto | null
}) {
  const events = historyEvents(history)

  return (
    <DetailSection title="Resource history">
      <div className="grid gap-3">
        {events.length ? (
          events.map((event) => (
            <div
              key={event.key}
              className="grid gap-1 border-l-2 border-[var(--napms-color-primary-border)] pl-4 sm:grid-cols-[170px_minmax(0,1fr)]"
            >
              <div className="text-xs text-[var(--napms-color-text-secondary)]">
                {formatResourceDate(event.at)}
              </div>
              <div>
                <div className="text-sm font-semibold text-[var(--napms-color-text-primary)]">
                  {event.title}
                </div>
                <div className="text-sm text-[var(--napms-color-text-body)]">
                  {event.summary}
                </div>
                {event.detail ? (
                  <div className="text-xs text-[var(--napms-color-text-secondary)]">
                    {event.detail}
                  </div>
                ) : null}
              </div>
            </div>
          ))
        ) : (
          <p className="text-sm text-[var(--napms-color-text-secondary)]">
            No historical facts recorded.
          </p>
        )}
      </div>
    </DetailSection>
  )
}

export function ResourceTechnicalDetails({
  detail,
}: {
  detail: ResourceDetailDto
}) {
  return (
    <DetailSection title="Technical details">
      <div className="grid gap-1 md:grid-cols-2 md:gap-x-8">
        <DetailRow label="Resource reference">
          <span className="font-mono text-xs">{detail.resource.resourceReference}</span>
        </DetailRow>
        <DetailRow label="Version">{detail.resource.version}</DetailRow>
        <DetailRow label="Provenance">
          <span className="font-mono text-xs">{detail.resource.provenanceReference}</span>
        </DetailRow>
        <DetailRow label="Retirement provenance">
          {detail.resource.retirementProvenanceReference ? (
            <span className="font-mono text-xs">
              {detail.resource.retirementProvenanceReference}
            </span>
          ) : "—"}
        </DetailRow>
      </div>
      <div className="mt-4 border-t border-[var(--napms-color-border)] pt-4">
        <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-[var(--napms-color-text-secondary)]">
          Current fact references
        </h3>
        <div className="grid gap-2 text-xs text-[var(--napms-color-text-body)] md:grid-cols-2">
          {detail.effectiveRealizations.map((item) => (
            <div key={item.factReference}>
              Realization · <span className="font-mono">{item.factReference}</span> · v{item.version}
            </div>
          ))}
          {detail.effectiveScopeAffiliations.map((item) => (
            <div key={item.affiliationReference}>
              Scope · <span className="font-mono">{item.affiliationReference}</span> · v{item.version}
            </div>
          ))}
          {detail.effectiveResponsibilities.map((item) => (
            <div key={item.assignmentReference}>
              Responsibility · <span className="font-mono">{item.assignmentReference}</span> · v{item.version}
            </div>
          ))}
        </div>
      </div>
    </DetailSection>
  )
}
