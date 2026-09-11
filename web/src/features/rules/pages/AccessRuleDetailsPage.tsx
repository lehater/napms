import { useEffect, useState } from "react"
import { ArrowLeft, CircleAlert } from "lucide-react"

import { Button } from "@/design-system/components/Button"
import { Input } from "@/design-system/components/Field"
import { StatusBadge } from "@/design-system/components/StatusBadge"
import { DetailSection } from "@/design-system/patterns/detail/Detail"
import { displayName } from "@/features/catalogues/components/CatalogueIdentity"
import {
  getAccessRule,
  setAccessRuleEffectiveWindow,
  setAccessRuleOperationalState,
  type RuleDetailResponse,
} from "@/features/rules/api"
import { AccessRuleDetailSections } from "@/features/rules/components/AccessRuleDetailSections"
import { ApiError } from "@/lib/api"
import { toLocalDateTimeInput, toOffsetAwareIso } from "@/lib/datetime"

export function AccessRuleDetailsPage({
  ruleId,
  onBack,
  onOpenDecision,
}: {
  ruleId: string
  onBack: () => void
  onOpenDecision: (decisionId: string) => void
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
      setWindowStart(toLocalDateTimeInput(response.rule.effectiveWindow?.start ?? null))
      setWindowEnd(toLocalDateTimeInput(response.rule.effectiveWindow?.end ?? null))
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Access Rule could not be loaded."))
    } finally {
      setLoading(false)
    }
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
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Rule state could not be changed."))
    } finally { setMutating(false) }
  }

  async function saveWindow() {
    if (!detail || detail.capabilities.setEffectiveWindow !== "Permitted") return
    setWindowMutating(true); setError(null); setMessage(null)
    try {
      const result = await setAccessRuleEffectiveWindow(ruleId, { start: toOffsetAwareIso(windowStart), end: toOffsetAwareIso(windowEnd) })
      setMessage(result.outcome === "Updated" ? "EffectiveWindow updated." : "Rule already has this EffectiveWindow.")
      await load()
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : new ApiError(422, "InvalidEffectiveWindow", "Select a valid start and end time."))
    } finally { setWindowMutating(false) }
  }

  async function clearWindow() {
    if (!detail || detail.capabilities.setEffectiveWindow !== "Permitted") return
    setWindowMutating(true); setError(null); setMessage(null)
    try {
      const result = await setAccessRuleEffectiveWindow(ruleId, null)
      setMessage(result.outcome === "Updated" ? "EffectiveWindow cleared." : "Rule already has no EffectiveWindow restriction.")
      await load()
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "EffectiveWindow could not be cleared."))
    } finally { setWindowMutating(false) }
  }

  return (
    <div className="mx-auto max-w-[1180px]">
      <div className="mb-4"><Button variant="ghost" onClick={onBack}><ArrowLeft className="size-4" aria-hidden="true" />Access Rules</Button></div>
      <header className="mb-6">
        <div className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#64748B]">Access Policy / Rule Details</div>
        <h1 className="break-all text-[28px] font-bold tracking-tight text-[#172033]">{ruleId}</h1>
        {detail ? <p className="mt-2 text-sm text-[#64748B]">{displayName(detail.rule.catalogue?.sourceDisplayName, detail.rule.semanticIdentity.sourceComponentDeploymentId)} → {displayName(detail.rule.catalogue?.destinationDisplayName, detail.rule.semanticIdentity.destinationComponentDeploymentId)} · {displayName(detail.rule.catalogue?.dcsDisplayName, detail.rule.semanticIdentity.dcsContractRevisionId)}</p> : null}
      </header>

      {error ? <div role="alert" className="mb-4 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800"><div className="flex gap-3"><CircleAlert className="mt-0.5 size-4 shrink-0" aria-hidden="true" /><div><div className="font-semibold">{error.code}</div><div className="mt-1">{error.message}</div>{error.correlationId ? <div className="mt-2 text-xs">Correlation: {error.correlationId}</div> : null}</div></div></div> : null}
      {message ? <div role="status" className="mb-4 rounded-md border border-green-200 bg-green-50 p-4 text-sm text-green-800">{message}</div> : null}

      {loading && !detail ? <div className="rounded-lg border border-[#E2E8F0] bg-white p-8 text-sm text-[#64748B]">Loading Access Rule…</div> : detail ? <div className="grid gap-6">
        <DetailSection title="Operational state">
          <div className="flex flex-wrap items-start justify-between gap-4"><div><div className="flex items-center gap-3"><StatusBadge>{detail.rule.operationalState}</StatusBadge><span className="text-xs text-[#64748B]">mutation: {detail.capabilities.setOperationalState}</span></div></div>{detail.capabilities.setOperationalState === "Permitted" ? <Button loading={mutating} onClick={() => void changeState()}>Set {detail.rule.operationalState === "Active" ? "Inactive" : "Active"}</Button> : null}</div>
        </DetailSection>

        <DetailSection title="EffectiveWindow">
          <p className="text-sm text-[#64748B]">Half-open interval: start ≤ asOf &lt; end. No window means no time-window restriction.</p>
          <div className="mt-2 text-xs text-[#64748B]">mutation: {detail.capabilities.setEffectiveWindow}</div>
          <div className="mt-5 grid gap-4 lg:grid-cols-2"><label className="grid gap-2 text-sm font-medium text-[#334155]">Start<Input type="datetime-local" step="1" value={windowStart} onChange={(event) => setWindowStart(event.target.value)} disabled={detail.capabilities.setEffectiveWindow !== "Permitted"} /></label><label className="grid gap-2 text-sm font-medium text-[#334155]">End<Input type="datetime-local" step="1" value={windowEnd} onChange={(event) => setWindowEnd(event.target.value)} disabled={detail.capabilities.setEffectiveWindow !== "Permitted"} /></label></div>
          {detail.capabilities.setEffectiveWindow === "Permitted" ? <div className="mt-4 flex flex-wrap justify-end gap-2"><Button variant="secondary" loading={windowMutating} disabled={!detail.rule.effectiveWindow} onClick={() => void clearWindow()}>Clear window</Button><Button loading={windowMutating} disabled={!windowStart || !windowEnd} onClick={() => void saveWindow()}>Save window</Button></div> : null}
        </DetailSection>

        <AccessRuleDetailSections detail={detail} onOpenDecision={onOpenDecision} />
      </div> : null}
    </div>
  )
}
