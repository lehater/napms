import { useEffect, useMemo, useState } from "react"
import {
  AlertTriangle,
  CheckCircle2,
  Plus,
  Search,
  X,
} from "lucide-react"

import { Button } from "@/components/ui/Button"
import { Input, Select } from "@/components/ui/Field"
import { FilterChip } from "@/design-system/components/FilterChip"
import {
  CataloguePage,
  CataloguePagination,
  CatalogueQuickFilters,
  CatalogueSurface,
} from "@/design-system/patterns/catalogue/CataloguePage"
import { createCatalogueResource } from "@/features/catalogues/api/catalogue"
import {
  listCatalogueResourceWorkspace,
  type ResourceWorkspaceDataState,
  type ResourceWorkspaceItemDto,
} from "@/features/catalogues/api/resourceWorkspace"
import { shortId } from "@/features/catalogues/components/CatalogueIdentity"
import { ApiError } from "@/lib/api"

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError
    ? caught
    : new ApiError(500, "InternalError", fallback)
}

function DataState({ item }: { item: ResourceWorkspaceItemDto }) {
  const missing: string[] = []
  if (!item.currentFacts.hasRealization) missing.push("No address")
  if (!item.currentFacts.hasScopeAffiliation) missing.push("No scope")
  if (!item.currentFacts.hasResponsibility) missing.push("No responsibility")

  if (missing.length === 0) {
    return (
      <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-[var(--napms-color-success)]">
        <CheckCircle2 className="size-3.5" aria-hidden="true" />
        No missing facts
      </span>
    )
  }

  return (
    <div className="grid gap-1">
      {missing.map((label) => (
        <span
          key={label}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-[var(--napms-color-warning)]"
        >
          <AlertTriangle className="size-3.5" aria-hidden="true" />
          {label}
        </span>
      ))}
    </div>
  )
}

function LifecycleBadge({ value }: { value: string }) {
  const active = value === "Active"
  return (
    <span
      className={`inline-flex h-[25px] items-center gap-1.5 rounded-full px-2.5 text-xs font-semibold ${
        active
          ? "bg-[var(--napms-color-success-bg)] text-[var(--napms-color-success)]"
          : "bg-[var(--napms-color-surface-muted)] text-[var(--napms-color-text-secondary)]"
      }`}
    >
      <span
        className={`size-1.5 rounded-full ${
          active
            ? "bg-[var(--napms-color-success-dot)]"
            : "bg-[var(--napms-color-text-muted)]"
        }`}
      />
      {value}
    </span>
  )
}

