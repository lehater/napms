import { useEffect, useState } from "react"
import { ArrowLeft, Pencil, Plus, Search } from "lucide-react"

import { ApiError } from "@/api"
import { Button } from "@/components/ui/Button"
import { AddDeploymentInteractionPanel } from "@/features/catalogues/AddDeploymentInteractionPanel"
import { CataloguePager } from "@/features/catalogues/CataloguePager"
import { DependencyBlockPanel } from "@/features/catalogues/DependencyBlockPanel"
import { DeploymentEditPanel } from "@/features/catalogues/TargetCatalogueEditPanels"
import {
  retireDeploymentInteraction,
  TargetCatalogueApiError,
  type DependencyGroupDto,
} from "@/features/catalogues/targetCatalogueCommands"
import { readDeploymentInteractionLifecycle } from "@/features/catalogues/targetDeploymentInteractionLifecycle"
import {
  listAvailableInteractions,
  listDeploymentConnectivity,
  readApplicationDeployment,
  type ApplicationDeploymentDto,
  type DeploymentConnectivityDto,
  type DeploymentInteractionSide,
} from "@/features/catalogues/targetCatalogueApi"
import { resourceCount, trafficSummary } from "@/features/catalogues/targetPresentation"

const inputClass =
  "min-h-10 min-w-0 rounded-md border border-[#CBD5E1] bg-white px-3 py-2 text-sm text-[#172033] outline-none focus:border-[#2563EB] focus:ring-2 focus:ring-[#DBEAFE]"

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError ? caught : new ApiError(500, "InternalError", fallback)
}

