import { useEffect, useState } from "react"
import { ChevronRight, Plus, Search } from "lucide-react"

import { ApiError } from "@/lib/api"
import { Button } from "@/components/ui/Button"
import { CataloguePager } from "@/features/catalogues/CataloguePager"
import { CreateDefinitionPanel } from "@/features/catalogues/TargetCatalogueForms"
import {
  listApplicationDefinitions,
  listApplicationDeployments,
  type ApplicationDefinitionSummaryDto,
  type ApplicationDeploymentSummaryDto,
} from "@/features/catalogues/targetCatalogueApi"

export type ApplicationCatalogueView = "definitions" | "deployments"

type Filters = {
  search: string
  first: string
  second: string
  third: string
}

const EMPTY_FILTERS: Filters = { search: "", first: "", second: "", third: "" }
const inputClass =
  "min-h-10 min-w-0 rounded-md border border-[#CBD5E1] bg-white px-3 py-2 text-sm text-[#172033] outline-none focus:border-[#2563EB] focus:ring-2 focus:ring-[#DBEAFE]"

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError
    ? caught
    : new ApiError(500, "InternalError", fallback)
}

export function ApplicationCataloguePage({
  view,
  page,
  onViewChange,
  onPageChange,
  onOpenDefinition,
  onOpenDeployment,
}: {
  view: ApplicationCatalogueView
  page: number
  onViewChange: (view: ApplicationCatalogueView) => void
  onPageChange: (page: number) => void
  onOpenDefinition: (applicationId: string) => void
  onOpenDeployment: (deploymentId: string) => void
}) {
  const [definitions, setDefinitions] = useState<ApplicationDefinitionSummaryDto[]>([])
  const [deployments, setDeployments] = useState<ApplicationDeploymentSummaryDto[]>([])
  const [total, setTotal] = useState(0)
  const [pageSize, setPageSize] = useState(50)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)
  const [draft, setDraft] = useState<Filters>(EMPTY_FILTERS)
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS)
  const [showCreate, setShowCreate] = useState(false)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      if (view === "definitions") {
        const result = await listApplicationDefinitions({
          page,
          search: filters.search,
          domain: filters.first,
          ownerReference: filters.second,
          sort: "name",
        })
        setDefinitions(result.items)
        setDeployments([])
        setTotal(result.total)
        setPageSize(result.pageSize)
      } else {
        const result = await listApplicationDeployments({
          page,
          search: filters.search,
          companyReference: filters.first,
          environment: filters.second,
          scopeReference: filters.third,
          sort: "application",
        })
        setDefinitions([])
        setDeployments(result.items)
        setTotal(result.total)
        setPageSize(result.pageSize)
      }
    } catch (caught) {
      setError(errorFrom(caught, "Application Catalogue could not be loaded."))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [view, page, filters])

  function switchView(next: ApplicationCatalogueView) {
    setDraft(EMPTY_FILTERS)
    setFilters(EMPTY_FILTERS)
    setShowCreate(false)
    onViewChange(next)
  }

  function changeDraft(field: keyof Filters, value: string) {
    setDraft((current) => ({ ...current, [field]: value }))
  }

  return (
    <div className="mx-auto grid max-w-7xl gap-5">
      <header className="flex items-end justify-between gap-4">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[#64748B]">
            Catalogues
          </div>
          <h1 className="mt-1 text-2xl font-bold text-[#172033]">Applications</h1>
        </div>
        {view === "definitions" ? (
          <Button onClick={() => setShowCreate((value) => !value)}>
            <Plus className="size-4" aria-hidden="true" />
            Add application
          </Button>
        ) : null}
      </header>

      <div className="flex gap-1 border-b border-[#E2E8F0]">
        {(["definitions", "deployments"] as const).map((item) => (
          <button
            key={item}
            type="button"
            className={`border-b-2 px-4 py-3 text-sm font-semibold ${
              view === item
                ? "border-[#2563EB] text-[#1D4ED8]"
                : "border-transparent text-[#64748B] hover:text-[#172033]"
            }`}
            onClick={() => switchView(item)}
          >
            {item === "definitions" ? "Definitions" : "Deployments"}
          </button>
        ))}
      </div>

      {showCreate && view === "definitions" ? (
        <CreateDefinitionPanel
          onCancel={() => setShowCreate(false)}
          onCreated={(definition) => {
            setShowCreate(false)
            onOpenDefinition(definition.applicationId)
          }}
        />
      ) : null}

      <section className="overflow-hidden rounded-lg border border-[#E2E8F0] bg-white shadow-sm">
        <form
          className="grid gap-2 border-b border-[#E2E8F0] p-4 lg:grid-cols-[minmax(16rem,1fr)_repeat(3,minmax(8rem,12rem))_auto]"
          onSubmit={(event) => {
            event.preventDefault()
            if (page !== 1) onPageChange(1)
            setFilters({
              search: draft.search.trim(),
              first: draft.first.trim(),
              second: draft.second.trim(),
              third: draft.third.trim(),
            })
          }}
        >
          <div className="relative min-w-0">
            <Search
              className="pointer-events-none absolute left-3 top-3 size-4 text-[#94A3B8]"
              aria-hidden="true"
            />
            <input
              className={`${inputClass} w-full pl-9`}
              value={draft.search}
              onChange={(event) => changeDraft("search", event.target.value)}
              placeholder={view === "definitions" ? "Search definitions" : "Search deployments"}
              aria-label="Search"
            />
          </div>
          {view === "definitions" ? (
            <>
              <input className={inputClass} value={draft.first} onChange={(event) => changeDraft("first", event.target.value)} placeholder="Domain" aria-label="Domain" />
              <input className={inputClass} value={draft.second} onChange={(event) => changeDraft("second", event.target.value)} placeholder="Owner" aria-label="Owner" />
              <div className="hidden lg:block" />
            </>
          ) : (
            <>
              <input className={inputClass} value={draft.first} onChange={(event) => changeDraft("first", event.target.value)} placeholder="Company" aria-label="Company" />
              <input className={inputClass} value={draft.second} onChange={(event) => changeDraft("second", event.target.value)} placeholder="Environment" aria-label="Environment" />
              <input className={inputClass} value={draft.third} onChange={(event) => changeDraft("third", event.target.value)} placeholder="Scope" aria-label="Scope" />
            </>
          )}
          <Button type="submit" variant="secondary">Apply</Button>
        </form>

        {loading ? (
          <div className="p-6 text-sm text-[#64748B]">Loading…</div>
        ) : error ? (
          <div className="p-6">
            <p className="text-sm text-red-700">{error.message}</p>
            <Button className="mt-3" variant="secondary" onClick={() => void load()}>Retry</Button>
          </div>
        ) : view === "definitions" ? (
          definitions.length === 0 ? (
            <div className="p-6 text-sm text-[#64748B]">No definitions match the current view.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[760px] text-left text-sm">
                <thead className="bg-[#F8FAFC] text-xs font-semibold uppercase tracking-wide text-[#64748B]">
                  <tr><th className="px-5 py-3">Name</th><th className="px-5 py-3">Domain</th><th className="px-5 py-3 text-right">Components</th><th className="px-5 py-3 text-right">Interactions</th><th className="px-5 py-3 text-right">Deployments</th><th className="w-10 px-3 py-3" /></tr>
                </thead>
                <tbody className="divide-y divide-[#E2E8F0]">
                  {definitions.map((item) => (
                    <tr key={item.applicationId} className="cursor-pointer hover:bg-[#F8FAFC]" onClick={() => onOpenDefinition(item.applicationId)}>
                      <td className="px-5 py-3 font-semibold text-[#172033]">{item.displayName}</td>
                      <td className="px-5 py-3 text-[#475569]">{item.domain ?? "—"}</td>
                      <td className="px-5 py-3 text-right tabular-nums">{item.componentCount}</td>
                      <td className="px-5 py-3 text-right tabular-nums">{item.interactionCount}</td>
                      <td className="px-5 py-3 text-right tabular-nums">{item.deploymentCount}</td>
                      <td className="px-3 py-3"><ChevronRight className="size-4 text-[#94A3B8]" /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        ) : deployments.length === 0 ? (
          <div className="p-6 text-sm text-[#64748B]">No deployments match the current view.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[920px] text-left text-sm">
              <thead className="bg-[#F8FAFC] text-xs font-semibold uppercase tracking-wide text-[#64748B]">
                <tr><th className="px-5 py-3">Application</th><th className="px-5 py-3">Company</th><th className="px-5 py-3">Environment</th><th className="px-5 py-3">Scope</th><th className="px-5 py-3 text-right">Interactions</th><th className="w-10 px-3 py-3" /></tr>
              </thead>
              <tbody className="divide-y divide-[#E2E8F0]">
                {deployments.map((item) => (
                  <tr key={item.applicationDeploymentId} className="cursor-pointer hover:bg-[#F8FAFC]" onClick={() => onOpenDeployment(item.applicationDeploymentId)}>
                    <td className="px-5 py-3 font-semibold text-[#172033]">{item.applicationName}</td>
                    <td className="px-5 py-3 text-[#475569]">{item.companyReference}</td>
                    <td className="px-5 py-3 text-[#475569]">{item.environment}</td>
                    <td className="px-5 py-3 text-[#475569]">{item.scopeReference}</td>
                    <td className="px-5 py-3 text-right tabular-nums">{item.selectedInteractionCount} / {item.definedInteractionCount}</td>
                    <td className="px-3 py-3"><ChevronRight className="size-4 text-[#94A3B8]" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!loading && !error ? (
          <CataloguePager page={page} pageSize={pageSize} total={total} loading={loading} onPageChange={onPageChange} />
        ) : null}
      </section>
    </div>
  )
}
