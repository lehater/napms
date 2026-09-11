import { useEffect, useMemo, useState } from "react"
import { ChevronRight, Plus, Search, Trash2 } from "lucide-react"

import { ApiError } from "@/lib/api"
import { listConnectivityDecisionInteractions, listConnectivityDecisions, listConnectivityDecisionScopes, recordConnectivityDecision, type ConnectivityDecisionDto, type ConnectivityDecisionOutcome, type DecisionEvidenceReferenceDto } from "@/features/decisions/api"
import type { ProposalInteraction } from "@/features/catalogues/model/interaction"
import {
  CatalogueIdentity,
  displayName,
  shortId,
  trafficAlternativeText,
} from "@/features/catalogues/components/CatalogueIdentity"
import { Button } from "@/components/ui/Button"
import { Field, Select } from "@/components/ui/Field"
import {
  nowLocalDateTimeInput,
  toOffsetAwareIso,
} from "@/lib/datetime"

type EvidenceDraft = {
  kind: string
  reference: string
}

type DecisionListState = {
  page: number
  refreshGeneration: number
  loading: boolean
  decisions: ConnectivityDecisionDto[]
  hasMore: boolean
  ambiguousReadScopes: string[]
  error: ApiError | null
}

function outcomeClasses(outcome: ConnectivityDecisionOutcome) {
  return outcome === "Allowed"
    ? "border-green-200 bg-green-50 text-green-800"
    : "border-red-200 bg-red-50 text-red-800"
}

function validityText(decision: ConnectivityDecisionDto) {
  return decision.validity.validUntil
    ? `${decision.validity.validFrom} → ${decision.validity.validUntil}`
    : `${decision.validity.validFrom} → open-ended`
}

function optionLabel(name: string | null | undefined, id: string) {
  const readable = name?.trim()
  return readable ? `${readable} · ${shortId(id)}` : shortId(id)
}

function dcsLabel(item: ProposalInteraction) {
  const base = optionLabel(
    item.catalogue?.dcsDisplayName,
    item.dcsContractRevisionId,
  )
  const alternatives = item.catalogue?.trafficAlternatives ?? []
  return alternatives.length > 0
    ? `${base} — ${alternatives.map(trafficAlternativeText).join(" | ")}`
    : base
}

function normalizeEvidence(
  evidence: EvidenceDraft[],
): DecisionEvidenceReferenceDto[] | null {
  const populated = evidence.filter(
    (item) => item.kind.trim() || item.reference.trim(),
  )
  if (
    populated.some(
      (item) => !item.kind.trim() || !item.reference.trim(),
    )
  ) {
    return null
  }
  return populated.map((item) => ({
    kind: item.kind.trim(),
    reference: item.reference.trim(),
  }))
}

