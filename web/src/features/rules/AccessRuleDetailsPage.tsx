import { useEffect, useState } from "react"
import { ArrowLeft, CircleAlert } from "lucide-react"

import {
  ApiError,
  getAccessRule,
  setAccessRuleOperationalState,
  type RuleDetailResponse,
} from "@/api"
import { Button } from "@/components/ui/Button"
import { StatusBadge } from "@/components/ui/StatusBadge"

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
  const [error, setError] = useState<ApiError | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      setDetail(await getAccessRule(ruleId))
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

  return (
    <div className="mx-auto max-w-[1180px]">
      <div className="mb-4">
        <Button variant="ghost" onClick={onBack}>
          <ArrowLeft className="size-4" aria-hidden="true" />
          Access Rules
        </Button>
      </div>

      <header className="mb-6">
        <div className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#64748B]">
          Access Policy / Rule Details
        </div>
        <h1 className="break-all text-[28px] font-bold tracking-tight text-[#172033]">
          {ruleId}
        </h1>
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
        <div className="rounded-lg border border-[#E2E8F0] bg-white p-8 text-sm text-[#64748B]">
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
                  <span className="text-xs text-[#64748B]">
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
            <h2 className="text-base font-semibold text-[#172033]">
              Semantic identity
            </h2>
            <dl className="mt-4 grid gap-4 text-sm lg:grid-cols-2">
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Source Component Deployment
                </dt>
                <dd className="mt-1 break-all font-mono">
                  {detail.rule.semanticIdentity.sourceComponentDeploymentId}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Destination Component Deployment
                </dt>
                <dd className="mt-1 break-all font-mono">
                  {detail.rule.semanticIdentity.destinationComponentDeploymentId}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  DCS revision
                </dt>
                <dd className="mt-1 break-all font-mono">
                  {detail.rule.semanticIdentity.dcsContractRevisionId}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Governance scope
                </dt>
                <dd className="mt-1">{detail.rule.governanceScope}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Decision reference
                </dt>
                <dd className="mt-1 break-all font-mono">
                  {valueOrDash(detail.rule.decisionReference)}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
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
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Actor
                </dt>
                <dd className="mt-1">{detail.rule.proposalProvenance.actorId}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Effective time
                </dt>
                <dd className="mt-1">{detail.rule.proposalProvenance.effectiveTime}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Authority reference
                </dt>
                <dd className="mt-1 break-all font-mono">
                  {detail.rule.proposalProvenance.authorityReference}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
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
              <p className="mt-3 text-sm text-[#64748B]">
                No operational-state transitions have been recorded.
              </p>
            ) : (
              <div className="mt-4 overflow-x-auto">
                <table className="w-full min-w-[760px] text-left text-sm">
                  <thead className="text-xs uppercase tracking-wide text-[#64748B]">
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
        </div>
      ) : null}
    </div>
  )
}
