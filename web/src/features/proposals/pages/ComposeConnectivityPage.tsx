import { useEffect, useMemo, useState } from "react"
import { ArrowRight, CheckCircle2, ShieldCheck } from "lucide-react"

import { Button } from "@/design-system/components/Button"
import { Field, Select } from "@/design-system/components/Field"
import { ErrorState } from "@/design-system/components/PageState"
import { SearchInput } from "@/design-system/components/SearchInput"
import { PageHeader } from "@/design-system/layout/PageHeader"
import { PageWorkspace } from "@/design-system/layout/PageWorkspace"
import { Surface } from "@/design-system/primitives/Surface"
import { displayName, shortId, trafficAlternativeText } from "@/features/catalogues/components/CatalogueIdentity"
import type { ProposalInteraction } from "@/features/catalogues/model/interaction"
import { listProposalInteractions, listProposalScopes, submitProposal } from "@/features/proposals/api"
import type { ProposalResult } from "@/features/proposals/model/result"
import { ApiError } from "@/lib/api"
import { useDebouncedValue } from "@/lib/useDebouncedValue"

function optionLabel(name: string | null | undefined, id: string) {
  const readable = name?.trim()
  return readable ? `${readable} · ${shortId(id)}` : shortId(id)
}

function dcsOptionLabel(item: ProposalInteraction) {
  const base = optionLabel(item.catalogue?.dcsDisplayName, item.dcsContractRevisionId)
  const traffic = item.catalogue?.trafficAlternatives ?? []
  return traffic.length === 0 ? base : `${base} — ${traffic.map(trafficAlternativeText).join(" | ")}`
}