export function ConnectivityDecisionsPage({
  page,
  onPageChange,
  onOpenDecision,
}: {
  page: number
  onPageChange: (page: number) => void
  onOpenDecision: (decisionId: string) => void
}) {
  const [listRefreshGeneration, setListRefreshGeneration] = useState(0)
  const [listState, setListState] = useState<DecisionListState>(() => ({
    page,
    refreshGeneration: 0,
    loading: true,
    decisions: [],
    hasMore: false,
    ambiguousReadScopes: [],
    error: null,
  }))

  const [scopes, setScopes] = useState<string[]>([])
  const [ambiguousDecideScopes, setAmbiguousDecideScopes] = useState<string[]>([])
  const [scope, setScope] = useState("")
  const [loadingScopes, setLoadingScopes] = useState(true)

  const [interactions, setInteractions] = useState<ProposalInteraction[]>([])
  const [interactionPage, setInteractionPage] = useState(1)
  const [hasMoreInteractions, setHasMoreInteractions] = useState(false)
  const [loadingInteractions, setLoadingInteractions] = useState(false)
  const [searchInput, setSearchInput] = useState("")
  const [search, setSearch] = useState("")
  const [source, setSource] = useState("")
  const [destination, setDestination] = useState("")
  const [dcs, setDcs] = useState("")

  const [outcome, setOutcome] =
    useState<ConnectivityDecisionOutcome>("Allowed")
  const [validFrom, setValidFrom] = useState(nowLocalDateTimeInput())
  const [validUntil, setValidUntil] = useState("")
  const [reasonCode, setReasonCode] = useState("")
  const [reasonText, setReasonText] = useState("")
  const [evidence, setEvidence] = useState<EvidenceDraft[]>([
    { kind: "", reference: "" },
  ])
  const [recording, setRecording] = useState(false)
  const [recordError, setRecordError] = useState<ApiError | null>(null)
  const [recordMessage, setRecordMessage] = useState<string | null>(null)

  useEffect(() => {
    const requestPage = page
    const requestRefreshGeneration = listRefreshGeneration
    let active = true

    setListState({
      page: requestPage,
      refreshGeneration: requestRefreshGeneration,
      loading: true,
      decisions: [],
      hasMore: false,
      ambiguousReadScopes: [],
      error: null,
    })

    void listConnectivityDecisions(requestPage)
      .then((result) => {
        if (!active) return
        setListState({
          page: requestPage,
          refreshGeneration: requestRefreshGeneration,
          loading: false,
          decisions: result.items,
          hasMore: result.hasMore,
          ambiguousReadScopes: result.ambiguousScopes.map(
            (item) => item.scope,
          ),
          error: null,
        })
      })
      .catch((caught) => {
        if (!active) return
        setListState({
          page: requestPage,
          refreshGeneration: requestRefreshGeneration,
          loading: false,
          decisions: [],
          hasMore: false,
          ambiguousReadScopes: [],
          error:
            caught instanceof ApiError
              ? caught
              : new ApiError(
                  500,
                  "InternalError",
                  "Connectivity Decisions could not be loaded.",
                ),
        })
      })

    return () => {
      active = false
    }
  }, [page, listRefreshGeneration])

  const listStateIsCurrent =
    listState.page === page &&
    listState.refreshGeneration === listRefreshGeneration
  const visibleDecisions = listStateIsCurrent ? listState.decisions : []
  const visibleHasMore = listStateIsCurrent ? listState.hasMore : false
  const visibleAmbiguousReadScopes = listStateIsCurrent
    ? listState.ambiguousReadScopes
    : []
  const visibleListError = listStateIsCurrent ? listState.error : null
  const visibleLoadingList = !listStateIsCurrent || listState.loading

  useEffect(() => {
    let active = true
    setLoadingScopes(true)
    setRecordError(null)
    void listConnectivityDecisionScopes()
      .then((result) => {
        if (!active) return
        const values = result.scopes.map((item) => item.scope)
        setScopes(values)
        setAmbiguousDecideScopes(
          result.ambiguousScopes.map((item) => item.scope),
        )
        if (values.length === 1) {
          setScope(values[0])
        }
      })
      .catch((caught) => {
        if (!active) return
        setRecordError(
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
  }, [])

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setInteractionPage(1)
      setSearch(searchInput.trim())
    }, 300)
    return () => window.clearTimeout(timer)
  }, [searchInput])

  useEffect(() => {
    setInteractions([])
    setHasMoreInteractions(false)
    setSource("")
    setDestination("")
    setDcs("")
    if (!scope) return

    let active = true
    setLoadingInteractions(true)
    setRecordError(null)
    void listConnectivityDecisionInteractions(scope, interactionPage, search)
      .then((result) => {
        if (!active) return
        setInteractions(result.items)
        setHasMoreInteractions(result.hasMore)
      })
      .catch((caught) => {
        if (!active) return
        setRecordError(
          caught instanceof ApiError
            ? caught
            : new ApiError(
                500,
                "InternalError",
                "Decision interactions could not be loaded.",
              ),
        )
      })
      .finally(() => {
        if (active) setLoadingInteractions(false)
      })

    return () => {
      active = false
    }
  }, [scope, interactionPage, search])

  const sourceOptions = useMemo(() => {
    const values = new Map<string, string | null | undefined>()
    for (const item of interactions) {
      if (!values.has(item.sourceComponentDeploymentId)) {
        values.set(
          item.sourceComponentDeploymentId,
          item.catalogue?.sourceDisplayName,
        )
      }
    }
    return [...values.entries()]
  }, [interactions])

  const destinationOptions = useMemo(() => {
    const values = new Map<string, string | null | undefined>()
    for (const item of interactions) {
      if (item.sourceComponentDeploymentId !== source) continue
      if (!values.has(item.destinationComponentDeploymentId)) {
        values.set(
          item.destinationComponentDeploymentId,
          item.catalogue?.destinationDisplayName,
        )
      }
    }
    return [...values.entries()]
  }, [interactions, source])

  const dcsOptions = useMemo(
    () =>
      interactions.filter(
        (item) =>
          item.sourceComponentDeploymentId === source &&
          item.destinationComponentDeploymentId === destination,
      ),
    [interactions, source, destination],
  )

  function updateEvidence(
    index: number,
    field: keyof EvidenceDraft,
    value: string,
  ) {
    setEvidence((current) =>
      current.map((item, itemIndex) =>
        itemIndex === index ? { ...item, [field]: value } : item,
      ),
    )
  }

  function resetRecordForm() {
    setSource("")
    setDestination("")
    setDcs("")
    setOutcome("Allowed")
    setValidFrom(nowLocalDateTimeInput())
    setValidUntil("")
    setReasonCode("")
    setReasonText("")
    setEvidence([{ kind: "", reference: "" }])
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    if (!scope || !source || !destination || !dcs) return

    if (!reasonCode.trim() || !reasonText.trim()) {
      setRecordError(
        new ApiError(
          422,
          "ValidationError",
          "Reason code and reason must both be non-empty.",
        ),
      )
      return
    }

    const evidenceReferences = normalizeEvidence(evidence)
    if (evidenceReferences === null) {
      setRecordError(
        new ApiError(
          422,
          "ValidationError",
          "Each evidence reference requires both kind and reference.",
        ),
      )
      return
    }

    let start: string
    let end: string | null
    try {
      start = toOffsetAwareIso(validFrom)
      end = validUntil ? toOffsetAwareIso(validUntil) : null
      if (end && new Date(start).getTime() >= new Date(end).getTime()) {
        throw new Error("invalid validity")
      }
    } catch {
      setRecordError(
        new ApiError(
          422,
          "InvalidDecisionValidity",
          "Validity requires a valid start and an optional end after the start.",
        ),
      )
      return
    }

    setRecording(true)
    setRecordError(null)
    setRecordMessage(null)
    try {
      const result = await recordConnectivityDecision({
        authorityScope: scope,
        sourceComponentDeploymentId: source,
        destinationComponentDeploymentId: destination,
        dcsContractRevisionId: dcs,
        outcome,
        validFrom: start,
        validUntil: end,
        reasonCode: reasonCode.trim(),
        reasonText: reasonText.trim(),
        evidenceReferences,
      })
      setRecordMessage(
        result.outcome === "Recorded"
          ? `Decision ${shortId(result.decision.decisionId)} recorded.`
          : `Equivalent current Decision ${shortId(result.decision.decisionId)} resolved.`,
      )
      resetRecordForm()
      setListRefreshGeneration((current) => current + 1)
    } catch (caught) {
      setRecordError(
        caught instanceof ApiError
          ? caught
          : new ApiError(
              500,
              "InternalError",
              "Connectivity Decision could not be recorded.",
            ),
      )
    } finally {
      setRecording(false)
    }
  }

  return (
    <div className="mx-auto max-w-[1440px]">
      <header className="mb-6">
        <div className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#64748B]">
          Connectivity Decisions
        </div>
        <h1 className="text-[28px] font-bold tracking-tight text-[#172033]">
          Decisions
        </h1>
        <p className="mt-2 max-w-4xl text-sm text-[#64748B]">
          Inspect final Connectivity Decisions visible through independent read
          authority, or record a final Allowed / NotAllowed result for an exact
          ACC-backed subject admitted by DecideConnectivity.
        </p>
      </header>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_460px]">
        <section className="overflow-hidden rounded-lg border border-[#E2E8F0] bg-white">
          <div className="flex items-center justify-between gap-4 border-b border-[#E2E8F0] px-5 py-4">
            <div>
              <h2 className="text-base font-semibold text-[#172033]">
                Visible final Decisions
              </h2>
              <p className="mt-1 text-xs text-[#64748B]">Page {page}</p>
            </div>
          </div>

          {visibleAmbiguousReadScopes.length > 0 ? (
            <div className="m-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
              {visibleAmbiguousReadScopes.length} read scope(s) are ambiguous and remain
              fail-closed. Decisions from those scopes are not exposed.
            </div>
          ) : null}

          {visibleListError ? (
            <div className="m-4 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800">
              <div className="font-semibold">{visibleListError.code}</div>
              <div className="mt-1">{visibleListError.message}</div>
            </div>
          ) : null}

          {visibleLoadingList ? (
            <div className="p-8 text-sm text-[#64748B]">
              Loading Decisions…
            </div>
          ) : visibleDecisions.length === 0 ? (
            <div className="p-10 text-center">
              <div className="text-sm font-semibold text-[#334155]">
                No visible Connectivity Decisions
              </div>
              <div className="mt-2 text-sm text-[#64748B]">
                No Decisions are visible through the current read-authority result.
                This may mean there are no admitted read scopes, or that admitted
                scopes contain no Decisions. Decide authority is evaluated
                separately in the record form.
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[1050px] text-left text-sm">
                <thead className="bg-[#F8FAFC] text-xs uppercase tracking-wide text-[#64748B]">
                  <tr>
                    <th className="px-4 py-3 font-semibold">Subject</th>
                    <th className="px-4 py-3 font-semibold">Scope</th>
                    <th className="px-4 py-3 font-semibold">Outcome</th>
                    <th className="px-4 py-3 font-semibold">Validity</th>
                    <th className="px-4 py-3 font-semibold">Supersession</th>
                    <th className="w-12 px-4 py-3" aria-label="Open" />
                  </tr>
                </thead>
                <tbody>
                  {visibleDecisions.map((decision) => (
                    <tr
                      key={decision.decisionId}
                      className="border-t border-[#E2E8F0] align-top hover:bg-[#F8FAFC]"
                    >
                      <td className="px-4 py-3">
                        <div className="grid gap-2">
                          <CatalogueIdentity
                            name={decision.catalogue?.sourceDisplayName}
                            id={decision.subject.sourceComponentDeploymentId}
                          />
                          <div className="text-xs font-semibold text-[#64748B]">
                            to
                          </div>
                          <CatalogueIdentity
                            name={decision.catalogue?.destinationDisplayName}
                            id={decision.subject.destinationComponentDeploymentId}
                          />
                          <div className="text-xs text-[#475569]">
                            Access:{" "}
                            {displayName(
                              decision.catalogue?.dcsDisplayName,
                              decision.subject.dcsContractRevisionId,
                            )}
                          </div>
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
                        {validityText(decision)}
                      </td>
                      <td className="px-4 py-3 text-xs text-[#475569]">
                        {decision.supersedesDecisionId
                          ? `Supersedes ${shortId(decision.supersedesDecisionId)}`
                          : "Original"}
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
              disabled={page === 1 || visibleLoadingList}
              onClick={() => onPageChange(Math.max(1, page - 1))}
            >
              Previous
            </Button>
            <Button
              variant="secondary"
              disabled={!visibleHasMore || visibleLoadingList}
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
          <div className="mb-5 flex items-center gap-2">
            <Plus className="size-4 text-[#2563EB]" aria-hidden="true" />
            <h2 className="text-base font-semibold text-[#172033]">
              Record final Decision
            </h2>
          </div>

          {ambiguousDecideScopes.length > 0 ? (
            <div className="mb-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
              {ambiguousDecideScopes.length} DecideConnectivity scope(s) are
              ambiguous and cannot be selected.
            </div>
          ) : null}

          {!loadingScopes && scopes.length === 0 ? (
            <div className="mb-4 rounded-md border border-[#E2E8F0] bg-[#F8FAFC] p-3 text-sm text-[#475569]">
              No unambiguous DecideConnectivity scope is currently admitted.
              Read access to Decisions is independent.
            </div>
          ) : null}

          {recordError ? (
            <div className="mb-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800">
              <div className="font-semibold">{recordError.code}</div>
              <div className="mt-1">{recordError.message}</div>
            </div>
          ) : null}

          {recordMessage ? (
            <div className="mb-4 rounded-md border border-green-200 bg-green-50 p-3 text-sm text-green-800">
              {recordMessage}
            </div>
          ) : null}

          <div className="grid gap-4">
            <Field label="Decision Governance Scope">
              <Select
                value={scope}
                onChange={(event) => {
                  setScope(event.target.value)
                  setInteractionPage(1)
                }}
                disabled={loadingScopes || scopes.length === 0}
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
              </Select>
            </Field>

            <Field label="Search exact ACC interaction">
              <div className="relative">
                <Search
                  className="pointer-events-none absolute left-3 top-3 size-4 text-[#94A3B8]"
                  aria-hidden="true"
                />
                <input
                  type="search"
                  value={searchInput}
                  maxLength={256}
                  onChange={(event) => setSearchInput(event.target.value)}
                  disabled={!scope}
                  className="min-h-10 w-full rounded-md border border-[#CBD5E1] pl-9 pr-3 text-sm disabled:bg-[#F8FAFC]"
                  placeholder="Search interactions"
                />
              </div>
            </Field>

            <div className="flex items-center justify-between text-xs text-[#64748B]">
              <span>
                Interaction page {interactionPage}
                {loadingInteractions ? " · loading" : ""}
              </span>
              <div className="flex gap-2">
                <button
                  type="button"
                  className="font-semibold text-[#2563EB] disabled:text-[#94A3B8]"
                  disabled={interactionPage === 1 || loadingInteractions}
                  onClick={() =>
                    setInteractionPage((value) => Math.max(1, value - 1))
                  }
                >
                  Previous
                </button>
                <button
                  type="button"
                  className="font-semibold text-[#2563EB] disabled:text-[#94A3B8]"
                  disabled={!hasMoreInteractions || loadingInteractions}
                  onClick={() => setInteractionPage((value) => value + 1)}
                >
                  Next
                </button>
              </div>
            </div>

            <Field label="Source Component Deployment">
              <Select
                value={source}
                onChange={(event) => {
                  setSource(event.target.value)
                  setDestination("")
                  setDcs("")
                }}
                disabled={!scope || loadingInteractions}
                required
              >
                <option value="">Select source</option>
                {sourceOptions.map(([id, name]) => (
                  <option key={id} value={id}>
                    {optionLabel(name, id)}
                  </option>
                ))}
              </Select>
            </Field>

            <Field label="Destination Component Deployment">
              <Select
                value={destination}
                onChange={(event) => {
                  setDestination(event.target.value)
                  setDcs("")
                }}
                disabled={!source || loadingInteractions}
                required
              >
                <option value="">Select destination</option>
                {destinationOptions.map(([id, name]) => (
                  <option key={id} value={id}>
                    {optionLabel(name, id)}
                  </option>
                ))}
              </Select>
            </Field>

            <Field label="DCS / Access">
              <Select
                value={dcs}
                onChange={(event) => setDcs(event.target.value)}
                disabled={!destination || loadingInteractions}
                required
              >
                <option value="">Select access</option>
                {dcsOptions.map((item) => (
                  <option
                    key={item.dcsContractRevisionId}
                    value={item.dcsContractRevisionId}
                  >
                    {dcsLabel(item)}
                  </option>
                ))}
              </Select>
            </Field>

            <Field label="Final outcome">
              <Select
                value={outcome}
                onChange={(event) =>
                  setOutcome(event.target.value as ConnectivityDecisionOutcome)
                }
                required
              >
                <option value="Allowed">Allowed</option>
                <option value="NotAllowed">NotAllowed</option>
              </Select>
            </Field>

            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Valid from">
                <input
                  type="datetime-local"
                  step="1"
                  value={validFrom}
                  onChange={(event) => setValidFrom(event.target.value)}
                  className="min-h-10 w-full rounded-md border border-[#CBD5E1] px-3 py-2 text-sm"
                  required
                />
              </Field>
              <Field label="Valid until" hint="Optional; leave empty for open-ended validity.">
                <input
                  type="datetime-local"
                  step="1"
                  value={validUntil}
                  onChange={(event) => setValidUntil(event.target.value)}
                  className="min-h-10 w-full rounded-md border border-[#CBD5E1] px-3 py-2 text-sm"
                />
              </Field>
            </div>

            <Field label="Reason code">
              <input
                value={reasonCode}
                maxLength={256}
                onChange={(event) => setReasonCode(event.target.value)}
                className="min-h-10 w-full rounded-md border border-[#CBD5E1] px-3 py-2 text-sm"
                required
              />
            </Field>

            <Field label="Reason">
              <textarea
                value={reasonText}
                maxLength={4096}
                onChange={(event) => setReasonText(event.target.value)}
                className="min-h-24 w-full rounded-md border border-[#CBD5E1] px-3 py-2 text-sm"
                required
              />
            </Field>

            <div className="grid gap-3">
              <div>
                <div className="text-sm font-medium text-[#334155]">
                  Evidence references
                </div>
                <div className="mt-1 text-xs text-[#64748B]">
                  Optional references only. Evidence content remains outside this
                  workspace.
                </div>
              </div>
              {evidence.map((item, index) => (
                <div
                  key={index}
                  className="grid gap-2 rounded-md border border-[#E2E8F0] p-3"
                >
                  <input
                    value={item.kind}
                    maxLength={256}
                    onChange={(event) =>
                      updateEvidence(index, "kind", event.target.value)
                    }
                    className="min-h-10 w-full rounded-md border border-[#CBD5E1] px-3 py-2 text-sm"
                    placeholder="Kind"
                    aria-label={`Evidence ${index + 1} kind`}
                  />
                  <input
                    value={item.reference}
                    maxLength={2048}
                    onChange={(event) =>
                      updateEvidence(index, "reference", event.target.value)
                    }
                    className="min-h-10 w-full rounded-md border border-[#CBD5E1] px-3 py-2 text-sm"
                    placeholder="Reference"
                    aria-label={`Evidence ${index + 1} reference`}
                  />
                  {evidence.length > 1 ? (
                    <button
                      type="button"
                      className="inline-flex items-center gap-1 justify-self-start text-xs font-semibold text-[#64748B] hover:text-[#172033]"
                      onClick={() =>
                        setEvidence((current) =>
                          current.filter((_, itemIndex) => itemIndex !== index),
                        )
                      }
                    >
                      <Trash2 className="size-3.5" aria-hidden="true" />
                      Remove
                    </button>
                  ) : null}
                </div>
              ))}
              <button
                type="button"
                className="justify-self-start text-xs font-semibold text-[#2563EB]"
                onClick={() =>
                  setEvidence((current) => [
                    ...current,
                    { kind: "", reference: "" },
                  ])
                }
              >
                Add evidence reference
              </button>
            </div>

            <Button
              type="submit"
              loading={recording}
              disabled={
                loadingScopes ||
                scopes.length === 0 ||
                !scope ||
                !source ||
                !destination ||
                !dcs
              }
            >
              Record Decision
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
