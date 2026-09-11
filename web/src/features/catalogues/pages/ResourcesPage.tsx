import { useEffect, useMemo, useState } from "react"
import {
  AlertTriangle,
  CheckCircle2,
  MoreHorizontal,
  Plus,
  Search,
  X,
} from "lucide-react"

import { ApiError } from "@/lib/api"
import { shortId } from "@/features/catalogues/components/CatalogueIdentity"
import { Button } from "@/components/ui/Button"
import { createCatalogueResource } from "@/features/catalogues/api/catalogue"
import {
  listCatalogueResourceWorkspace,
  type ResourceWorkspaceDataState,
  type ResourceWorkspaceItemDto,
} from "@/features/catalogues/api/resourceWorkspace"

const controlClass =
  "min-h-10 w-full rounded-md border border-[#CBD5E1] bg-white px-3 py-2 text-sm text-[#172033] outline-none transition focus:border-[#2563EB] focus:ring-2 focus:ring-[#DBEAFE]"

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError
    ? caught
    : new ApiError(500, "InternalError", fallback)
}

function DataState({ item }: { item: ResourceWorkspaceItemDto }) {
  let label = "Complete"
  let warning = false
  if (!item.currentFacts.hasRealization) {
    label = "No address"
    warning = true
  } else if (!item.currentFacts.hasScopeAffiliation) {
    label = "No scope"
    warning = true
  } else if (!item.currentFacts.hasResponsibility) {
    label = "No responsibility"
    warning = true
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 text-xs font-medium ${
        warning ? "text-amber-700" : "text-emerald-700"
      }`}
    >
      {warning ? (
        <AlertTriangle className="size-3.5" aria-hidden="true" />
      ) : (
        <CheckCircle2 className="size-3.5" aria-hidden="true" />
      )}
      {label}
    </span>
  )
}

function LifecycleBadge({ value }: { value: string }) {
  const active = value === "Active"
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-semibold ${
        active
          ? "bg-emerald-50 text-emerald-700"
          : "bg-slate-100 text-slate-600"
      }`}
    >
      <span className={`size-1.5 rounded-full ${active ? "bg-emerald-500" : "bg-slate-400"}`} />
      {value}
    </span>
  )
}

function ScopeChips({ values }: { values: string[] }) {
  if (values.length === 0) return <span className="text-[#94A3B8]">—</span>
  return (
    <div className="flex flex-wrap gap-1">
      {values.slice(0, 2).map((value) => (
        <span
          key={value}
          className="rounded bg-[#EFF6FF] px-2 py-0.5 text-xs font-medium text-[#1D4ED8]"
        >
          {value}
        </span>
      ))}
      {values.length > 2 ? (
        <span className="rounded bg-[#F1F5F9] px-2 py-0.5 text-xs text-[#64748B]">
          +{values.length - 2}
        </span>
      ) : null}
    </div>
  )
}

