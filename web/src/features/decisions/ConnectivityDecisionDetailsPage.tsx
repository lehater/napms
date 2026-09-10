import { useEffect, useState } from "react"
import { ArrowLeft, RotateCcw, Trash2 } from "lucide-react"

import {
  ApiError,
  getConnectivityDecision,
  listConnectivityDecisionScopes,
  recordConnectivityDecision,
  type ConnectivityDecisionDetailResponse,
  type ConnectivityDecisionOutcome,
  type DecisionEvidenceReferenceDto,
} from "@/api"
import {
  CatalogueIdentity,
  displayName,
  shortId,
} from "@/components/catalogue/CatalogueIdentity"
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

function outcomeClasses(outcome: ConnectivityDecisionOutcome) {
  return outcome === "Allowed"
    ? "border-green-200 bg-green-50 text-green-800"
    : "border-red-200 bg-red-50 text-red-800"
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

export function ConnectivityDecisionDetailsPage({
  decisionId,
  onBack,
  onOpenDecision,
  onOpenRequirement,
}: {
  decisionId: string
  onBack: () => void
  onOpenDecision: (decisionId: string) => void
  onOpenRequirement: (requirementId: string) => void
}) {
  const [detail, setDetail] =
    useState<ConnectivityDecisionDetailResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)

  const [decideScopes, setDecideScopes] = useState<string[]>([])
  const [ambiguousDecideScopes, setAmbiguousDecideScopes] = useState<string[]>([])
  const [loadingScopes, setLoadingScopes] = useState(true)
  const [scopeError, setScopeError] = useState<ApiError | null>(null)

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

  useEffect(() => {
    let active = true
    setLoading(true)
    setError(null)
    void getConnectivityDecision(decisionId)
      .then((result) => {
        if (!active) return
        setDetail(result)
        setOutcome(result.decision.outcome)
      })
      .catch((caught) => {
        if (!active) return
        setError(
          caught instanceof ApiError
            ? caught
            : new ApiError(
                500,
                "InternalError",
                "Connectivity Decision detail could not be loaded.",
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

  useEffect(() => {
    let active = true
    setLoadingScopes(true)
    setScopeError(null)
    void listConnectivityDecisionScopes()
      .then((result) => {
        if (!active) return
        setDecideScopes(result.scopes.map((item) => item.scope))
        setAmbiguousDecideScopes(
          result.ambiguousScopes.map((item) => item.scope),
        )
      })
      .catch((caught) => {
        if (!active) return
        setScopeError(
          caught instanceof ApiError
            ? caught
            : new ApiError(
                500,
                "InternalError",
                "DecideConnectivity authority could not be discovered.",
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

  async function submitReplacement(event: React.FormEvent) {
    event.preventDefault()
    if (!detail) return

    const decision = detail.decision
    if (!decideScopes.includes(decision.governanceScope)) {
      setRecordError(
        new ApiError(
          403,
          "AuthorityDenied",
          "This Decision scope is not currently admitted for DecideConnectivity.",
        ),
      )
      return
    }
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
    try {
      const result = await recordConnectivityDecision({
        authorityScope: decision.governanceScope,
        sourceComponentDeploymentId:
          decision.subject.sourceComponentDeploymentId,
        destinationComponentDeploymentId:
          decision.subject.destinationComponentDeploymentId,
        dcsContractRevisionId: decision.subject.dcsContractRevisionId,
        outcome,
        validFrom: start,
        validUntil: end,
        reasonCode: reasonCode.trim(),
        reasonText: reasonText.trim(),
        evidenceReferences,
        supersedesDecisionId: decision.decisionId,
      })
      onOpenDecision(result.decision.decisionId)
    } catch (caught) {
      setRecordError(
        caught instanceof ApiError
          ? caught
          : new ApiError(
              500,
              "InternalError",
              "Replacement Decision could not be recorded.",
            ),
      )
    } finally {
      setRecording(false)
    }
  }

  const decision = detail?.decision ?? null
  const scopeAmbiguous =
    decision !== null &&
    ambiguousDecideScopes.includes(decision.governanceScope)
  const canReplace =
    decision !== null &&
    decideScopes.includes(decision.governanceScope) &&
    !scopeAmbiguous

  return (
    <div className="mx-auto max-w-[1180px]">
      <button
        type="button"
        className="mb-5 inline-flex items-center gap-2 text-sm font-semibold text-[#475569] hover:text-[#172033]"
        onClick={onBack}
      >
        <ArrowLeft className="size-4" aria-hidden="true" />
        Back to Decisions
      </button>

      {loading ? (
        <div className="rounded-lg border border-[#E2E8F0] bg-white p-8 text-sm text-[#64748B]">
          Loading Decision…
        </div>
      ) : error ? (
        <div className="rounded-lg border border-red-200 bg-red-50 p-5 text-sm text-red-800">
          <div className="font-semibold">{error.code}</div>
          <div className="mt-1">{error.message}</div>
        </div>
      ) : detail && decision ? (
        <div className="grid gap-6">
          <header>
            <div className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#64748B]">
              Connectivity Decision
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-[28px] font-bold tracking-tight text-[#172033]">
                Decision {shortId(decision.decisionId)}
              </h1>
              <span
                className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${outcomeClasses(decision.outcome)}`}
              >
                {decision.outcome}
              </span>
            </div>
            <p className="mt-2 text-sm text-[#64748B]">
              Immutable final business result. Replacement creates a new Decision;
              this record is never edited in place.
            </p>
          </header>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <h2 className="text-base font-semibold text-[#172033]">
              Exact subject
            </h2>
            <div className="mt-4 grid gap-5 md:grid-cols-3">
              <div>
                <div className="mb-2 text-xs uppercase tracking-wide text-[#64748B]">
                  Source
                </div>
                <CatalogueIdentity
                  name={decision.catalogue?.sourceDisplayName}
                  id={decision.subject.sourceComponentDeploymentId}
                />
              </div>
              <div>
                <div className="mb-2 text-xs uppercase tracking-wide text-[#64748B]">
                  Destination
                </div>
                <CatalogueIdentity
                  name={decision.catalogue?.destinationDisplayName}
                  id={decision.subject.destinationComponentDeploymentId}
                />
              </div>
              <div>
                <div className="mb-2 text-xs uppercase tracking-wide text-[#64748B]">
                  DCS / Access
                </div>
                <CatalogueIdentity
                  name={decision.catalogue?.dcsDisplayName}
                  id={decision.subject.dcsContractRevisionId}
                />
              </div>
            </div>
            <dl className="mt-6 grid gap-4 border-t border-[#E2E8F0] pt-5 text-sm md:grid-cols-2">
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Governance scope
                </dt>
                <dd className="mt-1">{decision.governanceScope}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Decision ID
                </dt>
                <dd className="mt-1 break-all font-mono text-xs">
                  {decision.decisionId}
                </dd>
              </div>
            </dl>
          </section>

          <section className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
              <h2 className="text-base font-semibold text-[#172033]">
                Reason and validity
              </h2>
              <dl className="mt-4 grid gap-4 text-sm">
                <div>
                  <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                    Outcome
                  </dt>
                  <dd className="mt-1 font-semibold">{decision.outcome}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                    Reason code
                  </dt>
                  <dd className="mt-1">{decision.reason.code}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                    Reason
                  </dt>
                  <dd className="mt-1 whitespace-pre-wrap">
                    {decision.reason.text}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                    Validity
                  </dt>
                  <dd className="mt-1">
                    {decision.validity.validFrom} →{" "}
                    {decision.validity.validUntil ?? "open-ended"}
                  </dd>
                </div>
              </dl>
            </div>

            <div className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
              <h2 className="text-base font-semibold text-[#172033]">
                Evidence references
              </h2>
              {decision.evidenceReferences.length === 0 ? (
                <p className="mt-3 text-sm text-[#64748B]">
                  No evidence references were recorded.
                </p>
              ) : (
                <dl className="mt-4 grid gap-4 text-sm">
                  {decision.evidenceReferences.map((item, index) => (
                    <div key={`${item.kind}-${item.reference}-${index}`}>
                      <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                        {item.kind}
                      </dt>
                      <dd className="mt-1 break-all">
                        {item.kind === "ConnectivityRequirement" ? (
                          <button
                            type="button"
                            className="font-mono text-xs font-semibold text-[#2563EB] hover:underline"
                            onClick={() => onOpenRequirement(item.reference)}
                          >
                            {item.reference}
                          </button>
                        ) : (
                          item.reference
                        )}
                      </dd>
                    </div>
                  ))}
                </dl>
              )}
            </div>
          </section>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <h2 className="text-base font-semibold text-[#172033]">
              Authority provenance
            </h2>
            <dl className="mt-4 grid gap-4 text-sm md:grid-cols-2">
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Deciding actor
                </dt>
                <dd className="mt-1">{decision.provenance.actorId}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Decided at
                </dt>
                <dd className="mt-1">{decision.provenance.decidedAt}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Decide authority reference
                </dt>
                <dd className="mt-1 break-all font-mono text-xs">
                  {decision.provenance.authorityReference}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#64748B]">
                  Read authority reference
                </dt>
                <dd className="mt-1 break-all font-mono text-xs">
                  {detail.readAuthorityReference}
                </dd>
              </div>
            </dl>
          </section>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <h2 className="text-base font-semibold text-[#172033]">
              Supersession
            </h2>
            {decision.supersedesDecisionId ? (
              <div className="mt-3 text-sm text-[#475569]">
                This Decision explicitly supersedes{" "}
                <button
                  type="button"
                  className="font-mono text-xs font-semibold text-[#2563EB]"
                  onClick={() =>
                    onOpenDecision(decision.supersedesDecisionId as string)
                  }
                >
                  {decision.supersedesDecisionId}
                </button>
                .
              </div>
            ) : (
              <p className="mt-3 text-sm text-[#64748B]">
                This Decision does not supersede an earlier Decision.
              </p>
            )}
          </section>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <div className="flex items-center gap-2">
              <RotateCcw className="size-4 text-[#2563EB]" aria-hidden="true" />
              <h2 className="text-base font-semibold text-[#172033]">
                Record replacement Decision
              </h2>
            </div>
            <p className="mt-2 text-sm text-[#64748B]">
              Creates a new immutable Decision for the same exact subject and
              scope with explicit supersedesDecisionId={shortId(decision.decisionId)}.
            </p>

            {scopeError ? (
              <div className="mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800">
                <div className="font-semibold">{scopeError.code}</div>
                <div className="mt-1">{scopeError.message}</div>
              </div>
            ) : null}

            {scopeAmbiguous ? (
              <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
                DecideConnectivity authority for this governance scope is ambiguous,
                so replacement remains fail-closed.
              </div>
            ) : null}

            {!loadingScopes && !canReplace && !scopeAmbiguous && !scopeError ? (
              <div className="mt-4 rounded-md border border-[#E2E8F0] bg-[#F8FAFC] p-3 text-sm text-[#475569]">
                This Decision is readable, but its governance scope is not
                independently admitted for DecideConnectivity.
              </div>
            ) : null}

            {recordError ? (
              <div className="mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800">
                <div className="font-semibold">{recordError.code}</div>
                <div className="mt-1">{recordError.message}</div>
              </div>
            ) : null}

            {canReplace ? (
              <form
                onSubmit={submitReplacement}
                className="mt-5 grid gap-4 lg:max-w-3xl"
              >
                <Field label="Final outcome">
                  <Select
                    value={outcome}
                    onChange={(event) =>
                      setOutcome(
                        event.target.value as ConnectivityDecisionOutcome,
                      )
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
                  <Field
                    label="Valid until"
                    hint="Optional; leave empty for open-ended validity."
                  >
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
                      Optional references; evidence content is not edited here.
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
                        aria-label={`Replacement evidence ${index + 1} kind`}
                      />
                      <input
                        value={item.reference}
                        maxLength={2048}
                        onChange={(event) =>
                          updateEvidence(index, "reference", event.target.value)
                        }
                        className="min-h-10 w-full rounded-md border border-[#CBD5E1] px-3 py-2 text-sm"
                        placeholder="Reference"
                        aria-label={`Replacement evidence ${index + 1} reference`}
                      />
                      {evidence.length > 1 ? (
                        <button
                          type="button"
                          className="inline-flex items-center gap-1 justify-self-start text-xs font-semibold text-[#64748B] hover:text-[#172033]"
                          onClick={() =>
                            setEvidence((current) =>
                              current.filter(
                                (_, itemIndex) => itemIndex !== index,
                              ),
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

                <Button type="submit" loading={recording}>
                  Record replacement
                </Button>
              </form>
            ) : null}
          </section>
        </div>
      ) : null}
    </div>
  )
}
