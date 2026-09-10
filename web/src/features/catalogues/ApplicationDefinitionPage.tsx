import { useEffect, useState } from "react"
import { ArrowLeft, Pencil, Plus, Search } from "lucide-react"

import { ApiError } from "@/api"
import { Button } from "@/components/ui/Button"
import { CataloguePager } from "@/features/catalogues/CataloguePager"
import { InteractionDefinitionCreatePanel } from "@/features/catalogues/InteractionDefinitionCreatePanel"
import { InteractionDefinitionEditPanel } from "@/features/catalogues/InteractionDefinitionEditPanel"
import { ComponentEditPanel, DefinitionEditPanel } from "@/features/catalogues/TargetCatalogueEditPanels"
import { CreateComponentPanel, CreateDeploymentPanel } from "@/features/catalogues/TargetCatalogueForms"
import {
  listApplicationComponents,
  listApplicationDeployments,
  listInteractionDefinitions,
  readApplicationDefinition,
  type ApplicationComponentDto,
  type ApplicationDefinitionDto,
  type ApplicationDeploymentSummaryDto,
  type InteractionDefinitionSummaryDto,
} from "@/features/catalogues/targetCatalogueApi"
import { trafficSummary } from "@/features/catalogues/targetPresentation"

type Tab = "overview" | "components" | "interactions" | "deployments"
type TabFilters = { search: string; first: string; second: string; third: string }
const EMPTY_FILTERS: TabFilters = { search: "", first: "", second: "", third: "" }
const TAB_LABELS: Record<Tab, string> = {
  overview: "Overview",
  components: "Components",
  interactions: "Interactions",
  deployments: "Deployments",
}
const inputClass = "min-h-10 min-w-0 rounded-md border border-[#CBD5E1] bg-white px-3 py-2 text-sm text-[#172033] outline-none focus:border-[#2563EB] focus:ring-2 focus:ring-[#DBEAFE]"

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError ? caught : new ApiError(500, "InternalError", fallback)
}

function LoadingOrError({ loading, error }: { loading: boolean; error: ApiError | null }) {
  if (loading) return <div className="p-6 text-sm text-[#64748B]">Loading…</div>
  if (error) return <div className="p-6 text-sm text-red-700">{error.message}</div>
  return null
}

function TabToolbar({ tab, draft, onDraft, onApply }: { tab: Exclude<Tab, "overview">; draft: TabFilters; onDraft: (value: TabFilters) => void; onApply: () => void }) {
  return (
    <form className="grid gap-2 border-b border-[#E2E8F0] p-4 lg:grid-cols-[minmax(14rem,1fr)_repeat(3,minmax(8rem,12rem))_auto]" onSubmit={(event) => { event.preventDefault(); onApply() }}>
      <div className="relative min-w-0"><Search className="pointer-events-none absolute left-3 top-3 size-4 text-[#94A3B8]" aria-hidden="true" /><input className={`${inputClass} w-full pl-9`} value={draft.search} onChange={(event) => onDraft({ ...draft, search: event.target.value })} placeholder={`Search ${tab}`} aria-label={`Search ${tab}`} /></div>
      {tab === "components" ? (
        <><input className={inputClass} value={draft.first} onChange={(event) => onDraft({ ...draft, first: event.target.value })} placeholder="Type" aria-label="Component type" /><div className="hidden lg:block" /><div className="hidden lg:block" /></>
      ) : tab === "interactions" ? (
        <><input className={inputClass} value={draft.first} onChange={(event) => onDraft({ ...draft, first: event.target.value })} placeholder="Protocol" aria-label="Protocol" /><div className="hidden lg:block" /><div className="hidden lg:block" /></>
      ) : (
        <><input className={inputClass} value={draft.first} onChange={(event) => onDraft({ ...draft, first: event.target.value })} placeholder="Company" aria-label="Company" /><input className={inputClass} value={draft.second} onChange={(event) => onDraft({ ...draft, second: event.target.value })} placeholder="Environment" aria-label="Environment" /><input className={inputClass} value={draft.third} onChange={(event) => onDraft({ ...draft, third: event.target.value })} placeholder="Scope" aria-label="Scope" /></>
      )}
      <Button type="submit" variant="secondary">Apply</Button>
    </form>
  )
}

