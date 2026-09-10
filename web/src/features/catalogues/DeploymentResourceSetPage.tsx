import { useEffect, useState } from "react"
import { ArrowLeft, Search } from "lucide-react"

import { ApiError } from "@/api"
import { Button } from "@/components/ui/Button"
import { CataloguePager } from "@/features/catalogues/CataloguePager"
import {
  listDeploymentInteractionResources,
  type DeploymentInteractionSide,
  type ResourceSetMemberDto,
} from "@/features/catalogues/targetCatalogueApi"

const inputClass =
  "min-h-10 min-w-0 rounded-md border border-[#CBD5E1] bg-white px-3 py-2 text-sm text-[#172033] outline-none focus:border-[#2563EB] focus:ring-2 focus:ring-[#DBEAFE]"

function errorFrom(caught: unknown) {
  return caught instanceof ApiError
    ? caught
    : new ApiError(500, "InternalError", "Resource set could not be loaded.")
}

function scopesSummary(scopes: string[]) {
  if (scopes.length === 0) return "—"
  if (scopes.length <= 2) return scopes.join(", ")
  return `${scopes.slice(0, 2).join(", ")} +${scopes.length - 2}`
}

export function DeploymentResourceSetPage({
  deploymentInteractionId,
  side,
  onBack,
}: {
  deploymentInteractionId: string
  side: DeploymentInteractionSide
  onBack: () => void
}) {
  const [items, setItems] = useState<ResourceSetMemberDto[]>([])
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(50)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)
  const [draftSearch, setDraftSearch] = useState("")
  const [draftScope, setDraftScope] = useState("")
  const [search, setSearch] = useState("")
  const [scope, setScope] = useState("")

  useEffect(() => {
    let active = true
    setLoading(true)
    setError(null)
    void listDeploymentInteractionResources({
      deploymentInteractionId,
      side,
      page,
      search,
      scopeReference: scope,
    })
      .then((result) => {
        if (!active) return
        setItems(result.items)
        setTotal(result.total)
        setPageSize(result.pageSize)
      })
      .catch((caught) => {
        if (active) setError(errorFrom(caught))
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [deploymentInteractionId, side, page, search, scope])

  return (
    <div className="mx-auto grid max-w-6xl gap-5">
      <div>
        <Button variant="ghost" className="-ml-3" onClick={onBack}>
          <ArrowLeft className="size-4" aria-hidden="true" />
          Deployment
        </Button>
      </div>

      <header>
        <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[#64748B]">
          Application Deployment
        </div>
        <h1 className="mt-1 text-2xl font-bold text-[#172033]">{side} resources</h1>
        <p className="mt-2 text-sm text-[#64748B]">{total} effective resources</p>
      </header>

      <section className="overflow-hidden rounded-lg border border-[#E2E8F0] bg-white shadow-sm">
        <form
          className="grid gap-2 border-b border-[#E2E8F0] p-4 md:grid-cols-[minmax(16rem,1fr)_minmax(10rem,16rem)_auto]"
          onSubmit={(event) => {
            event.preventDefault()
            setPage(1)
            setSearch(draftSearch.trim())
            setScope(draftScope.trim())
          }}
        >
          <div className="relative min-w-0">
            <Search className="pointer-events-none absolute left-3 top-3 size-4 text-[#94A3B8]" aria-hidden="true" />
            <input
              className={`${inputClass} w-full pl-9`}
              value={draftSearch}
              onChange={(event) => setDraftSearch(event.target.value)}
              placeholder="Search resources"
              aria-label="Search resources"
            />
          </div>
          <input
            className={inputClass}
            value={draftScope}
            onChange={(event) => setDraftScope(event.target.value)}
            placeholder="Scope"
            aria-label="Scope"
          />
          <Button type="submit" variant="secondary">Apply</Button>
        </form>

        {loading ? (
          <div className="p-6 text-sm text-[#64748B]">Loading resources…</div>
        ) : error ? (
          <div className="p-6 text-sm text-red-700">{error.message}</div>
        ) : items.length === 0 ? (
          <div className="p-6 text-sm text-[#64748B]">No resources match the current view.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-left text-sm">
              <thead className="bg-[#F8FAFC] text-xs font-semibold uppercase tracking-wide text-[#64748B]">
                <tr><th className="px-5 py-3">Resource</th><th className="px-5 py-3">Scope</th></tr>
              </thead>
              <tbody className="divide-y divide-[#E2E8F0]">
                {items.map((item) => (
                  <tr key={item.bindingReference}>
                    <td className="px-5 py-3">
                      <div className="font-semibold text-[#172033]">{item.displayName ?? item.resourceReference}</div>
                      {item.displayName ? <div className="mt-0.5 text-xs text-[#94A3B8]">{item.resourceReference}</div> : null}
                    </td>
                    <td className="px-5 py-3 text-[#475569]">{scopesSummary(item.scopeReferences)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!loading && !error ? (
          <CataloguePager page={page} pageSize={pageSize} total={total} onPageChange={setPage} />
        ) : null}
      </section>
    </div>
  )
}
