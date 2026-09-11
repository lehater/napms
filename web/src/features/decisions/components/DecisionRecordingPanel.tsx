import { useEffect, useState } from "react"
import { Plus } from "lucide-react"

import { Alert } from "@/design-system/components/Alert"
import { Button } from "@/design-system/components/Button"
import { Field, Input, Select, Textarea } from "@/design-system/components/Field"
import { CatalogueInteractionSelector } from "@/features/catalogues/components/CatalogueInteractionSelector"
import { shortId } from "@/features/catalogues/components/CatalogueIdentity"
import type { ProposalInteraction } from "@/features/catalogues/model/interaction"
import {
  listConnectivityDecisionInteractions,
  listConnectivityDecisionScopes,
  recordConnectivityDecision,
  type ConnectivityDecisionOutcome,
  type DecisionEvidenceReferenceDto,
} from "@/features/decisions/api"
import {
  DecisionEvidenceFields,
  type DecisionEvidenceDraft,
} from "@/features/decisions/components/DecisionEvidenceFields"
import { ApiError } from "@/lib/api"
import { nowLocalDateTimeInput, toOffsetAwareIso } from "@/lib/datetime"
import { useDebouncedValue } from "@/lib/useDebouncedValue"

function normalizeEvidence(evidence: DecisionEvidenceDraft[]): DecisionEvidenceReferenceDto[] | null {
  const populated = evidence.filter((item) => item.kind.trim() || item.reference.trim())
  if (populated.some((item) => !item.kind.trim() || !item.reference.trim())) return null
  return populated.map((item) => ({ kind: item.kind.trim(), reference: item.reference.trim() }))
}

