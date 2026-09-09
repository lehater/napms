import { useEffect, useMemo, useState } from "react"
import { ChevronRight, CircleAlert, Scale, Search } from "lucide-react"

import {
  ApiError,
  listConnectivityDecisionInteractions,
  listConnectivityDecisionScopes,
  listConnectivityDecisions,
  recordConnectivityDecision,
  type ConnectivityDecisionDto,
  type ConnectivityDecisionOutcome,
  type ProposalInteraction,
} from "@/api"
import {
  CatalogueIdentity,
  displayName,
  shortId,
} from "@/components/catalogue/CatalogueIdentity"
import { Button } from "@/components/ui/Button"
import { Field, Select } from "@/components/ui/Field"
import type { DecisionDraftContext } from "@/features/decisions/model"
import {
  nowLocalDateTimeInput,
  toOffsetAwareIso,
} from "@/lib/datetime"

function outcomeClasses(outcome: ConnectivityDecisionOutcome) {
  return outcome === "Allowed"
    ? "border-green-200 bg-green-50 text-green-800"
    : "border-red-200 bg-red-50 text-red-800"
}

function interactionKey(item: ProposalInteraction) {
  return [
    item.sourceComponentDeploymentId,
    item.destinationComponentDeploymentId,
    item.dcsContractRevisionId,
  ].join(":")
}

function interactionLabel(item: ProposalInteraction) {
  return `${displayName(
    item.catalogue?.sourceDisplayName,
    item.sourceComponentDeploymentId,
  )} → ${displayName(
    item.catalogue?.destinationDisplayName,
    item.destinationComponentDeploymentId,
  )} · ${displayName(
    item.catalogue?.dcsDisplayName,
    item.dcsContractRevisionId,
  )}`
}

