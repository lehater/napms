import { useEffect, useState } from "react"
import { ArrowLeft } from "lucide-react"

import { Button } from "@/design-system/components/Button"
import { Field, Input } from "@/design-system/components/Field"
import { ErrorState, LoadingState } from "@/design-system/components/PageState"
import { PageHeader } from "@/design-system/layout/PageHeader"
import { PageWorkspace } from "@/design-system/layout/PageWorkspace"
import { DetailSection } from "@/design-system/patterns/detail/Detail"
import { displayName } from "@/features/catalogues/components/CatalogueIdentity"
import { getAccessRule, setAccessRuleEffectiveWindow, setAccessRuleOperationalState, type RuleDetailResponse } from "@/features/rules/api"
import { AccessRuleDetailSections } from "@/features/rules/components/AccessRuleDetailSections"
import { RuleOperationalStatus } from "@/features/rules/components/RuleStatus"
import { ApiError } from "@/lib/api"
import { toLocalDateTimeInput, toOffsetAwareIso } from "@/lib/datetime"

export function AccessRuleDetailsPage({ ruleId, onBack, onOpenDecision }: { ruleId: string; onBack: () => void; onOpenDecision: (decisionId: string) => void }) {
  const [detail, setDetail] = useState<RuleDetailResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [mutating, setMutating] = useState(false)
  const [windowMutating, setWindowMutating] = useState(false)
  const [windowStart, setWindowStart] = useState("")
  const [windowEnd, setWindowEnd] = useState("")
  const [error, setError] = useState<ApiError | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  async function load() {
    setLoading(true); setError(null)
    try {
      const response = await getAccessRule(ruleId)
      setDetail(response)
      setWindowStart(toLocalDateTimeInput(response.rule.effectiveWindow?.start ?? null))
      setWindowEnd(toLocalDateTimeInput(response.rule.effectiveWindow?.end ?? null))
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Access Rule could not be loaded."))
    } finally { setLoading(false) }
  }

  useEffect(() => { void load() }, [ruleId])

  async function changeState() {
    if (!detail || detail.capabilities.setOperationalState !== "Permitted") return
    const targetState = detail.rule.operationalState === "Active" ? "Inactive" : "Active"
    setMutating(true); setError(null); setMessage(null)
    try {
      const result = await setAccessRuleOperationalState(ruleId, targetState)
      setMessage(result.outcome === "Updated" ? `Rule state changed to ${targetState}.` : `Rule is already ${targetState}.`)
      await load()
    } catch (caught) { setError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Rule state could not be changed.")) }
    finally { setMutating(false) }
  }

  async function saveWindow() {
    if (!detail || detail.capabilities.setEffectiveWindow !== "Permitted") return
    setWindowMutating(true); setError(null); setMessage(null)
    try {
      const result = await setAccessRuleEffectiveWindow(ruleId, { start: toOffsetAwareIso(windowStart), end: toOffsetAwareIso(windowEnd) })
      setMessage(result.outcome === "Updated" ? "EffectiveWindow updated." : "Rule already has this EffectiveWindow.")
      await load()
    } catch (caught) { setError(caught instanceof ApiError ? caught : new ApiError(422, "InvalidEffectiveWindow", "Select a valid start and end time.")) }
    finally { setWindowMutating(false) }
  }

  async function clearWindow() {
    if (!detail || detail.capabilities.setEffectiveWindow !== "Permitted") return
    setWindowMutating(true); setError(null); setMessage(null)
    try {
      const result = await setAccessRuleEffectiveWindow(ruleId, null)
      setMessage(result.outcome === "Updated" ? "EffectiveWindow cleared." : "Rule already has no EffectiveWindow restriction.")
      await load()
    } catch (caught) { setError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "EffectiveWindow could not be cleared.")) }
    finally { setWindowMutating(false) }
  }

  return (
    <PageWorkspace width="content">
      <div><Button variant="ghost" size="sm" onClick={onBack}><ArrowLeft className="size-4" aria-hidden="true" />Access Rules</Button></div>
      <PageHeader
        title={ruleId}
        description={detail ? `${displayName(detail.rule.catalogue?.sourceDisplayName, detail.rule.semanticIdentity.sourceComponentDeploymentId)} → ${displayName(detail.rule.catalogue?.destinationDisplayName, detail.rule.semanticIdentity.destinationComponentDeploymentId)} · ${displayName(detail.rule.catalogue?.dcsDisplayName, detail.rule.semanticIdentity.dcsContractRevisionId)}` : undefined}
      />
      {error ? <ErrorState message={`${error.code}: ${error.message}${error.correlationId ? ` · Correlation: ${error.correlationId}` : ""}`} /> : null}
      {message ? <div role="status" className="rounded-[var(--napms-control-radius)] border border-[var(--napms-color-success-dot)] bg-[var(--napms-color-success-bg)] p-4 text-sm text-[var(--napms-color-success)]">{message}</div> : null}
      {loading && !detail ? <LoadingState>Loading Access Rule…</LoadingState> : detail ? (
        <div className="grid gap-6">
          <DetailSection title="Operational state">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="flex items-center gap-3"><RuleOperationalStatus state={detail.rule.operationalState} /><span className="text-xs text-[var(--napms-color-text-secondary)]">mutation: {detail.capabilities.setOperationalState}</span></div>
              {detail.capabilities.setOperationalState === "Permitted" ? <Button loading={mutating} onClick={() => void changeState()}>Set {detail.rule.operationalState === "Active" ? "Inactive" : "Active"}</Button> : null}
            </div>
          </DetailSection>
          <DetailSection title="EffectiveWindow">
            <p className="text-sm text-[var(--napms-color-text-secondary)]">Half-open interval: start ≤ asOf &lt; end. No window means no time-window restriction.</p>
            <div className="mt-2 text-xs text-[var(--napms-color-text-secondary)]">mutation: {detail.capabilities.setEffectiveWindow}</div>
            <div className="mt-5 grid gap-4 lg:grid-cols-2">
              <Field label="Start"><Input type="datetime-local" step="1" value={windowStart} onChange={(event) => setWindowStart(event.target.value)} disabled={detail.capabilities.setEffectiveWindow !== "Permitted"} /></Field>
              <Field label="End"><Input type="datetime-local" step="1" value={windowEnd} onChange={(event) => setWindowEnd(event.target.value)} disabled={detail.capabilities.setEffectiveWindow !== "Permitted"} /></Field>
            </div>
            {detail.capabilities.setEffectiveWindow === "Permitted" ? <div className="mt-4 flex flex-wrap justify-end gap-2"><Button variant="secondary" loading={windowMutating} disabled={!detail.rule.effectiveWindow} onClick={() => void clearWindow()}>Clear window</Button><Button loading={windowMutating} disabled={!windowStart || !windowEnd} onClick={() => void saveWindow()}>Save window</Button></div> : null}
          </DetailSection>
          <AccessRuleDetailSections detail={detail} onOpenDecision={onOpenDecision} />
        </div>
      ) : null}
    </PageWorkspace>
  )
}