export function DecisionRecordingPanel({ onRecorded }: { onRecorded: () => void }) {
  const [scopes, setScopes] = useState<string[]>([])
  const [ambiguousDecideScopes, setAmbiguousDecideScopes] = useState<string[]>([])
  const [scope, setScope] = useState("")
  const [loadingScopes, setLoadingScopes] = useState(true)
  const [interactions, setInteractions] = useState<ProposalInteraction[]>([])
  const [interactionPage, setInteractionPage] = useState(1)
  const [hasMoreInteractions, setHasMoreInteractions] = useState(false)
  const [loadingInteractions, setLoadingInteractions] = useState(false)
  const [searchInput, setSearchInput] = useState("")
  const search = useDebouncedValue(searchInput.trim(), 300)
  const [source, setSource] = useState("")
  const [destination, setDestination] = useState("")
  const [dcs, setDcs] = useState("")
  const [outcome, setOutcome] = useState<ConnectivityDecisionOutcome>("Allowed")
  const [validFrom, setValidFrom] = useState(nowLocalDateTimeInput())
  const [validUntil, setValidUntil] = useState("")
  const [reasonCode, setReasonCode] = useState("")
  const [reasonText, setReasonText] = useState("")
  const [evidence, setEvidence] = useState<DecisionEvidenceDraft[]>([{ kind: "", reference: "" }])
  const [recording, setRecording] = useState(false)
  const [recordError, setRecordError] = useState<ApiError | null>(null)
  const [recordMessage, setRecordMessage] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    setLoadingScopes(true)
    setRecordError(null)
    void listConnectivityDecisionScopes()
      .then((result) => {
        if (!active) return
        const values = result.scopes.map((item) => item.scope)
        setScopes(values)
        setAmbiguousDecideScopes(result.ambiguousScopes.map((item) => item.scope))
        if (values.length === 1) setScope(values[0])
      })
      .catch((caught) => {
        if (!active) return
        setRecordError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Decision scopes could not be loaded."))
      })
      .finally(() => { if (active) setLoadingScopes(false) })
    return () => { active = false }
  }, [])

  useEffect(() => { setInteractionPage(1) }, [search])

  useEffect(() => {
    setInteractions([]); setHasMoreInteractions(false); setSource(""); setDestination(""); setDcs("")
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
        setRecordError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Decision interactions could not be loaded."))
      })
      .finally(() => { if (active) setLoadingInteractions(false) })
    return () => { active = false }
  }, [scope, interactionPage, search])

  function resetRecordForm() {
    setSource(""); setDestination(""); setDcs(""); setOutcome("Allowed")
    setValidFrom(nowLocalDateTimeInput()); setValidUntil(""); setReasonCode(""); setReasonText("")
    setEvidence([{ kind: "", reference: "" }])
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    if (!scope || !source || !destination || !dcs) return
    if (!reasonCode.trim() || !reasonText.trim()) { setRecordError(new ApiError(422, "ValidationError", "Reason code and reason must both be non-empty.")); return }
    const evidenceReferences = normalizeEvidence(evidence)
    if (evidenceReferences === null) { setRecordError(new ApiError(422, "ValidationError", "Each evidence reference requires both kind and reference.")); return }
    let start: string
    let end: string | null
    try {
      start = toOffsetAwareIso(validFrom)
      end = validUntil ? toOffsetAwareIso(validUntil) : null
      if (end && new Date(start).getTime() >= new Date(end).getTime()) throw new Error("invalid validity")
    } catch {
      setRecordError(new ApiError(422, "InvalidDecisionValidity", "Validity requires a valid start and an optional end after the start.")); return
    }
    setRecording(true); setRecordError(null); setRecordMessage(null)
    try {
      const result = await recordConnectivityDecision({ authorityScope: scope, sourceComponentDeploymentId: source, destinationComponentDeploymentId: destination, dcsContractRevisionId: dcs, outcome, validFrom: start, validUntil: end, reasonCode: reasonCode.trim(), reasonText: reasonText.trim(), evidenceReferences })
      setRecordMessage(result.outcome === "Recorded" ? `Decision ${shortId(result.decision.decisionId)} recorded.` : `Equivalent current Decision ${shortId(result.decision.decisionId)} resolved.`)
      resetRecordForm()
      onRecorded()
    } catch (caught) {
      setRecordError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Connectivity Decision could not be recorded."))
    } finally { setRecording(false) }
  }

  return (
    <form onSubmit={submit} className="self-start rounded-[var(--napms-surface-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)] p-5 shadow-[var(--napms-surface-shadow)]">
      <div className="mb-5 flex items-center gap-2"><Plus className="size-4 text-[var(--napms-color-primary)]" aria-hidden="true" /><h2 className="text-base font-semibold text-[var(--napms-color-text-primary)]">Record final Decision</h2></div>
      {ambiguousDecideScopes.length > 0 ? <Alert tone="warning" className="mb-4">{ambiguousDecideScopes.length} DecideConnectivity scope(s) are ambiguous and cannot be selected.</Alert> : null}
      {!loadingScopes && scopes.length === 0 ? <Alert className="mb-4">No unambiguous DecideConnectivity scope is currently admitted. Read access to Decisions is independent.</Alert> : null}
      {recordError ? <Alert role="alert" tone="danger" className="mb-4"><div className="font-semibold">{recordError.code}</div><div className="mt-1">{recordError.message}</div></Alert> : null}
      {recordMessage ? <Alert role="status" tone="success" className="mb-4">{recordMessage}</Alert> : null}
      <div className="grid gap-4">
        <Field label="Decision Governance Scope"><Select value={scope} onChange={(event) => { setScope(event.target.value); setInteractionPage(1) }} disabled={loadingScopes || scopes.length === 0} required><option value="">{loadingScopes ? "Loading scopes…" : "Select scope"}</option>{scopes.map((value) => <option key={value} value={value}>{value}</option>)}</Select></Field>
        <CatalogueInteractionSelector interactions={interactions} searchInput={searchInput} onSearchInputChange={setSearchInput} searchDisabled={!scope} searchLabel="Search exact ACC interaction" loading={loadingInteractions} disabled={!scope} source={source} onSourceChange={(value) => { setSource(value); setDestination(""); setDcs("") }} destination={destination} onDestinationChange={(value) => { setDestination(value); setDcs("") }} dcs={dcs} onDcsChange={setDcs} />
        <div className="flex items-center justify-between text-xs text-[var(--napms-color-text-secondary)]"><span>Interaction page {interactionPage}{loadingInteractions ? " · loading" : ""}</span><div className="flex gap-2"><button type="button" className="font-semibold text-[var(--napms-color-primary)] disabled:text-[var(--napms-color-text-muted)]" disabled={interactionPage === 1 || loadingInteractions} onClick={() => setInteractionPage((value) => Math.max(1, value - 1))}>Previous</button><button type="button" className="font-semibold text-[var(--napms-color-primary)] disabled:text-[var(--napms-color-text-muted)]" disabled={!hasMoreInteractions || loadingInteractions} onClick={() => setInteractionPage((value) => value + 1)}>Next</button></div></div>
        <Field label="Final outcome"><Select value={outcome} onChange={(event) => setOutcome(event.target.value as ConnectivityDecisionOutcome)} required><option value="Allowed">Allowed</option><option value="NotAllowed">NotAllowed</option></Select></Field>
        <div className="grid gap-4 sm:grid-cols-2"><Field label="Valid from"><Input type="datetime-local" step="1" value={validFrom} onChange={(event) => setValidFrom(event.target.value)} required /></Field><Field label="Valid until" hint="Optional; leave empty for open-ended validity."><Input type="datetime-local" step="1" value={validUntil} onChange={(event) => setValidUntil(event.target.value)} /></Field></div>
        <Field label="Reason code"><Input value={reasonCode} maxLength={256} onChange={(event) => setReasonCode(event.target.value)} required /></Field>
        <Field label="Reason"><Textarea value={reasonText} maxLength={4096} onChange={(event) => setReasonText(event.target.value)} required /></Field>
        <DecisionEvidenceFields evidence={evidence} onChange={setEvidence} />
        <Button type="submit" loading={recording} disabled={loadingScopes || scopes.length === 0 || !scope || !source || !destination || !dcs}>Record Decision</Button>
      </div>
    </form>
  )
}