export function DecisionsPage({
  page,
  context,
  onPageChange,
  onOpenDecision,
}: {
  page: number
  context?: DecisionDraftContext
  onPageChange: (page: number) => void
  onOpenDecision: (decisionId: string) => void
}) {
  const [decisions, setDecisions] = useState<ConnectivityDecisionDto[]>([])
  const [hasMore, setHasMore] = useState(false)
  const [ambiguousReadScopes, setAmbiguousReadScopes] = useState<string[]>([])
  const [loadingList, setLoadingList] = useState(true)
  const [listError, setListError] = useState<ApiError | null>(null)
  const [reloadToken, setReloadToken] = useState(0)

  const [scopes, setScopes] = useState<string[]>([])
  const [ambiguousDecideScopes, setAmbiguousDecideScopes] = useState<string[]>([])
  const [loadingScopes, setLoadingScopes] = useState(true)
  const [scopeError, setScopeError] = useState<ApiError | null>(null)
  const [scope, setScope] = useState(context?.scope ?? "")

  const [interactions, setInteractions] = useState<ProposalInteraction[]>([])
  const [loadingInteractions, setLoadingInteractions] = useState(false)
  const [interactionError, setInteractionError] = useState<ApiError | null>(null)
  const [interactionPage, setInteractionPage] = useState(1)
  const [hasMoreInteractions, setHasMoreInteractions] = useState(false)
  const [searchInput, setSearchInput] = useState("")
  const [search, setSearch] = useState("")
  const [selectedKey, setSelectedKey] = useState("")

  const [outcome, setOutcome] =
    useState<ConnectivityDecisionOutcome>("Allowed")
  const [validFrom, setValidFrom] = useState(nowLocalDateTimeInput)
  const [validUntil, setValidUntil] = useState("")
  const [reasonCode, setReasonCode] = useState("")
  const [reasonText, setReasonText] = useState("")
  const [evidenceKind, setEvidenceKind] = useState("")
  const [evidenceReference, setEvidenceReference] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [recordError, setRecordError] = useState<ApiError | null>(null)
  const [recordMessage, setRecordMessage] = useState<string | null>(null)

  const contextualSubject = context
    ? {
        sourceComponentDeploymentId: context.sourceComponentDeploymentId,
        destinationComponentDeploymentId: context.destinationComponentDeploymentId,
        dcsContractRevisionId: context.dcsContractRevisionId,
      }
    : null

  useEffect(() => {
    let active = true
    setLoadingList(true)
    setListError(null)
    void listConnectivityDecisions(page)
      .then((result) => {
        if (!active) return
        setDecisions(result.items)
        setHasMore(result.hasMore)
        setAmbiguousReadScopes(result.ambiguousScopes.map((item) => item.scope))
      })
      .catch((caught) => {
        if (!active) return
        setListError(
          caught instanceof ApiError
            ? caught
            : new ApiError(
                500,
                "InternalError",
                "Connectivity Decisions could not be loaded.",
              ),
        )
      })
      .finally(() => {
        if (active) setLoadingList(false)
      })
    return () => {
      active = false
    }
  }, [page, reloadToken])

  useEffect(() => {
    let active = true
    setLoadingScopes(true)
    setScopeError(null)
    void listConnectivityDecisionScopes()
      .then((result) => {
        if (!active) return
        const permitted = result.scopes.map((item) => item.scope)
        setScopes(permitted)
        setAmbiguousDecideScopes(
          result.ambiguousScopes.map((item) => item.scope),
        )
        setScope((current) => {
          if (context?.scope) return context.scope
          return current && permitted.includes(current)
            ? current
            : (permitted[0] ?? "")
        })
      })
      .catch((caught) => {
        if (!active) return
        setScopes([])
        setScopeError(
          caught instanceof ApiError
            ? caught
            : new ApiError(
                500,
                "InternalError",
                "Decision scopes could not be loaded.",
              ),
        )
      })
      .finally(() => {
        if (active) setLoadingScopes(false)
      })
    return () => {
      active = false
    }
  }, [context?.scope])

  useEffect(() => {
    if (!scope || contextualSubject) {
      setInteractions([])
      setSelectedKey("")
      setLoadingInteractions(false)
      return
    }

    let active = true
    setLoadingInteractions(true)
    setInteractionError(null)
    void listConnectivityDecisionInteractions(
      scope,
      interactionPage,
      search,
    )
      .then((result) => {
        if (!active) return
        setInteractions(result.items)
        setHasMoreInteractions(result.hasMore)
        setSelectedKey((current) =>
          result.items.some((item) => interactionKey(item) === current)
            ? current
            : "",
        )
      })
      .catch((caught) => {
        if (!active) return
        setInteractions([])
        setSelectedKey("")
        setInteractionError(
          caught instanceof ApiError
            ? caught
            : new ApiError(
                500,
                "InternalError",
                "Decision subjects could not be loaded.",
              ),
        )
      })
      .finally(() => {
        if (active) setLoadingInteractions(false)
      })

    return () => {
      active = false
    }
  }, [scope, interactionPage, search, context])

  const selectedInteraction = useMemo(
    () => interactions.find((item) => interactionKey(item) === selectedKey) ?? null,
    [interactions, selectedKey],
  )

  const selectedSubject = contextualSubject ?? selectedInteraction
  const contextScopePermitted = !context || scopes.includes(context.scope)

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    if (!selectedSubject || !scope || !contextScopePermitted) return

    setSubmitting(true)
    setRecordError(null)
    setRecordMessage(null)
    try {
      const evidenceReferences =
        evidenceKind.trim() && evidenceReference.trim()
          ? [
              {
                kind: evidenceKind.trim(),
                reference: evidenceReference.trim(),
              },
            ]
          : []

      const result = await recordConnectivityDecision({
        authorityScope: scope,
        sourceComponentDeploymentId:
          selectedSubject.sourceComponentDeploymentId,
        destinationComponentDeploymentId:
          selectedSubject.destinationComponentDeploymentId,
        dcsContractRevisionId: selectedSubject.dcsContractRevisionId,
        outcome,
        validFrom: toOffsetAwareIso(validFrom),
        validUntil: validUntil ? toOffsetAwareIso(validUntil) : null,
        reasonCode: reasonCode.trim(),
        reasonText: reasonText.trim(),
        evidenceReferences,
        supersedesDecisionId: context?.supersedesDecisionId ?? null,
      })
      setRecordMessage(
        result.outcome === "Recorded"
          ? `Final ${result.decision.outcome} Decision recorded.`
          : "An identical current Decision already existed and was resolved.",
      )
      setReasonCode("")
      setReasonText("")
      setEvidenceKind("")
      setEvidenceReference("")
      setReloadToken((value) => value + 1)
    } catch (caught) {
      setRecordError(
        caught instanceof ApiError
          ? caught
          : new ApiError(
              500,
              "InternalError",
              "The final Decision could not be recorded.",
            ),
      )
    } finally {
      setSubmitting(false)
    }
  }

  const formDisabled =
    !scope ||
    !selectedSubject ||
    !reasonCode.trim() ||
    !reasonText.trim() ||
    !validFrom ||
    !contextScopePermitted ||
    (!!evidenceKind.trim() !== !!evidenceReference.trim())

  return (
    <div className="mx-auto max-w-[1440px]">
      <header className="mb-6">
        <div className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#64748B]">
          Policy
        </div>
        <h1 className="text-[28px] font-bold tracking-tight text-[#172033]">
          Decisions
        </h1>
        <p className="mt-2 max-w-3xl text-sm text-[#64748B]">
          Inspect authorized final Connectivity Decisions and record a direct
          final Allowed or NotAllowed outcome where DecideConnectivity is
          admitted. There is no pending approval state.
        </p>
      </header>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.7fr)_minmax(360px,0.8fr)]">
        <section className="overflow-hidden rounded-lg border border-[#E2E8F0] bg-white">
          <div className="border-b border-[#E2E8F0] px-5 py-4">
            <h2 className="text-base font-semibold text-[#172033]">
              Authorized final Decisions
            </h2>
            <p className="mt-1 text-xs text-[#64748B]">Page {page}</p>
          </div>

          {ambiguousReadScopes.length > 0 ? (
            <div className="m-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
              {ambiguousReadScopes.length} read scope(s) remain fail-closed
              because ReadConnectivityDecision authority is ambiguous.
            </div>
          ) : null}

          {listError ? (
            <ErrorBox error={listError} />
          ) : loadingList ? (
            <div className="p-8 text-sm text-[#64748B]">
              Loading Decisions…
            </div>
          ) : decisions.length === 0 ? (
            <div className="p-10 text-center">
              <Scale className="mx-auto size-7 text-[#94A3B8]" aria-hidden="true" />
              <div className="mt-3 text-sm font-semibold text-[#334155]">
                No visible final Decisions
              </div>
              <div className="mt-2 text-sm text-[#64748B]">
                No durable Connectivity Decision is currently visible through
                your read authority.
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[980px] text-left text-sm">
                <thead className="bg-[#F8FAFC] text-xs uppercase tracking-wide text-[#64748B]">
                  <tr>
                    <th className="px-4 py-3 font-semibold">Decision</th>
                    <th className="px-4 py-3 font-semibold">Interaction</th>
                    <th className="px-4 py-3 font-semibold">Scope</th>
                    <th className="px-4 py-3 font-semibold">Outcome</th>
                    <th className="px-4 py-3 font-semibold">Valid from</th>
                    <th className="w-12 px-4 py-3" aria-label="Open" />
                  </tr>
                </thead>
                <tbody>
                  {decisions.map((decision) => (
                    <tr
                      key={decision.decisionId}
                      className="border-t border-[#E2E8F0] align-top hover:bg-[#F8FAFC]"
                    >
                      <td className="px-4 py-3 font-mono text-xs text-[#334155]">
                        {shortId(decision.decisionId)}
                      </td>
                      <td className="px-4 py-3">
                        <div className="font-medium text-[#172033]">
                          {displayName(
                            decision.catalogue?.sourceDisplayName,
                            decision.subject.sourceComponentDeploymentId,
                          )}{" "}
                          →{" "}
                          {displayName(
                            decision.catalogue?.destinationDisplayName,
                            decision.subject.destinationComponentDeploymentId,
                          )}
                        </div>
                        <div className="mt-1 text-xs text-[#64748B]">
                          {displayName(
                            decision.catalogue?.dcsDisplayName,
                            decision.subject.dcsContractRevisionId,
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3">{decision.governanceScope}</td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${outcomeClasses(decision.outcome)}`}
                        >
                          {decision.outcome}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-xs text-[#475569]">
                        {new Date(decision.validity.validFrom).toLocaleString()}
                      </td>
                      <td className="px-4 py-3">
                        <button
                          type="button"
                          aria-label={`Open Decision ${decision.decisionId}`}
                          className="grid size-8 place-items-center rounded-md text-[#64748B] hover:bg-[#E2E8F0]"
                          onClick={() => onOpenDecision(decision.decisionId)}
                        >
                          <ChevronRight className="size-4" aria-hidden="true" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="flex justify-end gap-2 border-t border-[#E2E8F0] px-5 py-4">
            <Button
              variant="secondary"
              disabled={page === 1 || loadingList}
              onClick={() => onPageChange(Math.max(1, page - 1))}
            >
              Previous
            </Button>
            <Button
              variant="secondary"
              disabled={!hasMore || loadingList}
              onClick={() => onPageChange(page + 1)}
            >
              Next
            </Button>
          </div>
        </section>

        <form
          onSubmit={submit}
          className="self-start rounded-lg border border-[#E2E8F0] bg-white p-5"
        >
          <h2 className="text-base font-semibold text-[#172033]">
            {context?.supersedesDecisionId
              ? "Record replacement Decision"
              : "Record final Decision"}
          </h2>
          <p className="mt-1 text-xs text-[#64748B]">
            Actor, decision time and authority provenance are supplied by the
            authenticated server runtime.
          </p>

          <div className="mt-5 grid gap-4">
            {scopeError ? <ErrorBox error={scopeError} compact /> : null}

            <Field label="Decision Governance Scope">
              <Select
                value={scope}
                onChange={(event) => {
                  setScope(event.target.value)
                  setInteractionPage(1)
                  setSelectedKey("")
                }}
                disabled={loadingScopes || !!context}
                required
              >
                <option value="">
                  {loadingScopes ? "Loading scopes…" : "Select scope"}
                </option>
                {scopes.map((value) => (
                  <option key={value} value={value}>
                    {value}
                  </option>
                ))}
                {context?.scope && !scopes.includes(context.scope) ? (
                  <option value={context.scope}>{context.scope}</option>
                ) : null}
              </Select>
            </Field>

            {context && !contextScopePermitted && !loadingScopes ? (
              <div className="rounded-md border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900">
                This exact scope is not currently available through an
                unambiguous DecideConnectivity authority. Recording remains
                disabled.
              </div>
            ) : null}

            {contextualSubject ? (
              <div className="rounded-md border border-[#E2E8F0] bg-[#F8FAFC] p-3">
                <div className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">
                  Exact connectivity subject
                </div>
                <dl className="mt-3 grid gap-2 text-xs">
                  <div>
                    <dt className="text-[#64748B]">Source</dt>
                    <dd className="break-all font-mono text-[#334155]">
                      {contextualSubject.sourceComponentDeploymentId}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-[#64748B]">Destination</dt>
                    <dd className="break-all font-mono text-[#334155]">
                      {contextualSubject.destinationComponentDeploymentId}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-[#64748B]">DCS revision</dt>
                    <dd className="break-all font-mono text-[#334155]">
                      {contextualSubject.dcsContractRevisionId}
                    </dd>
                  </div>
                </dl>
                {context?.supersedesDecisionId ? (
                  <div className="mt-3 text-xs text-[#64748B]">
                    Supersedes{" "}
                    <span className="font-mono">
                      {shortId(context.supersedesDecisionId)}
                    </span>
                  </div>
                ) : null}
              </div>
            ) : (
              <>
                <Field label="Search decision subjects">
                  <div className="flex gap-2">
                    <div className="relative min-w-0 flex-1">
                      <Search
                        className="pointer-events-none absolute left-3 top-3 size-4 text-[#94A3B8]"
                        aria-hidden="true"
                      />
                      <input
                        type="search"
                        value={searchInput}
                        maxLength={256}
                        disabled={!scope}
                        onChange={(event) => setSearchInput(event.target.value)}
                        className="min-h-10 w-full rounded-md border border-[#CBD5E1] py-2 pl-9 pr-3 text-sm disabled:bg-[#F8FAFC]"
                        placeholder="Application, component, DCS…"
                      />
                    </div>
                    <Button
                      type="button"
                      variant="secondary"
                      disabled={!scope}
                      onClick={() => {
                        setSearch(searchInput.trim())
                        setInteractionPage(1)
                      }}
                    >
                      Search
                    </Button>
                  </div>
                </Field>

                {interactionError ? (
                  <ErrorBox error={interactionError} compact />
                ) : null}

                <Field label="Exact directed interaction">
                  <Select
                    value={selectedKey}
                    onChange={(event) => setSelectedKey(event.target.value)}
                    disabled={!scope || loadingInteractions}
                    required
                  >
                    <option value="">
                      {loadingInteractions
                        ? "Loading interactions…"
                        : "Select interaction"}
                    </option>
                    {interactions.map((item) => (
                      <option
                        key={interactionKey(item)}
                        value={interactionKey(item)}
                      >
                        {interactionLabel(item)}
                      </option>
                    ))}
                  </Select>
                </Field>

                <div className="flex items-center justify-between text-xs text-[#64748B]">
                  <span>Interaction page {interactionPage}</span>
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      variant="secondary"
                      disabled={interactionPage === 1 || loadingInteractions}
                      onClick={() =>
                        setInteractionPage((value) => Math.max(1, value - 1))
                      }
                    >
                      Previous
                    </Button>
                    <Button
                      type="button"
                      variant="secondary"
                      disabled={!hasMoreInteractions || loadingInteractions}
                      onClick={() =>
                        setInteractionPage((value) => value + 1)
                      }
                    >
                      Next
                    </Button>
                  </div>
                </div>
              </>
            )}

            <Field label="Final outcome">
              <Select
                value={outcome}
                onChange={(event) =>
                  setOutcome(event.target.value as ConnectivityDecisionOutcome)
                }
              >
                <option value="Allowed">Allowed</option>
                <option value="NotAllowed">NotAllowed</option>
              </Select>
            </Field>

            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1 2xl:grid-cols-2">
              <Field label="Valid from">
                <input
                  type="datetime-local"
                  step="1"
                  value={validFrom}
                  onChange={(event) => setValidFrom(event.target.value)}
                  required
                  className="min-h-10 rounded-md border border-[#CBD5E1] px-3 py-2 text-sm"
                />
              </Field>
              <Field label="Valid until" hint="Optional; end is exclusive.">
                <input
                  type="datetime-local"
                  step="1"
                  value={validUntil}
                  onChange={(event) => setValidUntil(event.target.value)}
                  className="min-h-10 rounded-md border border-[#CBD5E1] px-3 py-2 text-sm"
                />
              </Field>
            </div>

            <Field label="Reason code">
              <input
                value={reasonCode}
                maxLength={256}
                onChange={(event) => setReasonCode(event.target.value)}
                required
                className="min-h-10 rounded-md border border-[#CBD5E1] px-3 py-2 text-sm"
                placeholder="security-reviewed"
              />
            </Field>

            <Field label="Reason">
              <textarea
                value={reasonText}
                maxLength={4096}
                rows={4}
                onChange={(event) => setReasonText(event.target.value)}
                required
                className="w-full rounded-md border border-[#CBD5E1] px-3 py-2 text-sm"
              />
            </Field>

            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1 2xl:grid-cols-2">
              <Field label="Evidence kind" hint="Optional; supply both fields.">
                <input
                  value={evidenceKind}
                  maxLength={256}
                  onChange={(event) => setEvidenceKind(event.target.value)}
                  className="min-h-10 rounded-md border border-[#CBD5E1] px-3 py-2 text-sm"
                  placeholder="Requirement"
                />
              </Field>
              <Field label="Evidence reference">
                <input
                  value={evidenceReference}
                  maxLength={2048}
                  onChange={(event) => setEvidenceReference(event.target.value)}
                  className="min-h-10 rounded-md border border-[#CBD5E1] px-3 py-2 text-sm"
                />
              </Field>
            </div>

            {ambiguousDecideScopes.length > 0 ? (
              <div className="rounded-md border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900">
                {ambiguousDecideScopes.length} DecideConnectivity scope(s)
                remain fail-closed.
              </div>
            ) : null}

            {recordError ? <ErrorBox error={recordError} compact /> : null}
            {recordMessage ? (
              <div
                role="status"
                className="rounded-md border border-green-200 bg-green-50 p-3 text-sm text-green-800"
              >
                {recordMessage}
              </div>
            ) : null}

            <Button
              type="submit"
              loading={submitting}
              disabled={formDisabled}
            >
              Record final Decision
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

function ErrorBox({
  error,
  compact = false,
}: {
  error: ApiError
  compact?: boolean
}) {
  return (
    <div
      role="alert"
      className={`${compact ? "m-0" : "m-4"} rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800`}
    >
      <div className="flex gap-2">
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
  )
}