function ScopeChips({ values }: { values: string[] }) {
  if (values.length === 0) {
    return <span className="text-[var(--napms-color-text-muted)]">—</span>
  }

  return (
    <div className="flex flex-wrap gap-1">
      {values.slice(0, 2).map((value) => (
        <span
          key={value}
          className="inline-flex h-6 items-center rounded bg-[var(--napms-color-primary-subtle)] px-2 text-xs font-semibold text-[var(--napms-color-primary-hover)]"
        >
          {value}
        </span>
      ))}
      {values.length > 2 ? (
        <span className="inline-flex h-6 items-center rounded bg-[var(--napms-color-surface-muted)] px-2 text-xs text-[var(--napms-color-text-secondary)]">
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
    <CataloguePage
      title="Resource Catalogue"
      description="Find and manage network-relevant resources."
      actions={
        <Button onClick={() => setShowCreate(true)}>
          <Plus className="size-4" aria-hidden="true" />
          New resource
        </Button>
      }
    >
      <CatalogueSurface>
        <form
          className="border-b border-[var(--napms-color-border)] p-5"
          onSubmit={applySearch}
        >
          <div className="relative">
            <Search
              className="pointer-events-none absolute left-4 top-1/2 size-4 -translate-y-1/2 text-[var(--napms-color-text-muted)]"
              aria-hidden="true"
            />
            <Input
              className="pl-11"
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder="Search by name, reference, address, scope or owner…"
              aria-label="Search resources"
            />
          </div>

          <div className="mt-5 grid gap-3 xl:grid-cols-[290px_155px_230px_84px_auto] xl:gap-5">
            <label className="grid gap-2 text-[11px] font-bold uppercase tracking-[0.07em] text-[var(--napms-color-text-secondary)]">
              Scope
              <Input
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
            </label>

            <label className="grid gap-2 text-[11px] font-bold uppercase tracking-[0.07em] text-[var(--napms-color-text-secondary)]">
              Lifecycle
              <Select
                value={lifecycle}
                onChange={(event) => {
                  if (page !== 1) onPageChange(1)
                  setLifecycle(event.target.value as "active" | "all")
                }}
              >
                <option value="active">Active</option>
                <option value="all">All</option>
              </Select>
            </label>

            <label className="grid gap-2 text-[11px] font-bold uppercase tracking-[0.07em] text-[var(--napms-color-text-secondary)]">
              Data state
              <Select
                value={dataState}
                onChange={(event) =>
                  updateDataState(event.target.value as ResourceWorkspaceDataState)
                }
              >
                <option value="">All</option>
                <option value="missing-address">Missing address</option>
                <option value="missing-scope">Missing scope</option>
                <option value="missing-responsibility">Missing responsibility</option>
              </Select>
            </label>

            <Button type="submit" variant="secondary" className="self-end px-4">
              Apply
            </Button>
            <Button
              type="button"
              variant="ghost"
              className="self-end justify-start px-1 xl:justify-center"
              onClick={resetFilters}
            >
              Reset
            </Button>
          </div>
        </form>

        <CatalogueQuickFilters>
          {[
            ["", "All"],
            ["missing-address", "No address"],
            ["missing-responsibility", "No responsibility"],
            ["missing-scope", "No scope"],
          ].map(([value, label]) => (
            <FilterChip
              key={value}
              selected={dataState === value}
              onClick={() => updateDataState(value as ResourceWorkspaceDataState)}
            >
              {label}
            </FilterChip>
          ))}
        </CatalogueQuickFilters>

        {loading ? (
          <div className="flex min-h-[456px] items-start p-8 text-sm text-[var(--napms-color-text-secondary)]">
            Loading resources…
          </div>
        ) : error ? (
          <div className="min-h-[456px] p-8">
            <p className="text-sm text-[var(--napms-color-danger)]">{error.message}</p>
            <Button className="mt-3" variant="secondary" onClick={() => void load()}>
              Retry
            </Button>
          </div>
        ) : items.length === 0 ? (
          <div className="flex min-h-[456px] flex-col items-center justify-center p-10 text-center">
            <div className="text-sm font-semibold text-[var(--napms-color-text-primary)]">
              No resources found
            </div>
            <p className="mt-1 text-sm text-[var(--napms-color-text-secondary)]">
              Change the search or filters, or create a new resource.
            </p>
          </div>
        ) : (
          <div className="min-h-[456px] overflow-x-auto">
            <table className="w-full min-w-[1148px] table-fixed border-collapse text-left text-sm">
              <colgroup>
                <col style={{ width: "15.7%" }} />
                <col style={{ width: "12.2%" }} />
                <col style={{ width: "16%" }} />
                <col style={{ width: "14.5%" }} />
                <col style={{ width: "16.7%" }} />
                <col style={{ width: "9.7%" }} />
                <col style={{ width: "15.2%" }} />
              </colgroup>
              <thead className="bg-[var(--napms-color-surface-subtle)] text-[11px] font-bold uppercase tracking-[0.07em] text-[var(--napms-color-text-secondary)]">
                <tr className="h-11 border-b border-[var(--napms-color-border)]">
                  <th className="px-5">Name</th>
                  <th className="px-5">Reference</th>
                  <th className="px-5">Addresses</th>
                  <th className="px-5">Scope(s)</th>
                  <th className="px-5">Technical owner</th>
                  <th className="px-5">Lifecycle</th>
                  <th className="px-5">Data state</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--napms-color-border)]">
                {items.map((item) => (
                  <tr
                    key={item.resourceReference}
                    className="h-[62px] cursor-pointer bg-[var(--napms-color-surface)] transition hover:bg-[var(--napms-color-surface-subtle)]"
                    onClick={() => onOpenResource(item.resourceReference)}
                  >
                    <td className="px-5 py-3 align-middle">
                      <button
                        type="button"
                        className="font-semibold text-[var(--napms-color-primary)] hover:underline"
                        onClick={(event) => {
                          event.stopPropagation()
                          onOpenResource(item.resourceReference)
                        }}
                      >
                        {item.displayName || shortId(item.resourceReference)}
                      </button>
                    </td>
                    <td className="px-5 py-3 align-middle font-mono text-xs text-[var(--napms-color-text-secondary)]">
                      {shortId(item.resourceReference)}
                    </td>
                    <td className="px-5 py-3 align-middle">
                      {item.currentAddresses.length === 0 ? (
                        <span className="text-[var(--napms-color-text-muted)]">—</span>
                      ) : (
                        <div className="grid gap-0.5 font-mono text-xs text-[var(--napms-color-text-body)]">
                          {item.currentAddresses.slice(0, 2).map((address) => (
                            <span key={address}>{address}</span>
                          ))}
                          {item.currentAddresses.length > 2 ? (
                            <span className="text-[var(--napms-color-text-secondary)]">
                              +{item.currentAddresses.length - 2} more
                            </span>
                          ) : null}
                        </div>
                      )}
                    </td>
                    <td className="px-5 py-3 align-middle">
                      <ScopeChips values={item.currentScopes} />
                    </td>
                    <td className="px-5 py-3 align-middle text-[var(--napms-color-text-body)]">
                      {item.technicalOwners.length > 0 ? (
                        item.technicalOwners.join(", ")
                      ) : (
                        <span className="text-[var(--napms-color-text-muted)]">—</span>
                      )}
                    </td>
                    <td className="px-5 py-3 align-middle">
                      <LifecycleBadge value={item.lifecycle} />
                    </td>
                    <td className="px-5 py-3 align-middle">
                      <DataState item={item} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <CataloguePagination>
          <span className="text-xs text-[var(--napms-color-text-secondary)]">
            Page {page} · up to 50 resources per page
          </span>
          <div className="flex items-center gap-2.5">
            <Button
              variant="secondary"
              size="sm"
              disabled={page <= 1 || loading}
              onClick={() => onPageChange(page - 1)}
            >
              Previous
            </Button>
            <span className="flex size-[34px] items-center justify-center rounded-[var(--napms-control-radius)] border border-[var(--napms-color-primary-border)] bg-[var(--napms-color-primary-subtle)] text-xs font-semibold text-[var(--napms-color-primary-hover)]">
              {page}
            </span>
            <Button
              variant="secondary"
              size="sm"
              disabled={!hasMore || loading}
              onClick={() => onPageChange(page + 1)}
            >
              Next
            </Button>
          </div>
        </CataloguePagination>
      </CatalogueSurface>

      {showCreate ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/30 p-4"
          role="presentation"
          onMouseDown={(event) => {
            if (event.currentTarget === event.target && !creating) setShowCreate(false)
          }}
        >
          <div
            className="w-full max-w-[500px] overflow-hidden rounded-xl border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)] shadow-2xl"
            role="dialog"
            aria-modal="true"
            aria-labelledby="create-resource-title"
          >
            <div className="flex min-h-[89px] items-start justify-between border-b border-[var(--napms-color-border)] px-7 py-6">
              <div>
                <h2
                  id="create-resource-title"
                  className="text-lg font-bold text-[var(--napms-color-text-primary)]"
                >
                  New resource
                </h2>
                <p className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">
                  NAPMS generates the stable resource reference.
                </p>
              </div>
              <button
                type="button"
                className="rounded-[var(--napms-control-radius)] p-1.5 text-[var(--napms-color-text-secondary)] hover:bg-[var(--napms-color-surface-muted)]"
                onClick={() => setShowCreate(false)}
                disabled={creating}
                aria-label="Close"
              >
                <X className="size-4" aria-hidden="true" />
              </button>
            </div>
            <form onSubmit={create}>
              <div className="px-7 py-8">
                <label className="grid gap-3 text-sm font-semibold text-[var(--napms-color-text-primary)]">
                  Display name
                  <Input
                    value={displayName}
                    onChange={(event) => setDisplayName(event.target.value)}
                    placeholder="api-gateway"
                    maxLength={256}
                    autoFocus
                  />
                </label>
                <p className="mt-6 text-xs leading-5 text-[var(--napms-color-text-secondary)]">
                  Resource identity can exist before realization, scope affiliation or responsibility facts are added.
                </p>
                {createError ? (
                  <p className="mt-3 text-sm text-[var(--napms-color-danger)]">
                    {createError.message}
                  </p>
                ) : null}
              </div>
              <div className="flex min-h-[74px] justify-end gap-3 border-t border-[var(--napms-color-border)] px-7 py-[18px]">
                <Button
                  type="button"
                  variant="secondary"
                  disabled={creating}
                  onClick={() => setShowCreate(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" loading={creating}>
                  Create resource
                </Button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </CataloguePage>
  )
}
