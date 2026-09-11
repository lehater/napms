export function RequestConnectivityContextSummary({
  scope,
  resourceReference,
  localLabel,
  remoteLabel,
  direction,
  accessLabel,
  trafficText,
  needExists,
  loading,
}: {
  scope: string
  resourceReference: string
  localLabel: string
  remoteLabel: string
  direction: "Outgoing" | "Incoming"
  accessLabel: string
  trafficText: string
  needExists: boolean
  loading: boolean
}) {
  return (
    <section className="mb-5 overflow-hidden rounded-[var(--napms-surface-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)]">
      <div className="border-b border-[var(--napms-color-border)] px-5 py-4">
        <h2 className="text-base font-semibold text-[var(--napms-color-text-primary)]">
          Connectivity context
        </h2>
        <p className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">
          Scope {scope} · Resource {resourceReference}
        </p>
      </div>

      {loading ? (
        <div className="p-6 text-sm text-[var(--napms-color-text-secondary)]">
          Loading exact interaction…
        </div>
      ) : (
        <dl className="grid gap-0 sm:grid-cols-2">
          <div className="border-b border-[var(--napms-color-border)] px-5 py-4 sm:border-r">
            <dt className="text-xs font-semibold uppercase tracking-wide text-[var(--napms-color-text-secondary)]">
              My component
            </dt>
            <dd className="mt-1 font-medium text-[var(--napms-color-text-primary)]">{localLabel}</dd>
            <dd className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">{direction}</dd>
          </div>
          <div className="border-b border-[var(--napms-color-border)] px-5 py-4">
            <dt className="text-xs font-semibold uppercase tracking-wide text-[var(--napms-color-text-secondary)]">
              Remote component
            </dt>
            <dd className="mt-1 font-medium text-[var(--napms-color-text-primary)]">{remoteLabel}</dd>
          </div>
          <div className="px-5 py-4 sm:border-r">
            <dt className="text-xs font-semibold uppercase tracking-wide text-[var(--napms-color-text-secondary)]">
              Access
            </dt>
            <dd className="mt-1 font-medium text-[var(--napms-color-text-primary)]">{accessLabel}</dd>
            {trafficText ? (
              <dd className="mt-1 font-mono text-xs text-[var(--napms-color-text-secondary)]">{trafficText}</dd>
            ) : null}
          </div>
          <div className="px-5 py-4">
            <dt className="text-xs font-semibold uppercase tracking-wide text-[var(--napms-color-text-secondary)]">
              Need
            </dt>
            <dd className="mt-1 text-sm text-[var(--napms-color-text-body)]">
              {needExists
                ? "A current need already exists and will be reused."
                : "A current need will be recorded before the access proposal."}
            </dd>
          </div>
        </dl>
      )}
    </section>
  )
}
