import { useEffect, useState } from "react"
import { ArrowLeft, CircleAlert } from "lucide-react"

import {
  ApiError,
  getAccessRule,
  setAccessRuleEffectiveWindow,
  setAccessRuleOperationalState,
  type RuleDetailResponse,
} from "@/api"
import {
  CatalogueIdentity,
  displayName,
  trafficAlternativeText,
} from "@/components/catalogue/CatalogueIdentity"
import { Button } from "@/components/ui/Button"
import { StatusBadge } from "@/components/ui/StatusBadge"
import { toLocalDateTimeInput, toOffsetAwareIso } from "@/lib/datetime"

function valueOrDash(value: string | null | undefined) {
  return value ?? "—"
}

export function AccessRuleDetailsPage({
  ruleId,
  onBack,
}: {
  ruleId: string
  onBack: () => void
}) {
  const [detail, setDetail] = useState<RuleDetailResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [mutating, setMutating] = useState(false)
  const [windowMutating, setWindowMutating] = useState(false)
  const [windowStart, setWindowStart] = useState("")
  const [windowEnd, setWindowEnd] = useState("")
  const [error, setError] = useState<ApiError | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const response = await getAccessRule(ruleId)
      setDetail(response)
      setWindowStart(
        toLocalDateTimeInput(response.rule.effectiveWindow?.start ?? null),
      )
      setWindowEnd(
        toLocalDateTimeInput(response.rule.effectiveWindow?.end ?? null),
      )
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught
          : new ApiError(500, "InternalError", "Access Rule could not be loaded."),
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [ruleId])

  async function changeState() {
    if (!detail || detail.capabilities.setOperationalState !== "Permitted") return
    const targetState =
      detail.rule.operationalState === "Active" ? "Inactive" : "Active"

    setMutating(true)
    setError(null)
    setMessage(null)
    try {
      const result = await setAccessRuleOperationalState(ruleId, targetState)
      setMessage(
        result.outcome === "Updated"
          ? `Rule state changed to ${targetState}.`
          : `Rule is already ${targetState}.`,
      )
      await load()
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught
          : new ApiError(500, "InternalError", "Rule state could not be changed."),
      )
    } finally {
      setMutating(false)
    }
  }

  async function saveWindow() {
    if (!detail || detail.capabilities.setEffectiveWindow !== "Permitted") return
    setWindowMutating(true)
    setError(null)
    setMessage(null)
    try {
      const start = toOffsetAwareIso(windowStart)
      const end = toOffsetAwareIso(windowEnd)
      const result = await setAccessRuleEffectiveWindow(ruleId, { start, end })
      setMessage(
        result.outcome === "Updated"
          ? "EffectiveWindow updated."
          : "Rule already has this EffectiveWindow.",
      )
      await load()
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught
          : new ApiError(
              422,
              "InvalidEffectiveWindow",
              "Select a valid start and end time.",
            ),
      )
    } finally {
      setWindowMutating(false)
    }
  }

  async function clearWindow() {
    if (!detail || detail.capabilities.setEffectiveWindow !== "Permitted") return
    setWindowMutating(true)
    setError(null)
    setMessage(null)
    try {
      const result = await setAccessRuleEffectiveWindow(ruleId, null)
      setMessage(
        result.outcome === "Updated"
          ? "EffectiveWindow cleared."
          : "Rule already has no EffectiveWindow restriction.",
      )
      await load()
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught
          : new ApiError(500, "InternalError", "EffectiveWindow could not be cleared."),
      )
    } finally {
      setWindowMutating(false)
    }
  }

  return (
    <div className="mx-auto max-w-[1180px]">
      <div className="mb-4">
        <Button variant="ghost" onClick={onBack}>
          <ArrowLeft className="size-4" aria-hidden="true" />
          Access Rules
        </Button>
      </div>

      <header className="mb-6">
        <div className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#5F6B7D]">
          Access Policy / Rule Details
        </div>
        <h1 className="break-all text-[28px] font-bold tracking-tight text-[#172033]">
          {ruleId}
        </h1>
        {detail ? (
          <p className="mt-2 text-sm text-[#5F6B7D]">
            {displayName(
              detail.rule.catalogue?.sourceDisplayName,
              detail.rule.semanticIdentity.sourceComponentDeploymentId,
            )}{" "}
            →{" "}
            {displayName(
              detail.rule.catalogue?.destinationDisplayName,
              detail.rule.semanticIdentity.destinationComponentDeploymentId,
            )}{" "}
            ·{" "}
            {displayName(
              detail.rule.catalogue?.dcsDisplayName,
              detail.rule.semanticIdentity.dcsContractRevisionId,
            )}
          </p>
        ) : null}
      </header>

      {error ? (
        <div
          role="alert"
          className="mb-4 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800"
        >
          <div className="flex gap-3">
            <CircleAlert className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
            <div>
              <div className="font-semibold">{error.code}</div>
              <div className="mt-1">{error.message}</div>
              {error.correlationId ? (
                <div className="mt-2 text-xs">Correlation: {error.correlationId}</div>
              ) : null}
            </div>
          </div>
        </div>
      ) : null}

      {message ? (
        <div
          role="status"
          className="mb-4 rounded-md border border-green-200 bg-green-50 p-4 text-sm text-green-800"
        >
          {message}
        </div>
      ) : null}

      {loading && !detail ? (
        <div className="rounded-lg border border-[#E2E8F0] bg-white p-8 text-sm text-[#5F6B7D]">
          Loading Access Rule…
        </div>
      ) : detail ? (
        <div className="grid gap-6">
          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h2 className="text-base font-semibold text-[#172033]">
                  Operational state
                </h2>
                <div className="mt-3 flex items-center gap-3">
                  <StatusBadge value={detail.rule.operationalState} />
                  <span className="text-xs text-[#5F6B7D]">
                    mutation: {detail.capabilities.setOperationalState}
                  </span>
                </div>
              </div>
              {detail.capabilities.setOperationalState === "Permitted" ? (
                <Button loading={mutating} onClick={() => void changeState()}>
                  Set {detail.rule.operationalState === "Active" ? "Inactive" : "Active"}
                </Button>
              ) : null}
            </div>
          </section>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h2 className="text-base font-semibold text-[#172033]">
                  EffectiveWindow
                </h2>
                <p className="mt-1 text-sm text-[#5F6B7D]">
                  Half-open interval: start ≤ asOf &lt; end. No window means no
                  time-window restriction.
                </p>
                <div className="mt-2 text-xs text-[#5F6B7D]">
                  mutation: {detail.capabilities.setEffectiveWindow}
                </div>
              </div>
            </div>

            <div className="mt-5 grid gap-4 lg:grid-cols-2">
              <label className="grid gap-2 text-sm font-medium text-[#334155]">
                Start
                <input
                  type="datetime-local"
                  step="1"
                  value={windowStart}
                  onChange={(event) => setWindowStart(event.target.value)}
                  disabled={detail.capabilities.setEffectiveWindow !== "Permitted"}
                  className="min-h-10 rounded-md border border-[#CBD5E1] px-3 py-2 disabled:bg-[#F8FAFC]"
                />
              </label>
              <label className="grid gap-2 text-sm font-medium text-[#334155]">
                End
                <input
                  type="datetime-local"
                  step="1"
                  value={windowEnd}
                  onChange={(event) => setWindowEnd(event.target.value)}
                  disabled={detail.capabilities.setEffectiveWindow !== "Permitted"}
                  className="min-h-10 rounded-md border border-[#CBD5E1] px-3 py-2 disabled:bg-[#F8FAFC]"
                />
              </label>
            </div>

            {detail.capabilities.setEffectiveWindow === "Permitted" ? (
              <div className="mt-4 flex flex-wrap justify-end gap-2">
                <Button
                  variant="secondary"
                  loading={windowMutating}
                  disabled={!detail.rule.effectiveWindow}
                  onClick={() => void clearWindow()}
                >
                  Clear window
                </Button>
                <Button
                  loading={windowMutating}
                  disabled={!windowStart || !windowEnd}
                  onClick={() => void saveWindow()}
                >
                  Save window
                </Button>
              </div>
            ) : null}
          </section>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <h2 className="text-base font-semibold text-[#172033]">
              Semantic identity
            </h2>
            <dl className="mt-4 grid gap-4 text-sm lg:grid-cols-2">
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#5F6B7D]">
                  Source Component Deployment
                </dt>
                <dd className="mt-1">
                  <CatalogueIdentity
                    name={detail.rule.catalogue?.sourceDisplayName}
                    id={detail.rule.semanticIdentity.sourceComponentDeploymentId}
                  />
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#5F6B7D]">
                  Destination Component Deployment
                </dt>
                <dd className="mt-1">
                  <CatalogueIdentity
                    name={detail.rule.catalogue?.destinationDisplayName}
                    id={detail.rule.semanticIdentity.destinationComponentDeploymentId}
                  />
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#5F6B7D]">
                  DCS revision
                </dt>
                <dd className="mt-1">
                  <CatalogueIdentity
                    name={detail.rule.catalogue?.dcsDisplayName}
                    id={detail.rule.semanticIdentity.dcsContractRevisionId}
                  />
                  {(detail.rule.catalogue?.trafficAlternatives.length ?? 0) > 0 ? (
                    <div className="mt-2 grid gap-1 text-xs text-[#5F6B7D]">
                      {detail.rule.catalogue?.trafficAlternatives.map(
                        (alternative, index) => (
                          <div key={index}>{trafficAlternativeText(alternative)}</div>
                        ),
                      )}
                    </div>
                  ) : null}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#5F6B7D]">
                  Governance scope
                </dt>
                <dd className="mt-1">{detail.rule.governanceScope}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#5F6B7D]">
                  Decision reference
                </dt>
                <dd className="mt-1 break-all font-mono">
                  {valueOrDash(detail.rule.decisionReference)}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#5F6B7D]">
                  Effective window
                </dt>
                <dd className="mt-1">
                  {detail.rule.effectiveWindow
                    ? `${detail.rule.effectiveWindow.start} → ${detail.rule.effectiveWindow.end}`
                    : "No restriction"}
                </dd>
              </div>
            </dl>
          </section>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <h2 className="text-base font-semibold text-[#172033]">
              Proposal provenance
            </h2>
            <dl className="mt-4 grid gap-4 text-sm lg:grid-cols-2">
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#5F6B7D]">
                  Actor
                </dt>
                <dd className="mt-1">{detail.rule.proposalProvenance.actorId}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#5F6B7D]">
                  Effective time
                </dt>
                <dd className="mt-1">{detail.rule.proposalProvenance.effectiveTime}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#5F6B7D]">
                  Authority reference
                </dt>
                <dd className="mt-1 break-all font-mono">
                  {detail.rule.proposalProvenance.authorityReference}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#5F6B7D]">
                  Catalogue reference
                </dt>
                <dd className="mt-1 break-all font-mono">
                  {detail.rule.proposalProvenance.catalogueReference}
                </dd>
              </div>
            </dl>
          </section>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <h2 className="text-base font-semibold text-[#172033]">State history</h2>
            {detail.rule.stateHistory.length === 0 ? (
              <p className="mt-3 text-sm text-[#5F6B7D]">
                No operational-state transitions have been recorded.
              </p>
            ) : (
              <div className="mt-4 overflow-x-auto">
                <table className="w-full min-w-[760px] text-left text-sm">
                  <thead className="text-xs uppercase tracking-wide text-[#5F6B7D]">
                    <tr>
                      <th className="pb-3 font-semibold">Transition</th>
                      <th className="pb-3 font-semibold">Actor</th>
                      <th className="pb-3 font-semibold">Effective time</th>
                      <th className="pb-3 font-semibold">Authority</th>
                    </tr>
                  </thead>
                  <tbody>
                    {detail.rule.stateHistory.map((item, index) => (
                      <tr
                        key={`${item.effectiveTime}-${index}`}
                        className="border-t border-[#E2E8F0]"
                      >
                        <td className="py-3">
                          {item.fromState} → {item.toState}
                        </td>
                        <td className="py-3">{item.actorId}</td>
                        <td className="py-3">{item.effectiveTime}</td>
                        <td className="py-3 font-mono text-xs">
                          {item.authorityReference}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <h2 className="text-base font-semibold text-[#172033]">
              EffectiveWindow history
            </h2>
            {detail.rule.effectiveWindowHistory.length === 0 ? (
              <p className="mt-3 text-sm text-[#5F6B7D]">
                No EffectiveWindow changes have been recorded.
              </p>
            ) : (
              <div className="mt-4 overflow-x-auto">
                <table className="w-full min-w-[880px] text-left text-sm">
                  <thead className="text-xs uppercase tracking-wide text-[#5F6B7D]">
                    <tr>
                      <th className="pb-3 font-semibold">Previous</th>
                      <th className="pb-3 font-semibold">New</th>
                      <th className="pb-3 font-semibold">Actor</th>
                      <th className="pb-3 font-semibold">Effective time</th>
                      <th className="pb-3 font-semibold">Authority</th>
                    </tr>
                  </thead>
                  <tbody>
                    {detail.rule.effectiveWindowHistory.map((item, index) => (
                      <tr
                        key={`${item.effectiveTime}-window-${index}`}
                        className="border-t border-[#E2E8F0]"
                      >
                        <td className="py-3 text-xs">
                          {item.previousWindow
                            ? `${item.previousWindow.start} → ${item.previousWindow.end}`
                            : "No restriction"}
                        </td>
                        <td className="py-3 text-xs">
                          {item.newWindow
                            ? `${item.newWindow.start} → ${item.newWindow.end}`
                            : "No restriction"}
                        </td>
                        <td className="py-3">{item.actorId}</td>
                        <td className="py-3">{item.effectiveTime}</td>
                        <td className="py-3 font-mono text-xs">
                          {item.authorityReference}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </div>
      ) : null}
    </div>
  )
}
