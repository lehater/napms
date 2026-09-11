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
    <section className="mb-5 overflow-hidden rounded-lg border border-[#E2E8F0] bg-white">
      <div className="border-b border-[#E2E8F0] px-5 py-4">
        <h2 className="text-base font-semibold text-[#172033]">
          Connectivity context
        </h2>
        <p className="mt-1 text-xs text-[#64748B]">
          Scope {scope} · Resource {resourceReference}
        </p>
      </div>

      {loading ? (
        <div className="p-6 text-sm text-[#64748B]">
          Loading exact interaction…
        </div>
      ) : (
        <dl className="grid gap-0 sm:grid-cols-2">
          <div className="border-b border-[#E2E8F0] px-5 py-4 sm:border-r">
            <dt className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">
              My component
            </dt>
            <dd className="mt-1 font-medium text-[#172033]">{localLabel}</dd>
            <dd className="mt-1 text-xs text-[#64748B]">{direction}</dd>
          </div>
          <div className="border-b border-[#E2E8F0] px-5 py-4">
            <dt className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">
              Remote component
            </dt>
            <dd className="mt-1 font-medium text-[#172033]">{remoteLabel}</dd>
          </div>
          <div className="px-5 py-4 sm:border-r">
            <dt className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">
              Access
            </dt>
            <dd className="mt-1 font-medium text-[#172033]">{accessLabel}</dd>
            {trafficText ? (
              <dd className="mt-1 font-mono text-xs text-[#64748B]">{trafficText}</dd>
            ) : null}
          </div>
          <div className="px-5 py-4">
            <dt className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">
              Need
            </dt>
            <dd className="mt-1 text-sm text-[#334155]">
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
