import { useEffect, useMemo, useState } from "react"
import { Plus, X } from "lucide-react"

import { Button } from "@/components/ui/Button"
import { Input, Select } from "@/components/ui/Field"
import { Checkbox } from "@/design-system/components/Checkbox"
import {
  DataTable,
  DataTableBody,
  DataTableCell,
  DataTableHeadCell,
  DataTableHeader,
  DataTableHeaderRow,
  DataTableRow,
  DataTableSelectionCell,
  DataTableSelectionHead,
} from "@/design-system/components/DataTable"
import { FilterChip } from "@/design-system/components/FilterChip"
import { IssueIndicator } from "@/design-system/components/IssueIndicator"
import { EmptyState, ErrorState, LoadingState } from "@/design-system/components/PageState"
import { SearchInput } from "@/design-system/components/SearchInput"
import { StatusPill } from "@/design-system/components/StatusPill"
import { TagList } from "@/design-system/components/Tag"
import {
  CatalogueFilterBar,
  CatalogueFilterField,
  CataloguePage,
  CataloguePagination,
  CatalogueSurface,
  CatalogueToolbar,
  CatalogueViewBar,
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
    return <IssueIndicator tone="success">No missing facts</IssueIndicator>
  }

  return (
    <div className="grid gap-1">
      {missing.map((label) => (
        <IssueIndicator key={label}>{label}</IssueIndicator>
      ))}
    </div>
  )
}