export function ApplicationDefinitionPage({ applicationId, onBack, onOpenDeployment }: { applicationId: string; onBack: () => void; onOpenDeployment: (deploymentId: string) => void }) {
  const [definition, setDefinition] = useState<ApplicationDefinitionDto | null>(null)
  const [tab, setTab] = useState<Tab>("overview")
  const [tabPage, setTabPage] = useState(1)
  const [tabPageSize, setTabPageSize] = useState(50)
  const [tabTotal, setTabTotal] = useState(0)
  const [draftFilters, setDraftFilters] = useState<TabFilters>(EMPTY_FILTERS)
  const [filters, setFilters] = useState<TabFilters>(EMPTY_FILTERS)
  const [components, setComponents] = useState<ApplicationComponentDto[]>([])
  const [interactions, setInteractions] = useState<InteractionDefinitionSummaryDto[]>([])
  const [deployments, setDeployments] = useState<ApplicationDeploymentSummaryDto[]>([])
  const [loading, setLoading] = useState(true)
  const [tabLoading, setTabLoading] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)
  const [tabError, setTabError] = useState<ApiError | null>(null)
  const [createOpen, setCreateOpen] = useState(false)
  const [definitionEditOpen, setDefinitionEditOpen] = useState(false)
  const [editingComponent, setEditingComponent] = useState<ApplicationComponentDto | null>(null)
  const [editingInteraction, setEditingInteraction] = useState<InteractionDefinitionSummaryDto | null>(null)
  const [reloadToken, setReloadToken] = useState(0)

  useEffect(() => {
    let active = true
    setLoading(true); setError(null)
    void readApplicationDefinition(applicationId)
      .then((result) => { if (active) setDefinition(result.definition) })
      .catch((caught) => { if (active) setError(errorFrom(caught, "Application Definition could not be loaded.")) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [applicationId])

  useEffect(() => {
    if (tab === "overview") return
    let active = true
    setTabLoading(true); setTabError(null)
    const acceptPage = (result: { total: number; pageSize: number }) => { if (active) { setTabTotal(result.total); setTabPageSize(result.pageSize) } }
    const pending = tab === "components"
      ? listApplicationComponents({ applicationId, page: tabPage, search: filters.search, componentType: filters.first, sort: "name" }).then((result) => { if (active) setComponents(result.items); acceptPage(result) })
      : tab === "interactions"
        ? listInteractionDefinitions({ applicationId, page: tabPage, search: filters.search, protocol: filters.first, sort: "source" }).then((result) => { if (active) setInteractions(result.items); acceptPage(result) })
        : listApplicationDeployments({ applicationId, page: tabPage, search: filters.search, companyReference: filters.first, environment: filters.second, scopeReference: filters.third, sort: "company" }).then((result) => { if (active) setDeployments(result.items); acceptPage(result) })
    void pending.catch((caught) => { if (active) setTabError(errorFrom(caught, "Definition details could not be loaded.")) }).finally(() => { if (active) setTabLoading(false) })
    return () => { active = false }
  }, [applicationId, tab, tabPage, filters, reloadToken])

  function selectTab(next: Tab) {
    setTabPage(1); setTabTotal(0); setDraftFilters(EMPTY_FILTERS); setFilters(EMPTY_FILTERS); setCreateOpen(false); setEditingComponent(null); setEditingInteraction(null); setTab(next)
  }
  function refreshTab(closeEditor = true) {
    setCreateOpen(false); if (closeEditor) { setEditingComponent(null); setEditingInteraction(null) }; setTabPage(1); setReloadToken((value) => value + 1)
  }

  if (loading || error) return <div className="mx-auto max-w-7xl"><section className="rounded-lg border border-[#E2E8F0] bg-white"><LoadingOrError loading={loading} error={error} /></section></div>
  if (!definition) return null

  return (
    <div className="mx-auto grid max-w-7xl gap-5">
      <div><Button variant="ghost" className="-ml-3" onClick={onBack}><ArrowLeft className="size-4" aria-hidden="true" />Definitions</Button></div>
      <header className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"><div><div className="text-xs font-semibold uppercase tracking-[0.16em] text-[#64748B]">Applications / Definitions</div><h1 className="mt-1 text-2xl font-bold text-[#172033]">{definition.displayName}</h1><p className="mt-2 text-sm text-[#64748B]">{definition.domain ?? "No domain"}{definition.ownerReference ? ` · Owner: ${definition.ownerReference}` : ""}</p></div><Button variant="secondary" onClick={() => setDefinitionEditOpen((value) => !value)}><Pencil className="size-4" aria-hidden="true" />Edit</Button></header>
      {definitionEditOpen ? <DefinitionEditPanel definition={definition} onChanged={(updated) => { setDefinition(updated); setDefinitionEditOpen(false) }} onRetired={onBack} onCancel={() => setDefinitionEditOpen(false)} /> : null}

      <div className="flex gap-1 border-b border-[#E2E8F0]">{(["overview", "components", "interactions", "deployments"] as const).map((item) => <button key={item} type="button" className={`border-b-2 px-4 py-3 text-sm font-semibold ${tab === item ? "border-[#2563EB] text-[#1D4ED8]" : "border-transparent text-[#64748B] hover:text-[#172033]"}`} onClick={() => selectTab(item)}>{TAB_LABELS[item]}</button>)}</div>

      <section className="overflow-hidden rounded-lg border border-[#E2E8F0] bg-white shadow-sm">
        {tab === "overview" ? <dl className="grid gap-x-8 gap-y-5 p-6 md:grid-cols-2"><div><dt className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">Name</dt><dd className="mt-1 text-sm font-medium text-[#172033]">{definition.displayName}</dd></div><div><dt className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">Domain</dt><dd className="mt-1 text-sm text-[#172033]">{definition.domain ?? "—"}</dd></div><div><dt className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">Owner</dt><dd className="mt-1 text-sm text-[#172033]">{definition.ownerReference ?? "—"}</dd></div><div><dt className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">Description</dt><dd className="mt-1 text-sm text-[#172033]">{definition.description ?? "—"}</dd></div></dl> : (
          <>
            <TabToolbar tab={tab} draft={draftFilters} onDraft={setDraftFilters} onApply={() => { setTabPage(1); setFilters({ search: draftFilters.search.trim(), first: draftFilters.first.trim(), second: draftFilters.second.trim(), third: draftFilters.third.trim() }) }} />
            {tabLoading || tabError ? <LoadingOrError loading={tabLoading} error={tabError} /> : tab === "components" ? (
              <><div className="flex items-center justify-between border-b border-[#E2E8F0] px-5 py-4"><h2 className="font-semibold text-[#172033]">Components</h2><Button onClick={() => { setEditingComponent(null); setCreateOpen((value) => !value) }}><Plus className="size-4" aria-hidden="true" />Add component</Button></div>{createOpen ? <CreateComponentPanel applicationId={applicationId} onCancel={() => setCreateOpen(false)} onCreated={() => refreshTab()} /> : null}{editingComponent ? <ComponentEditPanel component={editingComponent} onChanged={(updated) => { setComponents((items) => items.map((item) => item.componentId === updated.componentId ? updated : item)); setEditingComponent(null) }} onRetired={() => refreshTab()} onCancel={() => setEditingComponent(null)} /> : null}{components.length === 0 ? <div className="p-6 text-sm text-[#64748B]">No active components.</div> : <div className="overflow-x-auto"><table className="w-full min-w-[760px] text-left text-sm"><thead className="bg-[#F8FAFC] text-xs font-semibold uppercase tracking-wide text-[#64748B]"><tr><th className="px-5 py-3">Name</th><th className="px-5 py-3">Type</th><th className="px-5 py-3">Description</th><th className="w-20 px-5 py-3" /></tr></thead><tbody className="divide-y divide-[#E2E8F0]">{components.map((item) => <tr key={item.componentId}><td className="px-5 py-3 font-semibold text-[#172033]">{item.displayName}</td><td className="px-5 py-3 text-[#475569]">{item.componentType ?? "—"}</td><td className="px-5 py-3 text-[#475569]">{item.description ?? "—"}</td><td className="px-5 py-3"><Button variant="ghost" onClick={() => { setCreateOpen(false); setEditingComponent(item) }}>Edit</Button></td></tr>)}</tbody></table></div>}<CataloguePager page={tabPage} pageSize={tabPageSize} total={tabTotal} onPageChange={setTabPage} /></>
            ) : tab === "interactions" ? (
              <><div className="flex items-center justify-between border-b border-[#E2E8F0] px-5 py-4"><h2 className="font-semibold text-[#172033]">Interactions</h2><Button onClick={() => { setEditingInteraction(null); setCreateOpen((value) => !value) }}><Plus className="size-4" aria-hidden="true" />Add interaction</Button></div>{createOpen ? <InteractionDefinitionCreatePanel applicationId={applicationId} onCancel={() => setCreateOpen(false)} onCreated={() => refreshTab()} /> : null}{editingInteraction ? <InteractionDefinitionEditPanel interaction={editingInteraction} sourceName={editingInteraction.sourceComponentName} destinationName={editingInteraction.destinationComponentName} onChanged={() => refreshTab(false)} onRetired={() => refreshTab()} onCancel={() => setEditingInteraction(null)} /> : null}{interactions.length === 0 ? <div className="p-6 text-sm text-[#64748B]">No active interactions.</div> : <div className="overflow-x-auto"><table className="w-full min-w-[840px] text-left text-sm"><thead className="bg-[#F8FAFC] text-xs font-semibold uppercase tracking-wide text-[#64748B]"><tr><th className="px-5 py-3">Source</th><th className="px-5 py-3">Destination</th><th className="px-5 py-3">Traffic</th><th className="px-5 py-3 text-right">Deployments</th><th className="w-20 px-5 py-3" /></tr></thead><tbody className="divide-y divide-[#E2E8F0]">{interactions.map((item) => <tr key={item.interactionDefinitionId}><td className="px-5 py-3 font-semibold text-[#172033]">{item.sourceComponentName}</td><td className="px-5 py-3 font-semibold text-[#172033]">{item.destinationComponentName}</td><td className="px-5 py-3 text-[#475569]">{trafficSummary(item.trafficAlternatives)}</td><td className="px-5 py-3 text-right tabular-nums">{item.activeDeploymentCount}</td><td className="px-5 py-3"><Button variant="ghost" onClick={() => { setCreateOpen(false); setEditingInteraction(item) }}>Edit</Button></td></tr>)}</tbody></table></div>}<CataloguePager page={tabPage} pageSize={tabPageSize} total={tabTotal} onPageChange={setTabPage} /></>
            ) : (
              <><div className="flex items-center justify-between border-b border-[#E2E8F0] px-5 py-4"><h2 className="font-semibold text-[#172033]">Deployments</h2><Button onClick={() => setCreateOpen((value) => !value)}><Plus className="size-4" aria-hidden="true" />Add deployment</Button></div>{createOpen ? <CreateDeploymentPanel applicationId={applicationId} onCancel={() => setCreateOpen(false)} onCreated={() => refreshTab()} /> : null}{deployments.length === 0 ? <div className="p-6 text-sm text-[#64748B]">No active deployments.</div> : <div className="overflow-x-auto"><table className="w-full min-w-[760px] text-left text-sm"><thead className="bg-[#F8FAFC] text-xs font-semibold uppercase tracking-wide text-[#64748B]"><tr><th className="px-5 py-3">Company</th><th className="px-5 py-3">Environment</th><th className="px-5 py-3">Scope</th><th className="px-5 py-3 text-right">Interactions</th></tr></thead><tbody className="divide-y divide-[#E2E8F0]">{deployments.map((item) => <tr key={item.applicationDeploymentId} className="cursor-pointer hover:bg-[#F8FAFC]" onClick={() => onOpenDeployment(item.applicationDeploymentId)}><td className="px-5 py-3 font-semibold text-[#172033]">{item.companyReference}</td><td className="px-5 py-3 text-[#475569]">{item.environment}</td><td className="px-5 py-3 text-[#475569]">{item.scopeReference}</td><td className="px-5 py-3 text-right tabular-nums">{item.selectedInteractionCount} / {item.definedInteractionCount}</td></tr>)}</tbody></table></div>}<CataloguePager page={tabPage} pageSize={tabPageSize} total={tabTotal} onPageChange={setTabPage} /></>
            )}
          </>
        )}
      </section>
    </div>
  )
}