export function ApplicationDeploymentPage({
  deploymentId,
  onBack,
  onOpenResources,
}: {
  deploymentId: string
  onBack: () => void
  onOpenResources: (deploymentInteractionId: string, side: DeploymentInteractionSide) => void
}) {
  const [deployment, setDeployment] = useState<ApplicationDeploymentDto | null>(null)
  const [applicationName, setApplicationName] = useState<string | null>(null)
  const [selectedTotal, setSelectedTotal] = useState(0)
  const [definedTotal, setDefinedTotal] = useState(0)
  const [detailLoading, setDetailLoading] = useState(true)
  const [detailError, setDetailError] = useState<ApiError | null>(null)
  const [editOpen, setEditOpen] = useState(false)

  const [connectivity, setConnectivity] = useState<DeploymentConnectivityDto[]>([])
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(50)
  const [filteredTotal, setFilteredTotal] = useState(0)
  const [connectivityLoading, setConnectivityLoading] = useState(true)
  const [connectivityError, setConnectivityError] = useState<ApiError | null>(null)
  const [draftSearch, setDraftSearch] = useState("")
  const [draftProtocol, setDraftProtocol] = useState("")
  const [search, setSearch] = useState("")
  const [protocol, setProtocol] = useState("")
  const [addOpen, setAddOpen] = useState(false)
  const [reloadToken, setReloadToken] = useState(0)
  const [removingId, setRemovingId] = useState<string | null>(null)
  const [removeError, setRemoveError] = useState<string | null>(null)
  const [removeBlockers, setRemoveBlockers] = useState<DependencyGroupDto[] | null>(null)
  const [removeBlockerSubject, setRemoveBlockerSubject] = useState<string | null>(null)
  const [removing, setRemoving] = useState(false)

  useEffect(() => {
    let active = true
    setDetailLoading(true)
    setDetailError(null)
    void Promise.all([
      readApplicationDeployment(deploymentId),
      listDeploymentConnectivity({ applicationDeploymentId: deploymentId, page: 1, pageSize: 1 }),
      listAvailableInteractions({ applicationDeploymentId: deploymentId, page: 1, pageSize: 1 }),
    ])
      .then(([detail, selected, available]) => {
        if (!active) return
        setDeployment(detail.deployment)
        setApplicationName(detail.applicationName)
        setSelectedTotal(selected.total)
        setDefinedTotal(selected.total + available.total)
      })
      .catch((caught) => { if (active) setDetailError(errorFrom(caught, "Application Deployment could not be loaded.")) })
      .finally(() => { if (active) setDetailLoading(false) })
    return () => { active = false }
  }, [deploymentId, reloadToken])

  useEffect(() => {
    let active = true
    setConnectivityLoading(true)
    setConnectivityError(null)
    void listDeploymentConnectivity({ applicationDeploymentId: deploymentId, page, search, protocol })
      .then((result) => {
        if (!active) return
        setConnectivity(result.items)
        setFilteredTotal(result.total)
        setPageSize(result.pageSize)
      })
      .catch((caught) => { if (active) setConnectivityError(errorFrom(caught, "Connectivity could not be loaded.")) })
      .finally(() => { if (active) setConnectivityLoading(false) })
    return () => { active = false }
  }, [deploymentId, page, search, protocol, reloadToken])

  function refreshDeployment() {
    setPage(1)
    setRemovingId(null)
    setRemoveError(null)
    setRemoveBlockers(null)
    setRemoveBlockerSubject(null)
    setReloadToken((value) => value + 1)
  }

  async function removeInteraction(deploymentInteractionId: string) {
    setRemoving(true)
    setRemoveError(null)
    setRemoveBlockers(null)
    setRemoveBlockerSubject(null)
    try {
      const current = await readDeploymentInteractionLifecycle(deploymentInteractionId)
      if (current.lifecycleState === "Retired") {
        refreshDeployment()
        return
      }
      await retireDeploymentInteraction(deploymentInteractionId, current.version)
      refreshDeployment()
    } catch (caught) {
      if (caught instanceof TargetCatalogueApiError && caught.code === "CatalogueDependencyBlocked") {
        setRemoveBlockers(caught.details?.dependencies ?? [])
        setRemoveBlockerSubject(deploymentInteractionId)
      } else {
        setRemoveError(caught instanceof Error ? caught.message : "Interaction could not be removed from the deployment.")
      }
    } finally {
      setRemoving(false)
      setRemovingId(null)
    }
  }

  if (detailLoading) return <div className="mx-auto max-w-7xl"><section className="rounded-lg border border-[#E2E8F0] bg-white p-6 text-sm text-[#64748B]">Loading deployment…</section></div>
  if (detailError) return <div className="mx-auto max-w-7xl"><section className="rounded-lg border border-[#E2E8F0] bg-white p-6 text-sm text-red-700">{detailError.message}</section></div>
  if (!deployment) return null

  return (
    <div className="mx-auto grid max-w-7xl gap-5">
      <div><Button variant="ghost" className="-ml-3" onClick={onBack}><ArrowLeft className="size-4" aria-hidden="true" />Deployments</Button></div>

      <header className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div><div className="text-xs font-semibold uppercase tracking-[0.16em] text-[#64748B]">Applications / Deployments</div><h1 className="mt-1 text-2xl font-bold text-[#172033]">{applicationName ?? "Application"} — {deployment.companyReference} / {deployment.environment}</h1></div>
        <Button variant="secondary" onClick={() => setEditOpen((value) => !value)}><Pencil className="size-4" aria-hidden="true" />Edit</Button>
      </header>

      {editOpen ? <DeploymentEditPanel deployment={deployment} onChanged={(updated) => { setDeployment(updated); setEditOpen(false); refreshDeployment() }} onRetired={onBack} onCancel={() => setEditOpen(false)} /> : null}

      <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
        <dl className="grid gap-4 md:grid-cols-4"><div><dt className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">Application</dt><dd className="mt-1 text-sm font-medium text-[#172033]">{applicationName ?? "—"}</dd></div><div><dt className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">Company</dt><dd className="mt-1 text-sm text-[#172033]">{deployment.companyReference}</dd></div><div><dt className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">Environment</dt><dd className="mt-1 text-sm text-[#172033]">{deployment.environment}</dd></div><div><dt className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">Scope</dt><dd className="mt-1 text-sm text-[#172033]">{deployment.scopeReference}</dd></div></dl>
      </section>

      <section className="overflow-hidden rounded-lg border border-[#E2E8F0] bg-white shadow-sm">
        <div className="flex items-center justify-between gap-4 border-b border-[#E2E8F0] px-5 py-4"><div><h2 className="font-semibold text-[#172033]">Connectivity {selectedTotal} / {definedTotal}</h2><p className="mt-1 text-xs text-[#64748B]">Selected Interaction Definitions in this deployment.</p></div><Button onClick={() => setAddOpen((value) => !value)}><Plus className="size-4" aria-hidden="true" />Add interaction</Button></div>
        {addOpen ? <AddDeploymentInteractionPanel deploymentId={deploymentId} onCancel={() => setAddOpen(false)} onChanged={refreshDeployment} /> : null}

        <form className="grid gap-2 border-b border-[#E2E8F0] p-4 sm:grid-cols-[minmax(14rem,1fr)_10rem_auto]" onSubmit={(event) => { event.preventDefault(); setPage(1); setSearch(draftSearch.trim()); setProtocol(draftProtocol.trim()) }}><div className="relative min-w-0"><Search className="pointer-events-none absolute left-3 top-3 size-4 text-[#94A3B8]" aria-hidden="true" /><input className={`${inputClass} w-full pl-9`} value={draftSearch} onChange={(event) => setDraftSearch(event.target.value)} placeholder="Search connectivity" aria-label="Search connectivity" /></div><input className={inputClass} value={draftProtocol} onChange={(event) => setDraftProtocol(event.target.value)} placeholder="Protocol" aria-label="Protocol" /><Button type="submit" variant="secondary">Apply</Button></form>

        {removeError ? <div className="border-b border-red-200 bg-red-50 px-5 py-3 text-sm text-red-700">{removeError}</div> : null}
        {removeBlockers && removeBlockerSubject ? <DependencyBlockPanel groups={removeBlockers} subjectKind="deployment-interaction" subjectId={removeBlockerSubject} onClose={() => { setRemoveBlockers(null); setRemoveBlockerSubject(null) }} /> : null}

        {connectivityLoading ? <div className="p-6 text-sm text-[#64748B]">Loading connectivity…</div> : connectivityError ? <div className="p-6 text-sm text-red-700">{connectivityError.message}</div> : connectivity.length === 0 ? <div className="p-6 text-sm text-[#64748B]">No interactions match the current view.</div> : (
          <div className="overflow-x-auto"><table className="w-full min-w-[1120px] text-left text-sm"><thead className="bg-[#F8FAFC] text-xs font-semibold uppercase tracking-wide text-[#64748B]"><tr><th className="px-5 py-3">Source component</th><th className="px-5 py-3 text-right">Source resources</th><th className="px-5 py-3">Destination component</th><th className="px-5 py-3 text-right">Destination resources</th><th className="px-5 py-3">Traffic</th><th className="w-44 px-5 py-3" /></tr></thead><tbody className="divide-y divide-[#E2E8F0]">{connectivity.map((item) => <tr key={item.deploymentInteractionId}><td className="px-5 py-3 font-semibold text-[#172033]">{item.sourceComponent.displayName}</td><td className="px-5 py-3 text-right tabular-nums"><button type="button" className="font-semibold text-[#2563EB] hover:underline" onClick={() => onOpenResources(item.deploymentInteractionId, "Source")}>{resourceCount(item.sourceComponent.resourceCount)}</button></td><td className="px-5 py-3 font-semibold text-[#172033]">{item.destinationComponent.displayName}</td><td className="px-5 py-3 text-right tabular-nums"><button type="button" className="font-semibold text-[#2563EB] hover:underline" onClick={() => onOpenResources(item.deploymentInteractionId, "Destination")}>{resourceCount(item.destinationComponent.resourceCount)}</button></td><td className="px-5 py-3 text-[#475569]">{trafficSummary(item.trafficAlternatives)}</td><td className="px-5 py-3 text-right">{removingId === item.deploymentInteractionId ? <div className="flex justify-end gap-2"><Button variant="ghost" disabled={removing} onClick={() => setRemovingId(null)}>Cancel</Button><Button variant="secondary" loading={removing} onClick={() => void removeInteraction(item.deploymentInteractionId)}>Confirm remove</Button></div> : <Button variant="ghost" onClick={() => setRemovingId(item.deploymentInteractionId)}>Remove from deployment</Button>}</td></tr>)}</tbody></table></div>
        )}
        {!connectivityLoading && !connectivityError ? <CataloguePager page={page} pageSize={pageSize} total={filteredTotal} onPageChange={setPage} /> : null}
      </section>
    </div>
  )
}