function LifecycleBadge({ value }: { value: string }) {
  return (
    <StatusPill tone={value === "Active" ? "positive" : "neutral"}>
      {value}
    </StatusPill>
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
  const [selected, setSelected] = useState<Set<string>>(new Set())

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

  const visibleReferences = useMemo(
    () => items.map((item) => item.resourceReference),
    [items],
  )
  const allVisibleSelected =
    visibleReferences.length > 0 && visibleReferences.every((reference) => selected.has(reference))
  const someVisibleSelected =
    !allVisibleSelected && visibleReferences.some((reference) => selected.has(reference))

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

  useEffect(() => {
    const visible = new Set(visibleReferences)
    setSelected((current) => new Set([...current].filter((reference) => visible.has(reference))))
  }, [visibleReferences])

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

  function toggleResource(reference: string, checked: boolean) {
    setSelected((current) => {
      const next = new Set(current)
      if (checked) next.add(reference)
      else next.delete(reference)
      return next
    })
  }

  function toggleAllVisible(checked: boolean) {
    setSelected(checked ? new Set(visibleReferences) : new Set())
  }

  return (
    <CataloguePage
      title="Resource Catalogue"
      description="Find and manage network-relevant resources."
      actions={
        <Button onClick={() => setShowCreate(true)}>
          <Plus className="size-[var(--napms-icon-size-control)]" aria-hidden="true" />
          New resource
        </Button>
      }
    >
      <CatalogueSurface>
        <form onSubmit={applySearch}>
          <CatalogueToolbar>
            <SearchInput
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder="Search by name, reference, address, scope or owner…"
              aria-label="Search resources"
            />

            <CatalogueFilterBar>
              <CatalogueFilterField label="Scope" className="xl:w-[290px]">
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
              </CatalogueFilterField>

              <CatalogueFilterField label="Lifecycle" className="xl:w-[155px]">
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
              </CatalogueFilterField>

              <CatalogueFilterField label="Data state" className="xl:w-[230px]">
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
              </CatalogueFilterField>

              <Button type="submit" variant="secondary" className="px-4">
                Apply
              </Button>
              <Button type="button" variant="ghost" className="px-1" onClick={resetFilters}>
                Reset
              </Button>
            </CatalogueFilterBar>
          </CatalogueToolbar>
        </form>

        <CatalogueViewBar>
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
        </CatalogueViewBar>

        {loading ? (
          <LoadingState>Loading resources…</LoadingState>
        ) : error ? (
          <ErrorState message={error.message} onRetry={() => void load()} />
        ) : items.length === 0 ? (
          <EmptyState
            title="No resources found"
            description="Change the search or filters, or create a new resource."
          />
        ) : (
          <DataTable minWidth={1200}>
            <colgroup>
              <col style={{ width: "52px" }} />
              <col style={{ width: "15.1%" }} />
              <col style={{ width: "11.8%" }} />
              <col style={{ width: "15.5%" }} />
              <col style={{ width: "14%" }} />
              <col style={{ width: "16.2%" }} />
              <col style={{ width: "9.4%" }} />
              <col style={{ width: "18%" }} />
            </colgroup>
            <DataTableHeader>
              <DataTableHeaderRow>
                <DataTableSelectionHead>
                  <Checkbox
                    checked={allVisibleSelected}
                    indeterminate={someVisibleSelected}
                    onChange={(event) => toggleAllVisible(event.target.checked)}
                    aria-label="Select all resources on this page"
                  />
                </DataTableSelectionHead>
                <DataTableHeadCell>Name</DataTableHeadCell>
                <DataTableHeadCell>Reference</DataTableHeadCell>
                <DataTableHeadCell>Addresses</DataTableHeadCell>
                <DataTableHeadCell>Scope(s)</DataTableHeadCell>
                <DataTableHeadCell>Technical owner</DataTableHeadCell>
                <DataTableHeadCell>Lifecycle</DataTableHeadCell>
                <DataTableHeadCell>Data state</DataTableHeadCell>
              </DataTableHeaderRow>
            </DataTableHeader>
            <DataTableBody>
              {items.map((item) => {
                const isSelected = selected.has(item.resourceReference)
                return (
                  <DataTableRow key={item.resourceReference} selected={isSelected}>
                    <DataTableSelectionCell>
                      <Checkbox
                        checked={isSelected}
                        onChange={(event) =>
                          toggleResource(item.resourceReference, event.target.checked)
                        }
                        aria-label={`Select ${item.displayName || shortId(item.resourceReference)}`}
                      />
                    </DataTableSelectionCell>
                    <DataTableCell>
                      <button
                        type="button"
                        className="font-semibold text-[var(--napms-color-primary)] hover:underline"
                        onClick={() => onOpenResource(item.resourceReference)}
                      >
                        {item.displayName || shortId(item.resourceReference)}
                      </button>
                    </DataTableCell>
                    <DataTableCell className="font-mono text-xs text-[var(--napms-color-text-secondary)]">
                      {shortId(item.resourceReference)}
                    </DataTableCell>
                    <DataTableCell>
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
                    </DataTableCell>
                    <DataTableCell>
                      <TagList values={item.currentScopes} />
                    </DataTableCell>
                    <DataTableCell className="text-[var(--napms-color-text-body)]">
                      {item.technicalOwners.length > 0 ? (
                        item.technicalOwners.join(", ")
                      ) : (
                        <span className="text-[var(--napms-color-text-muted)]">—</span>
                      )}
                    </DataTableCell>
                    <DataTableCell>
                      <LifecycleBadge value={item.lifecycle} />
                    </DataTableCell>
                    <DataTableCell>
                      <DataState item={item} />
                    </DataTableCell>
                  </DataTableRow>
                )
              })}
            </DataTableBody>
          </DataTable>
        )}

        <CataloguePagination>
          <span className="text-xs text-[var(--napms-color-text-secondary)]">
            Page {page} · up to 50 resources per page
            {selected.size > 0 ? ` · ${selected.size} selected` : ""}
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
                <h2 id="create-resource-title" className="text-lg font-bold text-[var(--napms-color-text-primary)]">
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
                <X className="size-[var(--napms-icon-size-control)]" aria-hidden="true" />
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
                  <p className="mt-3 text-sm text-[var(--napms-color-danger)]">{createError.message}</p>
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
