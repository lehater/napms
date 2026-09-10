import { useEffect, useState } from "react"
import { ArrowLeft, Plus } from "lucide-react"

import { ApiError } from "@/api"
import { Button } from "@/components/ui/Button"
import { CataloguePager } from "@/features/catalogues/CataloguePager"
import {
  CreateComponentPanel,
  CreateDeploymentPanel,
} from "@/features/catalogues/TargetCatalogueForms"
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

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError
    ? caught
    : new ApiError(500, "InternalError", fallback)
}

function LoadingOrError({ loading, error }: { loading: boolean; error: ApiError | null }) {
  if (loading) return <div className="p-6 text-sm text-[#64748B]">Loading…</div>
  if (error) return <div className="p-6 text-sm text-red-700">{error.message}</div>
  return null
}

export function ApplicationDefinitionPage({
  applicationId,
  onBack,
  onOpenDeployment,
}: {
  applicationId: string
  onBack: () => void
  onOpenDeployment: (deploymentId: string) => void
}) {
  const [definition, setDefinition] = useState<ApplicationDefinitionDto | null>(null)
  const [tab, setTab] = useState<Tab>("overview")
  const [tabPage, setTabPage] = useState(1)
  const [tabPageSize, setTabPageSize] = useState(50)
  const [tabTotal, setTabTotal] = useState(0)
  const [components, setComponents] = useState<ApplicationComponentDto[]>([])
  const [interactions, setInteractions] = useState<InteractionDefinitionSummaryDto[]>([])
  const [deployments, setDeployments] = useState<ApplicationDeploymentSummaryDto[]>([])
  const [loading, setLoading] = useState(true)
  const [tabLoading, setTabLoading] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)
  const [tabError, setTabError] = useState<ApiError | null>(null)
  const [createOpen, setCreateOpen] = useState(false)
  const [reloadToken, setReloadToken] = useState(0)

  useEffect(() => {
    let active = true
    setLoading(true)
    setError(null)
    void readApplicationDefinition(applicationId)
      .then((result) => {
        if (active) setDefinition(result.definition)
      })
      .catch((caught) => {
        if (active) setError(errorFrom(caught, "Application Definition could not be loaded."))
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [applicationId])

  useEffect(() => {
    if (tab === "overview") return
    let active = true
    setTabLoading(true)
    setTabError(null)
    const acceptPage = (result: { total: number; pageSize: number }) => {
      if (!active) return
      setTabTotal(result.total)
      setTabPageSize(result.pageSize)
    }
    const pending =
      tab === "components"
        ? listApplicationComponents({ applicationId, page: tabPage }).then((result) => {
            if (active) setComponents(result.items)
            acceptPage(result)
          })
        : tab === "interactions"
          ? listInteractionDefinitions({ applicationId, page: tabPage }).then((result) => {
              if (active) setInteractions(result.items)
              acceptPage(result)
            })
          : listApplicationDeployments({
              applicationId,
              page: tabPage,
              sort: "company",
            }).then((result) => {
              if (active) setDeployments(result.items)
              acceptPage(result)
            })
    void pending
      .catch((caught) => {
        if (active) setTabError(errorFrom(caught, "Definition details could not be loaded."))
      })
      .finally(() => {
        if (active) setTabLoading(false)
      })
    return () => {
      active = false
    }
  }, [applicationId, tab, tabPage, reloadToken])

  function selectTab(next: Tab) {
    setTabPage(1)
    setTabTotal(0)
    setCreateOpen(false)
    setTab(next)
  }

  function refreshTab() {
    setCreateOpen(false)
    setTabPage(1)
    setReloadToken((value) => value + 1)
  }

  return (
    <div className="mx-auto grid max-w-7xl gap-5">
      <div>
        <Button variant="ghost" className="-ml-3" onClick={onBack}>
          <ArrowLeft className="size-4" aria-hidden="true" />
          Definitions
        </Button>
      </div>

      {loading || error ? (
        <section className="rounded-lg border border-[#E2E8F0] bg-white">
          <LoadingOrError loading={loading} error={error} />
        </section>
      ) : definition ? (
        <>
          <header>
            <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[#64748B]">
              Applications / Definitions
            </div>
            <h1 className="mt-1 text-2xl font-bold text-[#172033]">{definition.displayName}</h1>
            <p className="mt-2 text-sm text-[#64748B]">
              {definition.domain ?? "No domain"}
              {definition.ownerReference ? ` · Owner: ${definition.ownerReference}` : ""}
            </p>
          </header>

          <div className="flex gap-1 border-b border-[#E2E8F0]">
            {(["overview", "components", "interactions", "deployments"] as const).map((item) => (
              <button
                key={item}
                type="button"
                className={`border-b-2 px-4 py-3 text-sm font-semibold capitalize ${
                  tab === item
                    ? "border-[#2563EB] text-[#1D4ED8]"
                    : "border-transparent text-[#64748B] hover:text-[#172033]"
                }`}
                onClick={() => selectTab(item)}
              >
                {item}
              </button>
            ))}
          </div>

          <section className="overflow-hidden rounded-lg border border-[#E2E8F0] bg-white shadow-sm">
            {tab === "overview" ? (
              <dl className="grid gap-x-8 gap-y-5 p-6 md:grid-cols-2">
                <div><dt className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">Name</dt><dd className="mt-1 text-sm font-medium text-[#172033]">{definition.displayName}</dd></div>
                <div><dt className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">Domain</dt><dd className="mt-1 text-sm text-[#172033]">{definition.domain ?? "—"}</dd></div>
                <div><dt className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">Owner</dt><dd className="mt-1 text-sm text-[#172033]">{definition.ownerReference ?? "—"}</dd></div>
                <div><dt className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">Description</dt><dd className="mt-1 text-sm text-[#172033]">{definition.description ?? "—"}</dd></div>
              </dl>
            ) : tabLoading || tabError ? (
              <LoadingOrError loading={tabLoading} error={tabError} />
            ) : tab === "components" ? (
              <>
                <div className="flex items-center justify-between border-b border-[#E2E8F0] px-5 py-4">
                  <h2 className="font-semibold text-[#172033]">Components</h2>
                  <Button onClick={() => setCreateOpen((value) => !value)}><Plus className="size-4" aria-hidden="true" />Add component</Button>
                </div>
                {createOpen ? <CreateComponentPanel applicationId={applicationId} onCancel={() => setCreateOpen(false)} onCreated={refreshTab} /> : null}
                {components.length === 0 ? (
                  <div className="p-6 text-sm text-[#64748B]">No active components.</div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full min-w-[720px] text-left text-sm">
                      <thead className="bg-[#F8FAFC] text-xs font-semibold uppercase tracking-wide text-[#64748B]"><tr><th className="px-5 py-3">Name</th><th className="px-5 py-3">Type</th><th className="px-5 py-3">Description</th></tr></thead>
                      <tbody className="divide-y divide-[#E2E8F0]">{components.map((item) => (<tr key={item.componentId}><td className="px-5 py-3 font-semibold text-[#172033]">{item.displayName}</td><td className="px-5 py-3 text-[#475569]">{item.componentType ?? "—"}</td><td className="px-5 py-3 text-[#475569]">{item.description ?? "—"}</td></tr>))}</tbody>
                    </table>
                  </div>
                )}
                <CataloguePager page={tabPage} pageSize={tabPageSize} total={tabTotal} onPageChange={setTabPage} />
              </>
            ) : tab === "interactions" ? (
              <>
                <div className="border-b border-[#E2E8F0] px-5 py-4"><h2 className="font-semibold text-[#172033]">Interactions</h2></div>
                {interactions.length === 0 ? (
                  <div className="p-6 text-sm text-[#64748B]">No active interactions.</div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full min-w-[760px] text-left text-sm">
                      <thead className="bg-[#F8FAFC] text-xs font-semibold uppercase tracking-wide text-[#64748B]"><tr><th className="px-5 py-3">Source</th><th className="px-5 py-3">Destination</th><th className="px-5 py-3">Traffic</th><th className="px-5 py-3 text-right">Deployments</th></tr></thead>
                      <tbody className="divide-y divide-[#E2E8F0]">{interactions.map((item) => (<tr key={item.interactionDefinitionId}><td className="px-5 py-3 font-semibold text-[#172033]">{item.sourceComponentName}</td><td className="px-5 py-3 font-semibold text-[#172033]">{item.destinationComponentName}</td><td className="px-5 py-3 text-[#475569]">{trafficSummary(item.trafficAlternatives)}</td><td className="px-5 py-3 text-right tabular-nums">{item.activeDeploymentCount}</td></tr>))}</tbody>
                    </table>
                  </div>
                )}
                <CataloguePager page={tabPage} pageSize={tabPageSize} total={tabTotal} onPageChange={setTabPage} />
              </>
            ) : (
              <>
                <div className="flex items-center justify-between border-b border-[#E2E8F0] px-5 py-4">
                  <h2 className="font-semibold text-[#172033]">Deployments</h2>
                  <Button onClick={() => setCreateOpen((value) => !value)}><Plus className="size-4" aria-hidden="true" />Add deployment</Button>
                </div>
                {createOpen ? <CreateDeploymentPanel applicationId={applicationId} onCancel={() => setCreateOpen(false)} onCreated={refreshTab} /> : null}
                {deployments.length === 0 ? (
                  <div className="p-6 text-sm text-[#64748B]">No active deployments.</div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full min-w-[760px] text-left text-sm">
                      <thead className="bg-[#F8FAFC] text-xs font-semibold uppercase tracking-wide text-[#64748B]"><tr><th className="px-5 py-3">Company</th><th className="px-5 py-3">Environment</th><th className="px-5 py-3">Scope</th><th className="px-5 py-3 text-right">Interactions</th></tr></thead>
                      <tbody className="divide-y divide-[#E2E8F0]">{deployments.map((item) => (<tr key={item.applicationDeploymentId} className="cursor-pointer hover:bg-[#F8FAFC]" onClick={() => onOpenDeployment(item.applicationDeploymentId)}><td className="px-5 py-3 font-semibold text-[#172033]">{item.companyReference}</td><td className="px-5 py-3 text-[#475569]">{item.environment}</td><td className="px-5 py-3 text-[#475569]">{item.scopeReference}</td><td className="px-5 py-3 text-right tabular-nums">{item.selectedInteractionCount} / {item.definedInteractionCount}</td></tr>))}</tbody>
                    </table>
                  </div>
                )}
                <CataloguePager page={tabPage} pageSize={tabPageSize} total={tabTotal} onPageChange={setTabPage} />
              </>
            )}
          </section>
        </>
      ) : null}
    </div>
  )
}
