import { useEffect, useState } from "react"
import { ArrowLeft, RotateCcw } from "lucide-react"

import { Button } from "@/design-system/components/Button"
import { Field, Input, Select, Textarea } from "@/design-system/components/Field"
import { DetailSection } from "@/design-system/patterns/detail/Detail"
import { shortId } from "@/features/catalogues/components/CatalogueIdentity"
import {
  getConnectivityDecision,
  listConnectivityDecisionScopes,
  recordConnectivityDecision,
  type ConnectivityDecisionDetailResponse,
  type ConnectivityDecisionOutcome,
  type DecisionEvidenceReferenceDto,
} from "@/features/decisions/api"
import {
  DecisionEvidenceFields,
  type DecisionEvidenceDraft,
} from "@/features/decisions/components/DecisionEvidenceFields"
import {
  DecisionEvidenceSection,
  DecisionProvenanceSection,
  DecisionReasonSection,
  DecisionSubjectSection,
  DecisionSupersessionSection,
} from "@/features/decisions/components/DecisionDetailSections"
import { DecisionOutcomeStatus } from "@/features/decisions/components/DecisionStatus"
import { ApiError } from "@/lib/api"
import {
  nowLocalDateTimeInput,
  toOffsetAwareIso,
} from "@/lib/datetime"

function normalizeEvidence(
  evidence: DecisionEvidenceDraft[],
): DecisionEvidenceReferenceDto[] | null {
  const populated = evidence.filter(
    (item) => item.kind.trim() || item.reference.trim(),
  )
  if (populated.some((item) => !item.kind.trim() || !item.reference.trim())) {
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
  const [detail, setDetail] = useState<ConnectivityDecisionDetailResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)

  const [decideScopes, setDecideScopes] = useState<string[]>([])
  const [ambiguousDecideScopes, setAmbiguousDecideScopes] = useState<string[]>([])
  const [loadingScopes, setLoadingScopes] = useState(true)
  const [scopeError, setScopeError] = useState<ApiError | null>(null)

  const [outcome, setOutcome] = useState<ConnectivityDecisionOutcome>("Allowed")
  const [validFrom, setValidFrom] = useState(nowLocalDateTimeInput())
  const [validUntil, setValidUntil] = useState("")
  const [reasonCode, setReasonCode] = useState("")
  const [reasonText, setReasonText] = useState("")
  const [evidence, setEvidence] = useState<DecisionEvidenceDraft[]>([
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
        setAmbiguousDecideScopes(result.ambiguousScopes.map((item) => item.scope))
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
        sourceComponentDeploymentId: decision.subject.sourceComponentDeploymentId,
        destinationComponentDeploymentId: decision.subject.destinationComponentDeploymentId,
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
    decision !== null && ambiguousDecideScopes.includes(decision.governanceScope)
  const canReplace =
    decision !== null &&
    decideScopes.includes(decision.governanceScope) &&
    !scopeAmbiguous

  return (
    <div className="mx-auto max-w-[1180px]">
      <button
        type="button"
        className="mb-5 inline-flex items-center gap-2 text-sm font-semibold text-[var(--napms-color-text-body)] hover:text-[var(--napms-color-text-primary)]"
        onClick={onBack}
      >
        <ArrowLeft className="size-4" aria-hidden="true" />
        Back to Decisions
      </button>

      {loading ? (
        <div className="rounded-lg border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)] p-8 text-sm text-[var(--napms-color-text-secondary)]">
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
            <div className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-[var(--napms-color-text-secondary)]">
              Connectivity Decision
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-[28px] font-bold tracking-tight text-[var(--napms-color-text-primary)]">
                Decision {shortId(decision.decisionId)}
              </h1>
              <DecisionOutcomeStatus outcome={decision.outcome} />
            </div>
            <p className="mt-2 text-sm text-[var(--napms-color-text-secondary)]">
              Immutable final business result. Replacement creates a new Decision; this record is never edited in place.
            </p>
          </header>

          <DecisionSubjectSection detail={detail} />

          <section className="grid gap-6 lg:grid-cols-2">
            <DecisionReasonSection detail={detail} />
            <DecisionEvidenceSection
              detail={detail}
              onOpenRequirement={onOpenRequirement}
            />
          </section>

          <DecisionProvenanceSection detail={detail} />
          <DecisionSupersessionSection
            detail={detail}
            onOpenDecision={onOpenDecision}
          />

          <DetailSection title={
            <span className="inline-flex items-center gap-2">
              <RotateCcw className="size-4 text-[var(--napms-color-primary)]" aria-hidden="true" />
              Record replacement Decision
            </span>
          }>
            <p className="text-sm text-[var(--napms-color-text-secondary)]">
              Creates a new immutable Decision for the same exact subject and scope with explicit supersedesDecisionId={shortId(decision.decisionId)}.
            </p>

            {scopeError ? (
              <div className="mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800">
                <div className="font-semibold">{scopeError.code}</div>
                <div className="mt-1">{scopeError.message}</div>
              </div>
            ) : null}

            {scopeAmbiguous ? (
              <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
                DecideConnectivity authority for this governance scope is ambiguous, so replacement remains fail-closed.
              </div>
            ) : null}

            {!loadingScopes && !canReplace && !scopeAmbiguous && !scopeError ? (
              <div className="mt-4 rounded-md border border-[var(--napms-color-border)] bg-[var(--napms-color-surface-subtle)] p-3 text-sm text-[var(--napms-color-text-body)]">
                This Decision is readable, but its governance scope is not independently admitted for DecideConnectivity.
              </div>
            ) : null}

            {recordError ? (
              <div className="mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800">
                <div className="font-semibold">{recordError.code}</div>
                <div className="mt-1">{recordError.message}</div>
              </div>
            ) : null}

            {canReplace ? (
              <form onSubmit={submitReplacement} className="mt-5 grid gap-4 lg:max-w-3xl">
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
                    <Input
                      type="datetime-local"
                      step="1"
                      value={validFrom}
                      onChange={(event) => setValidFrom(event.target.value)}
                      required
                    />
                  </Field>
                  <Field
                    label="Valid until"
                    hint="Optional; leave empty for open-ended validity."
                  >
                    <Input
                      type="datetime-local"
                      step="1"
                      value={validUntil}
                      onChange={(event) => setValidUntil(event.target.value)}
                    />
                  </Field>
                </div>

                <Field label="Reason code">
                  <Input
                    value={reasonCode}
                    maxLength={256}
                    onChange={(event) => setReasonCode(event.target.value)}
                    required
                  />
                </Field>

                <Field label="Reason">
                  <Textarea
                    value={reasonText}
                    maxLength={4096}
                    onChange={(event) => setReasonText(event.target.value)}
                    required
                  />
                </Field>

                <DecisionEvidenceFields evidence={evidence} onChange={setEvidence} />

                <Button type="submit" loading={recording}>
                  Record replacement
                </Button>
              </form>
            ) : null}
          </DetailSection>
        </div>
      ) : null}
    </div>
  )
}
