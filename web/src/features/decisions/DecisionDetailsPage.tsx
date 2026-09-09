import { useEffect, useState } from "react"
import { ArrowLeft, CircleAlert, History } from "lucide-react"

import {
  ApiError,
  getConnectivityDecision,
  type ConnectivityDecisionDetailResponse,
  type ConnectivityDecisionOutcome,
} from "@/api"
import {
  CatalogueIdentity,
  displayName,
  shortId,
  trafficAlternativeText,
} from "@/components/catalogue/CatalogueIdentity"
import { Button } from "@/components/ui/Button"
import type { DecisionDraftContext } from "@/features/decisions/model"

function outcomeClasses(outcome: ConnectivityDecisionOutcome) {
  return outcome === "Allowed"
    ? "border-green-200 bg-green-50 text-green-800"
    : "border-red-200 bg-red-50 text-red-800"
}

export function DecisionDetailsPage({
  decisionId,
  onBack,
  onOpenDecision,
  onReplace,
}: {
  decisionId: string
  onBack: () => void
  onOpenDecision: (decisionId: string) => void
  onReplace: (context: DecisionDraftContext) => void
}) {
  const [detail, setDetail] =
    useState<ConnectivityDecisionDetailResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)

  useEffect(() => {
    let active = true
    setLoading(true)
    setError(null)
    void getConnectivityDecision(decisionId)
      .then((result) => {
        if (active) setDetail(result)
      })
      .catch((caught) => {
        if (!active) return
        setError(
          caught instanceof ApiError
            ? caught
            : new ApiError(
                500,
                "InternalError",
                "Connectivity Decision could not be loaded.",
              ),
        )
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [decisionId])

  const decision = detail?.decision

  return (
    <div className="mx-auto max-w-[1180px]">
      <div className="mb-4">
        <Button variant="ghost" onClick={onBack}>
          <ArrowLeft className="size-4" aria-hidden="true" />
          Decisions
        </Button>
      </div>

      <header className="mb-6">
        <div className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#64748B]">
          Policy / Decision Details
        </div>
        <h1 className="break-all text-[28px] font-bold tracking-tight text-[#172033]">
          {decisionId}
        </h1>
        {decision ? (
          <p className="mt-2 text-sm text-[#64748B]">
            {displayName(
              decision.catalogue?.sourceDisplayName,
              decision.subject.sourceComponentDeploymentId,
            )}{" "}
            →{" "}
            {displayName(
              decision.catalogue?.destinationDisplayName,
              decision.subject.destinationComponentDeploymentId,
            )}{" "}
            ·{" "}
            {displayName(
              decision.catalogue?.dcsDisplayName,
              decision.subject.dcsContractRevisionId,
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
                <div className="mt-2 text-xs">
                  Correlation: {error.correlationId}
                </div>
              ) : null}
            </div>
          </div>
        </div>
      ) : null}

      {loading && !decision ? (
        <div className="rounded-lg border border-[#E2E8F0] bg-white p-8 text-sm text-[#64748B]">
          Loading Decision…
        </div>
      ) : decision ? (
        <div className="grid gap-6">
          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h2 className="text-base font-semibold text-[#172033]">
                  Final outcome
                </h2>
                <span
                  className={`mt-3 inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${outcomeClasses(decision.outcome)}`}
                >
                  {decision.outcome}
                </span>
                <p className="mt-3 text-sm text-[#475569]">
                  {decision.reason.code} · {decision.reason.text}
                </p>
              </div>
              <Button
                onClick={() =>
                  onReplace({
                    scope: decision.governanceScope,
                    sourceComponentDeploymentId:
                      decision.subject.sourceComponentDeploymentId,
                    destinationComponentDeploymentId:
                      decision.subject.destinationComponentDeploymentId,
                    dcsContractRevisionId:
                      decision.subject.dcsContractRevisionId,
                    supersedesDecisionId: decision.decisionId,
                  })
                }
              >
                Record replacement
              </Button>
            </div>
          </section>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <h2 className="text-base font-semibold text-[#172033]">
              Exact subject and validity
            </h2>
            <dl className="mt-4 grid gap-4 text-sm lg:grid-cols-2">
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Source
                </dt>
                <dd className="mt-1">
                  <CatalogueIdentity
                    name={decision.catalogue?.sourceDisplayName}
                    id={decision.subject.sourceComponentDeploymentId}
                  />
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Destination
                </dt>
                <dd className="mt-1">
                  <CatalogueIdentity
                    name={decision.catalogue?.destinationDisplayName}
                    id={decision.subject.destinationComponentDeploymentId}
                  />
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  DCS revision
                </dt>
                <dd className="mt-1">
                  <CatalogueIdentity
                    name={decision.catalogue?.dcsDisplayName}
                    id={decision.subject.dcsContractRevisionId}
                  />
                  {(decision.catalogue?.trafficAlternatives.length ?? 0) > 0 ? (
                    <div className="mt-2 grid gap-1 text-xs text-[#64748B]">
                      {decision.catalogue?.trafficAlternatives.map(
                        (alternative, index) => (
                          <div key={index}>
                            {trafficAlternativeText(alternative)}
                          </div>
                        ),
                      )}
                    </div>
                  ) : null}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Governance scope
                </dt>
                <dd className="mt-1">{decision.governanceScope}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Valid from
                </dt>
                <dd className="mt-1">
                  {new Date(decision.validity.validFrom).toLocaleString()}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Valid until
                </dt>
                <dd className="mt-1">
                  {decision.validity.validUntil
                    ? new Date(decision.validity.validUntil).toLocaleString()
                    : "No end"}
                </dd>
              </div>
            </dl>
          </section>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <h2 className="text-base font-semibold text-[#172033]">
              Provenance and evidence
            </h2>
            <dl className="mt-4 grid gap-4 text-sm lg:grid-cols-2">
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Deciding actor
                </dt>
                <dd className="mt-1">{decision.provenance.actorId}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Decision time
                </dt>
                <dd className="mt-1">
                  {new Date(decision.provenance.decidedAt).toLocaleString()}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Decision authority
                </dt>
                <dd className="mt-1 break-all font-mono text-xs">
                  {decision.provenance.authorityReference}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Read authority
                </dt>
                <dd className="mt-1 break-all font-mono text-xs">
                  {detail?.readAuthorityReference}
                </dd>
              </div>
            </dl>

            <div className="mt-5 border-t border-[#E2E8F0] pt-4">
              <div className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">
                Evidence references
              </div>
              {decision.evidenceReferences.length === 0 ? (
                <div className="mt-2 text-sm text-[#64748B]">None</div>
              ) : (
                <ul className="mt-2 grid gap-2 text-sm">
                  {decision.evidenceReferences.map((item, index) => (
                    <li
                      key={index}
                      className="rounded-md border border-[#E2E8F0] bg-[#F8FAFC] px-3 py-2"
                    >
                      <span className="font-semibold">{item.kind}</span>
                      {" · "}
                      <span className="break-all font-mono text-xs">
                        {item.reference}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </section>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <div className="flex items-center gap-2">
              <History className="size-4 text-[#64748B]" aria-hidden="true" />
              <h2 className="text-base font-semibold text-[#172033]">
                Supersession history
              </h2>
            </div>
            {decision.supersedesDecisionId ? (
              <div className="mt-4 flex flex-wrap items-center gap-3 text-sm">
                <span className="text-[#64748B]">Supersedes</span>
                <button
                  type="button"
                  className="font-mono text-xs font-semibold text-[#2563EB] hover:text-[#1D4ED8]"
                  onClick={() =>
                    onOpenDecision(decision.supersedesDecisionId as string)
                  }
                >
                  {shortId(decision.supersedesDecisionId)}
                </button>
              </div>
            ) : (
              <p className="mt-3 text-sm text-[#64748B]">
                This Decision does not supersede an earlier Decision.
              </p>
            )}
          </section>
        </div>
      ) : null}
    </div>
  )
}