export function ComposeConnectivityPage() {
  const [scopes, setScopes] = useState<string[]>([])
  const [ambiguousScopes, setAmbiguousScopes] = useState<string[]>([])
  const [scope, setScope] = useState("")
  const [interactions, setInteractions] = useState<ProposalInteraction[]>([])
  const [interactionPage, setInteractionPage] = useState(1)
  const [hasMoreInteractions, setHasMoreInteractions] = useState(false)
  const [searchInput, setSearchInput] = useState("")
  const search = useDebouncedValue(searchInput.trim(), 300)
  const [source, setSource] = useState("")
  const [destination, setDestination] = useState("")
  const [dcs, setDcs] = useState("")
  const [loadingScopes, setLoadingScopes] = useState(true)
  const [loadingInteractions, setLoadingInteractions] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)
  const [result, setResult] = useState<ProposalResult | null>(null)

  useEffect(() => {
    let active = true
    void listProposalScopes()
      .then((payload) => {
        if (!active) return
        const values = payload.scopes.map((item) => item.scope)
        setScopes(values)
        setAmbiguousScopes(payload.ambiguousScopes.map((item) => item.scope))
        if (values.length === 1) setScope(values[0])
      })
      .catch((caught) => { if (active) setError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Scopes could not be loaded.")) })
      .finally(() => { if (active) setLoadingScopes(false) })
    return () => { active = false }
  }, [])

  useEffect(() => { setInteractionPage(1) }, [search])

  useEffect(() => {
    setInteractions([])
    setHasMoreInteractions(false)
    setSource("")
    setDestination("")
    setDcs("")
    setResult(null)
    if (!scope) return
    let active = true
    setLoadingInteractions(true)
    setError(null)
    void listProposalInteractions(scope, interactionPage, search)
      .then((response) => { if (active) { setInteractions(response.items); setHasMoreInteractions(response.hasMore) } })
      .catch((caught) => { if (active) setError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Available interactions could not be loaded.")) })
      .finally(() => { if (active) setLoadingInteractions(false) })
    return () => { active = false }
  }, [scope, interactionPage, search])

  const sourceOptions = useMemo(() => {
    const values = new Map<string, string | null | undefined>()
    for (const item of interactions) if (!values.has(item.sourceComponentDeploymentId)) values.set(item.sourceComponentDeploymentId, item.catalogue?.sourceDisplayName)
    return [...values.entries()]
  }, [interactions])
  const destinationOptions = useMemo(() => {
    const values = new Map<string, string | null | undefined>()
    for (const item of interactions) if (item.sourceComponentDeploymentId === source && !values.has(item.destinationComponentDeploymentId)) values.set(item.destinationComponentDeploymentId, item.catalogue?.destinationDisplayName)
    return [...values.entries()]
  }, [interactions, source])
  const dcsOptions = useMemo(() => {
    const values = new Map<string, ProposalInteraction>()
    for (const item of interactions) if (item.sourceComponentDeploymentId === source && item.destinationComponentDeploymentId === destination && !values.has(item.dcsContractRevisionId)) values.set(item.dcsContractRevisionId, item)
    return [...values.values()]
  }, [interactions, source, destination])
  const selectedInteraction = useMemo(() => interactions.find((item) => item.sourceComponentDeploymentId === source && item.destinationComponentDeploymentId === destination && item.dcsContractRevisionId === dcs) ?? null, [interactions, source, destination, dcs])

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    if (!scope || !source || !destination || !dcs) return
    setSubmitting(true)
    setError(null)
    setResult(null)
    try {
      setResult(await submitProposal({ authorityScope: scope, sourceComponentDeploymentId: source, destinationComponentDeploymentId: destination, dcsContractRevisionId: dcs }))
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "The proposal could not be submitted."))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <PageWorkspace width="content">
      <PageHeader title="Compose Connectivity" description="Select a valid application-backed interaction. Human-readable catalogue labels are presentation metadata; stable deployment and DCS IDs remain the proposal identity." />
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
        <Surface className="p-5 md:p-6">
          <form onSubmit={submit} className="grid gap-5">
            <div><h2 className="text-base font-semibold text-[var(--napms-color-text-primary)]">Proposal identity</h2><p className="mt-1 text-sm text-[var(--napms-color-text-secondary)]">Only authorized catalogue-backed directed interactions are selectable.</p></div>
            <Field label="Governance scope">
              <Select value={scope} onChange={(event) => { setScope(event.target.value); setInteractionPage(1) }} disabled={loadingScopes} required>
                <option value="">{loadingScopes ? "Loading scopes…" : "Select scope"}</option>
                {scopes.map((value) => <option key={value} value={value}>{value}</option>)}
              </Select>
            </Field>
            <Field label="Search interactions" hint="Server-side search by deployment label, DCS label or stable UUID.">
              <SearchInput value={searchInput} onChange={(event) => setSearchInput(event.target.value)} disabled={!scope} placeholder="e.g. Orders, Checkout, HTTPS" aria-label="Search interactions" />
            </Field>
            <div className="grid gap-5 lg:grid-cols-2">
              <Field label="Source Component Deployment" hint="Readable label first; stable deployment ID remains visible.">
                <Select value={source} onChange={(event) => { setSource(event.target.value); setDestination(""); setDcs(""); setResult(null) }} disabled={!scope || loadingInteractions} required>
                  <option value="">{loadingInteractions ? "Loading interactions…" : "Select source"}</option>
                  {sourceOptions.map(([id, name]) => <option key={id} value={id}>{optionLabel(name, id)}</option>)}
                </Select>
              </Field>
              <Field label="Destination Component Deployment">
                <Select value={destination} onChange={(event) => { setDestination(event.target.value); setDcs(""); setResult(null) }} disabled={!source} required>
                  <option value="">Select destination</option>
                  {destinationOptions.map(([id, name]) => <option key={id} value={id}>{optionLabel(name, id)}</option>)}
                </Select>
              </Field>
            </div>
            <Field label="Directed Communication Specification revision" hint="DCS label plus decoded immutable traffic summary.">
              <Select value={dcs} onChange={(event) => { setDcs(event.target.value); setResult(null) }} disabled={!destination} required>
                <option value="">Select DCS revision</option>
                {dcsOptions.map((item) => <option key={item.dcsContractRevisionId} value={item.dcsContractRevisionId}>{dcsOptionLabel(item)}</option>)}
              </Select>
            </Field>
            {selectedInteraction ? (
              <div className="rounded-[var(--napms-control-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface-subtle)] p-4 text-sm">
                <div className="font-semibold text-[var(--napms-color-text-primary)]">{displayName(selectedInteraction.catalogue?.sourceDisplayName, selectedInteraction.sourceComponentDeploymentId)} → {displayName(selectedInteraction.catalogue?.destinationDisplayName, selectedInteraction.destinationComponentDeploymentId)}</div>
                <div className="mt-1 text-[var(--napms-color-text-body)]">{displayName(selectedInteraction.catalogue?.dcsDisplayName, selectedInteraction.dcsContractRevisionId)}</div>
                {(selectedInteraction.catalogue?.trafficAlternatives.length ?? 0) > 0 ? <div className="mt-2 grid gap-1 text-xs text-[var(--napms-color-text-secondary)]">{selectedInteraction.catalogue?.trafficAlternatives.map((alternative, index) => <div key={index}>{trafficAlternativeText(alternative)}</div>)}</div> : null}
              </div>
            ) : null}
            {!loadingInteractions && scope && interactions.length === 0 ? <div className="rounded-[var(--napms-control-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface-subtle)] p-4 text-sm text-[var(--napms-color-text-secondary)]">{search ? "No authorized interactions match this search." : "No authorized interactions are available in this scope."}</div> : null}
            <div className="flex items-center justify-between rounded-[var(--napms-control-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface-subtle)] px-3 py-2">
              <span className="text-xs text-[var(--napms-color-text-secondary)]">Interaction page {interactionPage}{search ? ` · search: ${search}` : ""}</span>
              <div className="flex gap-2"><Button type="button" variant="secondary" size="sm" disabled={interactionPage === 1 || loadingInteractions} onClick={() => setInteractionPage((value) => Math.max(1, value - 1))}>Previous</Button><Button type="button" variant="secondary" size="sm" disabled={!hasMoreInteractions || loadingInteractions} onClick={() => setInteractionPage((value) => value + 1)}>Next</Button></div>
            </div>
            {error ? <ErrorState message={`${error.code}: ${error.message}${error.correlationId ? ` · Correlation: ${error.correlationId}` : ""}`} /> : null}
            <div className="flex justify-end border-t border-[var(--napms-color-border)] pt-5"><Button type="submit" loading={submitting} disabled={!scope || !source || !destination || !dcs}>Submit proposal<ArrowRight className="size-4" aria-hidden="true" /></Button></div>
          </form>
        </Surface>

        <aside className="grid content-start gap-4">
          <Surface className="p-5">
            <div className="flex items-center gap-2 text-sm font-semibold text-[var(--napms-color-text-primary)]"><ShieldCheck className="size-4 text-[var(--napms-color-primary)]" aria-hidden="true" />Decision boundary</div>
            <p className="mt-2 text-sm leading-6 text-[var(--napms-color-text-secondary)]">In local-dev, structurally valid and authorized proposals use the explicit <code className="mx-1 rounded bg-[var(--napms-color-surface-muted)] px-1 py-0.5 text-xs">local-dev:allowed</code> decision adapter.</p>
          </Surface>
          {ambiguousScopes.length > 0 ? <section className="rounded-[var(--napms-surface-radius)] border border-[var(--napms-color-warning-dot)] bg-[var(--napms-color-warning-bg)] p-5 text-sm text-[var(--napms-color-warning)]"><div className="font-semibold">Authority ambiguity detected</div><p className="mt-2">{ambiguousScopes.length} scope(s) are hidden from permitted choices and remain fail-closed.</p></section> : null}
          {result ? (
            <section className={`rounded-[var(--napms-surface-radius)] border p-5 ${result.outcome === "NotAllowed" ? "border-[var(--napms-color-danger-dot)] bg-[var(--napms-color-danger-bg)]" : "border-[var(--napms-color-success-dot)] bg-[var(--napms-color-success-bg)]"}`} aria-live="polite">
              {result.outcome === "NotAllowed" ? <><div className="font-semibold text-[var(--napms-color-danger)]">NotAllowed</div><p className="mt-2 text-sm text-[var(--napms-color-danger)]">The proposal produced no authoritative Access Rule.</p></> : <><div className="flex items-center gap-2 font-semibold text-[var(--napms-color-success)]"><CheckCircle2 className="size-4" aria-hidden="true" />{result.outcome}</div><dl className="mt-4 grid gap-3 text-sm text-[var(--napms-color-text-primary)]"><div><dt className="text-xs uppercase tracking-wide text-[var(--napms-color-success)]">Interaction</dt><dd className="mt-1">{displayName(result.rule.catalogue?.sourceDisplayName, result.rule.semanticIdentity.sourceComponentDeploymentId)} → {displayName(result.rule.catalogue?.destinationDisplayName, result.rule.semanticIdentity.destinationComponentDeploymentId)}</dd><dd className="mt-1 text-xs">{displayName(result.rule.catalogue?.dcsDisplayName, result.rule.semanticIdentity.dcsContractRevisionId)}</dd></div><div><dt className="text-xs uppercase tracking-wide text-[var(--napms-color-success)]">Rule ID</dt><dd className="mt-1 break-all font-mono">{result.rule.ruleId}</dd></div><div><dt className="text-xs uppercase tracking-wide text-[var(--napms-color-success)]">State</dt><dd className="mt-1 font-semibold">{result.rule.operationalState}</dd></div><div><dt className="text-xs uppercase tracking-wide text-[var(--napms-color-success)]">Decision</dt><dd className="mt-1 break-all font-mono">{result.rule.decisionReference ?? "—"}</dd></div></dl></>}
            </section>
          ) : null}
        </aside>
      </div>
    </PageWorkspace>
  )
}