export function ResourcesPage({
  page,
  onPageChange,
  onOpenResource,
}: {
  page: number
  onPageChange: (page: number) => void
  onOpenResource: (resourceReference: string) => void
}) {
  const [items, setItems] = useState<ResourceWorkspaceItemDto[]>([])
  const [hasMore, setHasMore] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)

  const [searchInput, setSearchInput] = useState("")
  const [search, setSearch] = useState("")
  const [scopeInput, setScopeInput] = useState("")
  const [scopeFilter, setScopeFilter] = useState("")
  const [lifecycle, setLifecycle] = useState<"active" | "all">("active")
  const [dataState, setDataState] = useState<ResourceWorkspaceDataState>("")

  const [showCreate, setShowCreate] = useState(false)
  const [displayName, setDisplayName] = useState("")
  const [creating, setCreating] = useState(false)
  const [createError, setCreateError] = useState<ApiError | null>(null)

  const visibleScopes = useMemo(
    () => Array.from(new Set(items.flatMap((item) => item.currentScopes))).sort(),
    [items],
  )

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const result = await listCatalogueResourceWorkspace(
        page,
        search,
        scopeFilter,
        {
          includeRetired: lifecycle === "all",
          dataState,
        },
      )
      setItems(result.items)
      setHasMore(result.hasMore)
    } catch (caught) {
      setError(errorFrom(caught, "Resources could not be loaded."))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [page, search, scopeFilter, lifecycle, dataState])

  async function create(event: React.FormEvent) {
    event.preventDefault()
    setCreating(true)
    setCreateError(null)
    try {
      const created = await createCatalogueResource(displayName.trim() || null)
      setDisplayName("")
      setShowCreate(false)
      onOpenResource(created.resourceReference)
    } catch (caught) {
      setCreateError(errorFrom(caught, "Resource could not be created."))
    } finally {
      setCreating(false)
    }
  }

  function applySearch(event: React.FormEvent) {
    event.preventDefault()
    if (page !== 1) onPageChange(1)
    setSearch(searchInput.trim())
    setScopeFilter(scopeInput.trim())
  }

  function updateDataState(next: ResourceWorkspaceDataState) {
    if (page !== 1) onPageChange(1)
    setDataState(next)
  }

  function resetFilters() {
    setSearchInput("")
    setSearch("")
    setScopeInput("")
    setScopeFilter("")
    setLifecycle("active")
    setDataState("")
    if (page !== 1) onPageChange(1)
  }

  return (
    <div className="mx-auto grid max-w-[1480px] gap-5">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#172033]">Resource Catalogue</h1>
          <p className="mt-1 text-sm text-[#64748B]">
            Find and manage network-relevant resources.
          </p>
        </div>
        <Button onClick={() => setShowCreate(true)}>
          <Plus className="size-4" aria-hidden="true" />
          New resource
        </Button>
      </header>

      <section className="overflow-hidden rounded-lg border border-[#DCE3EC] bg-white shadow-sm">
        <form className="border-b border-[#E2E8F0] p-4" onSubmit={applySearch}>
          <div className="relative">
            <Search
              className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-[#94A3B8]"
              aria-hidden="true"
            />
            <input
              className={`${controlClass} pl-10`}
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder="Search by name, reference, address, scope or owner…"
              aria-label="Search resources"
            />
          </div>

          <div className="mt-3 grid gap-2 lg:grid-cols-[minmax(13rem,1fr)_11rem_13rem_auto_auto]">
            <div>
              <label className="mb-1 block text-[11px] font-semibold uppercase tracking-wide text-[#64748B]">
                Scope
              </label>
              <input
                className={controlClass}
                value={scopeInput}
                onChange={(event) => setScopeInput(event.target.value)}
                placeholder="All scopes"
                list="resource-scope-options"
              />
              <datalist id="resource-scope-options">
                {visibleScopes.map((scope) => (
                  <option key={scope} value={scope} />
                ))}
              </datalist>
            </div>
            <label className="grid gap-1 text-[11px] font-semibold uppercase tracking-wide text-[#64748B]">
              Lifecycle
              <select
                className={controlClass}
                value={lifecycle}
                onChange={(event) => {
                  if (page !== 1) onPageChange(1)
                  setLifecycle(event.target.value as "active" | "all")
                }}
              >
                <option value="active">Active</option>
                <option value="all">All</option>
              </select>
            </label>
            <label className="grid gap-1 text-[11px] font-semibold uppercase tracking-wide text-[#64748B]">
              Data state
              <select
                className={controlClass}
                value={dataState}
                onChange={(event) =>
                  updateDataState(event.target.value as ResourceWorkspaceDataState)
                }
              >
                <option value="">All</option>
                <option value="missing-address">Missing address</option>
                <option value="missing-scope">Missing scope</option>
                <option value="missing-responsibility">Missing responsibility</option>
              </select>
            </label>
            <Button type="submit" variant="secondary" className="self-end">
              Apply
            </Button>
            <Button
              type="button"
              variant="ghost"
              className="self-end"
              onClick={resetFilters}
            >
              Reset
            </Button>
          </div>
        </form>

        <div className="flex flex-wrap items-center gap-2 border-b border-[#E2E8F0] px-4 py-3">
          {[
            ["", "All"],
            ["missing-address", "No address"],
            ["missing-responsibility", "No responsibility"],
            ["missing-scope", "No scope"],
          ].map(([value, label]) => (
            <button
              key={value}
              type="button"
              onClick={() => updateDataState(value as ResourceWorkspaceDataState)}
              className={`rounded-full border px-3 py-1 text-xs font-semibold transition ${
                dataState === value
                  ? "border-[#93C5FD] bg-[#EFF6FF] text-[#1D4ED8]"
                  : "border-[#E2E8F0] bg-white text-[#64748B] hover:bg-[#F8FAFC]"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="p-8 text-sm text-[#64748B]">Loading resources…</div>
        ) : error ? (
          <div className="p-8">
            <p className="text-sm text-red-700">{error.message}</p>
            <Button className="mt-3" variant="secondary" onClick={() => void load()}>
              Retry
            </Button>
          </div>
        ) : items.length === 0 ? (
          <div className="p-10 text-center">
            <div className="text-sm font-semibold text-[#172033]">No resources found</div>
            <p className="mt-1 text-sm text-[#64748B]">
              Change the search or filters, or create a new resource.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[1050px] border-collapse text-left text-sm">
              <thead className="bg-[#F8FAFC] text-[11px] font-semibold uppercase tracking-wide text-[#64748B]">
                <tr className="border-b border-[#E2E8F0]">
                  <th className="px-4 py-3">Name</th>
                  <th className="px-4 py-3">Reference</th>
                  <th className="px-4 py-3">Addresses</th>
                  <th className="px-4 py-3">Scope(s)</th>
                  <th className="px-4 py-3">Technical owner</th>
                  <th className="px-4 py-3">Lifecycle</th>
                  <th className="px-4 py-3">Data state</th>
                  <th className="w-10 px-3 py-3" aria-label="Actions" />
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E2E8F0]">
                {items.map((item) => (
                  <tr
                    key={item.resourceReference}
                    className="cursor-pointer bg-white transition hover:bg-[#F8FAFC]"
                    onClick={() => onOpenResource(item.resourceReference)}
                  >
                    <td className="px-4 py-3.5 align-top">
                      <button
                        type="button"
                        className="font-semibold text-[#2563EB] hover:underline"
                        onClick={(event) => {
                          event.stopPropagation()
                          onOpenResource(item.resourceReference)
                        }}
                      >
                        {item.displayName || shortId(item.resourceReference)}
                      </button>
                    </td>
                    <td className="px-4 py-3.5 align-top font-mono text-xs text-[#64748B]">
                      {shortId(item.resourceReference)}
                    </td>
                    <td className="px-4 py-3.5 align-top">
                      {item.currentAddresses.length === 0 ? (
                        <span className="text-[#94A3B8]">—</span>
                      ) : (
                        <div className="grid gap-0.5 font-mono text-xs text-[#334155]">
                          {item.currentAddresses.slice(0, 2).map((address) => (
                            <span key={address}>{address}</span>
                          ))}
                          {item.currentAddresses.length > 2 ? (
                            <span className="text-[#64748B]">
                              +{item.currentAddresses.length - 2} more
                            </span>
                          ) : null}
                        </div>
                      )}
                    </td>
                    <td className="px-4 py-3.5 align-top">
                      <ScopeChips values={item.currentScopes} />
                    </td>
                    <td className="px-4 py-3.5 align-top text-[#334155]">
                      {item.technicalOwners.length > 0
                        ? item.technicalOwners.join(", ")
                        : <span className="text-[#94A3B8]">—</span>}
                    </td>
                    <td className="px-4 py-3.5 align-top">
                      <LifecycleBadge value={item.lifecycle} />
                    </td>
                    <td className="px-4 py-3.5 align-top">
                      <DataState item={item} />
                    </td>
                    <td className="px-3 py-3.5 align-top text-right">
                      <MoreHorizontal className="size-4 text-[#94A3B8]" aria-hidden="true" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="flex items-center justify-between border-t border-[#E2E8F0] px-4 py-3">
          <span className="text-xs text-[#64748B]">
            Page {page} · up to 50 resources per page
          </span>
          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              disabled={page <= 1 || loading}
              onClick={() => onPageChange(page - 1)}
            >
              Previous
            </Button>
            <span className="flex size-9 items-center justify-center rounded-md border border-[#93C5FD] bg-[#EFF6FF] text-sm font-semibold text-[#1D4ED8]">
              {page}
            </span>
            <Button
              variant="secondary"
              disabled={!hasMore || loading}
              onClick={() => onPageChange(page + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      </section>

      {showCreate ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/35 p-4"
          role="presentation"
          onMouseDown={(event) => {
            if (event.currentTarget === event.target && !creating) setShowCreate(false)
          }}
        >
          <div
            className="w-full max-w-lg rounded-xl border border-[#E2E8F0] bg-white shadow-2xl"
            role="dialog"
            aria-modal="true"
            aria-labelledby="create-resource-title"
          >
            <div className="flex items-start justify-between border-b border-[#E2E8F0] px-5 py-4">
              <div>
                <h2 id="create-resource-title" className="font-semibold text-[#172033]">
                  New resource
                </h2>
                <p className="mt-1 text-xs text-[#64748B]">
                  NAPMS generates the stable resource reference.
                </p>
              </div>
              <button
                type="button"
                className="rounded-md p-2 text-[#64748B] hover:bg-[#F1F5F9]"
                onClick={() => setShowCreate(false)}
                disabled={creating}
                aria-label="Close"
              >
                <X className="size-4" aria-hidden="true" />
              </button>
            </div>
            <form className="p-5" onSubmit={create}>
              <label className="grid gap-1.5 text-sm font-medium text-[#172033]">
                Display name
                <input
                  className={controlClass}
                  value={displayName}
                  onChange={(event) => setDisplayName(event.target.value)}
                  placeholder="api-gateway"
                  maxLength={256}
                  autoFocus
                />
              </label>
              {createError ? (
                <p className="mt-3 text-sm text-red-700">{createError.message}</p>
              ) : null}
              <div className="mt-5 flex justify-end gap-2">
                <Button
                  type="button"
                  variant="secondary"
                  disabled={creating}
                  onClick={() => setShowCreate(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" loading={creating}>Create resource</Button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </div>
  )
}
