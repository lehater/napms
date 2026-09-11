import { useEffect, useMemo, useState } from "react"
import { Plus } from "lucide-react"

import { Button } from "@/design-system/components/Button"
import { Select } from "@/design-system/components/Field"
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
import { EmptyState, ErrorState, LoadingState } from "@/design-system/components/PageState"
import { SearchInput } from "@/design-system/components/SearchInput"
import { TagList } from "@/design-system/components/Tag"
import {
  EmptyValue,
  PrimaryTableAction,
  ReferenceText,
  TechnicalValueList,
} from "@/design-system/components/TableValue"
import {
  CatalogueFilterBar,
  CatalogueFilterField,
  CataloguePage,
  CataloguePaginationControls,
  CatalogueSurface,
  CatalogueToolbar,
  CatalogueViewBar,
} from "@/design-system/patterns/catalogue/CataloguePage"
import { createCatalogueResource } from "@/features/catalogues/api/catalogue"
import {
  listCatalogueResourceWorkspace,
  type ResourceWorkspaceDataState,
  type ResourceWorkspaceItemDto,
  type ResourceWorkspaceLifecycle,
  type ResourceWorkspaceSortBy,
  type ResourceWorkspaceSortDirection,
} from "@/features/catalogues/api/resourceWorkspace"
import { shortId } from "@/features/catalogues/components/CatalogueIdentity"
import { CatalogueLifecycleStatus } from "@/features/catalogues/components/CatalogueLifecycleStatus"
import { CreateResourceDialog } from "@/features/catalogues/components/CreateResourceDialog"
import { ResourceDataState } from "@/features/catalogues/components/ResourceDataState"
import { ApiError } from "@/lib/api"

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError
    ? caught
    : new ApiError(500, "InternalError", fallback)
}

const emptyCounts = {
  all: 0,
  active: 0,
  retired: 0,
  missingAddress: 0,
  missingScope: 0,
  missingResponsibility: 0,
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
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [total, setTotal] = useState(0)
  const [counts, setCounts] = useState(emptyCounts)

  const [searchInput, setSearchInput] = useState("")
  const [search, setSearch] = useState("")
  const [scopeInput, setScopeInput] = useState("")
  const [scopeFilter, setScopeFilter] = useState("")
  const [lifecycle, setLifecycle] = useState<ResourceWorkspaceLifecycle>("active")
  const [dataState, setDataState] = useState<ResourceWorkspaceDataState>("")
  const [pageSize, setPageSize] = useState(50)
  const [sortBy, setSortBy] = useState<ResourceWorkspaceSortBy>("name")
  const [sortDirection, setSortDirection] = useState<ResourceWorkspaceSortDirection>("asc")
  const [showCreate, setShowCreate] = useState(false)

  const visibleScopes = useMemo(
    () => Array.from(new Set(items.flatMap((item) => item.currentScopes))).sort(),
    [items],
  )
  const scopeOptions = useMemo(
    () => Array.from(new Set([scopeInput, scopeFilter, ...visibleScopes].filter(Boolean))).sort(),
    [scopeFilter, scopeInput, visibleScopes],
  )
  const visibleReferences = useMemo(
    () => items.map((item) => item.resourceReference),
    [items],
  )
  const allVisibleSelected = visibleReferences.length > 0 && visibleReferences.every((reference) => selected.has(reference))
  const someVisibleSelected = !allVisibleSelected && visibleReferences.some((reference) => selected.has(reference))

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const result = await listCatalogueResourceWorkspace(page, search, scopeFilter, {
        pageSize,
        lifecycle,
        dataState,
        sortBy,
        sortDirection,
      })
      setItems(result.items)
      setTotal(result.total)
      setCounts(result.counts)
    } catch (caught) {
      setError(errorFrom(caught, "Resources could not be loaded."))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [page, search, scopeFilter, lifecycle, dataState, pageSize, sortBy, sortDirection])

  useEffect(() => {
    const nextSearch = searchInput.trim()
    if (nextSearch === search) return
    const timeout = window.setTimeout(() => {
      if (page !== 1) onPageChange(1)
      setSearch(nextSearch)
    }, 250)
    return () => window.clearTimeout(timeout)
  }, [page, search, searchInput, onPageChange])

  useEffect(() => {
    const visible = new Set(visibleReferences)
    setSelected((current) => new Set([...current].filter((reference) => visible.has(reference))))
  }, [visibleReferences])

  async function createResource(displayName: string | null) {
    try {
      const created = await createCatalogueResource(displayName)
      onOpenResource(created.resourceReference)
      return null
    } catch (caught) {
      return errorFrom(caught, "Resource could not be created.").message
    }
  }

  function applySearch(event: React.FormEvent) {
    event.preventDefault()
    if (page !== 1) onPageChange(1)
    setSearch(searchInput.trim())
  }

  function resetPage() {
    if (page !== 1) onPageChange(1)
  }

  function updateScope(next: string) {
    resetPage()
    setScopeInput(next)
    setScopeFilter(next)
  }

  function updateDataState(next: ResourceWorkspaceDataState) {
    resetPage()
    setDataState(next)
  }

  function setQuickFilter(next: "all" | "active" | "retired" | "missing-address" | "missing-responsibility" | "missing-scope") {
    resetPage()
    if (next === "active" || next === "retired" || next === "all") {
      setLifecycle(next)
      setDataState("")
      return
    }
    setLifecycle("all")
    setDataState(next)
  }

  function resetFilters() {
    setSearchInput("")
    setSearch("")
    setScopeInput("")
    setScopeFilter("")
    setLifecycle("active")
    setDataState("")
    resetPage()
  }

  function updateSort(field: ResourceWorkspaceSortBy) {
    resetPage()
    if (sortBy === field) {
      setSortDirection((value) => value === "asc" ? "desc" : "asc")
    } else {
      setSortBy(field)
      setSortDirection("asc")
    }
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

  const quickFilters = [
    { key: "all" as const, label: "All", count: counts.all, selected: lifecycle === "all" && dataState === "" },
    { key: "active" as const, label: "Active", count: counts.active, selected: lifecycle === "active" && dataState === "" },
    { key: "retired" as const, label: "Retired", count: counts.retired, selected: lifecycle === "retired" && dataState === "" },
    { key: "missing-address" as const, label: "No address", count: counts.missingAddress, selected: dataState === "missing-address" },
    { key: "missing-responsibility" as const, label: "No responsibility", count: counts.missingResponsibility, selected: dataState === "missing-responsibility" },
    { key: "missing-scope" as const, label: "No scope", count: counts.missingScope, selected: dataState === "missing-scope" },
  ]

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
              placeholder="Search by name, reference, address, owner…"
              aria-label="Search resources"
            />

            <CatalogueFilterBar>
              <CatalogueFilterField label="Scope" className="xl:w-[170px]">
                <Select value={scopeInput} onChange={(event) => updateScope(event.target.value)} aria-label="Filter resources by scope">
                  <option value="">All scopes</option>
                  {scopeOptions.map((scope) => <option key={scope} value={scope}>{scope}</option>)}
                </Select>
              </CatalogueFilterField>

              <CatalogueFilterField label="Lifecycle" className="xl:w-[170px]">
                <Select
                  value={lifecycle}
                  onChange={(event) => {
                    resetPage()
                    setLifecycle(event.target.value as ResourceWorkspaceLifecycle)
                  }}
                >
                  <option value="active">Active</option>
                  <option value="retired">Retired</option>
                  <option value="all">All</option>
                </Select>
              </CatalogueFilterField>

              <CatalogueFilterField label="Data state" className="xl:w-[170px]">
                <Select value={dataState} onChange={(event) => updateDataState(event.target.value as ResourceWorkspaceDataState)}>
                  <option value="">All</option>
                  <option value="missing-address">Missing address</option>
                  <option value="missing-scope">Missing scope</option>
                  <option value="missing-responsibility">Missing responsibility</option>
                </Select>
              </CatalogueFilterField>

              <Button type="button" variant="ghost" size="sm" className="xl:ml-auto" onClick={resetFilters}>Reset</Button>
            </CatalogueFilterBar>
          </CatalogueToolbar>
        </form>

        <CatalogueViewBar>
          {quickFilters.map((filter) => (
            <FilterChip key={filter.key} selected={filter.selected} onClick={() => setQuickFilter(filter.key)}>
              <span className="inline-flex items-center gap-2">
                <span>{filter.label}</span>
                <span className="tabular-nums">{filter.count.toLocaleString()}</span>
              </span>
            </FilterChip>
          ))}
        </CatalogueViewBar>

        {loading ? (
          <LoadingState>Loading resources…</LoadingState>
        ) : error ? (
          <ErrorState message={error.message} onRetry={() => void load()} />
        ) : items.length === 0 ? (
          <EmptyState title="No resources found" description="Change the search or filters, or create a new resource." />
        ) : (
          <DataTable minWidth={1120}>
            <colgroup>
              <col style={{ width: "var(--napms-table-selection-column)" }} />
              <col style={{ width: "15%" }} />
              <col style={{ width: "12%" }} />
              <col style={{ width: "16%" }} />
              <col style={{ width: "17%" }} />
              <col style={{ width: "16%" }} />
              <col style={{ width: "10%" }} />
              <col style={{ width: "14%" }} />
            </colgroup>
            <DataTableHeader>
              <DataTableHeaderRow>
                <DataTableSelectionHead>
                  <Checkbox checked={allVisibleSelected} indeterminate={someVisibleSelected} onChange={(event) => toggleAllVisible(event.target.checked)} aria-label="Select all resources on this page" />
                </DataTableSelectionHead>
                <DataTableHeadCell onSort={() => updateSort("name")} sortDirection={sortBy === "name" ? sortDirection : null} ariaLabel="Sort by name">Name</DataTableHeadCell>
                <DataTableHeadCell onSort={() => updateSort("reference")} sortDirection={sortBy === "reference" ? sortDirection : null} ariaLabel="Sort by reference">Reference</DataTableHeadCell>
                <DataTableHeadCell>Addresses</DataTableHeadCell>
                <DataTableHeadCell>Scope(s)</DataTableHeadCell>
                <DataTableHeadCell>Technical owner</DataTableHeadCell>
                <DataTableHeadCell onSort={() => updateSort("lifecycle")} sortDirection={sortBy === "lifecycle" ? sortDirection : null} ariaLabel="Sort by lifecycle">Lifecycle</DataTableHeadCell>
                <DataTableHeadCell>Data state</DataTableHeadCell>
              </DataTableHeaderRow>
            </DataTableHeader>
            <DataTableBody>
              {items.map((item) => {
                const isSelected = selected.has(item.resourceReference)
                return (
                  <DataTableRow key={item.resourceReference} selected={isSelected}>
                    <DataTableSelectionCell>
                      <Checkbox checked={isSelected} onChange={(event) => toggleResource(item.resourceReference, event.target.checked)} aria-label={`Select ${item.displayName || shortId(item.resourceReference)}`} />
                    </DataTableSelectionCell>
                    <DataTableCell>
                      <PrimaryTableAction onClick={() => onOpenResource(item.resourceReference)}>{item.displayName || shortId(item.resourceReference)}</PrimaryTableAction>
                    </DataTableCell>
                    <DataTableCell><ReferenceText>{shortId(item.resourceReference)}</ReferenceText></DataTableCell>
                    <DataTableCell><TechnicalValueList values={item.currentAddresses} /></DataTableCell>
                    <DataTableCell><TagList values={item.currentScopes} /></DataTableCell>
                    <DataTableCell className="text-[var(--napms-color-text-body)]">{item.technicalOwners.length > 0 ? item.technicalOwners.join(", ") : <EmptyValue />}</DataTableCell>
                    <DataTableCell><CatalogueLifecycleStatus value={item.lifecycle} /></DataTableCell>
                    <DataTableCell><ResourceDataState item={item} /></DataTableCell>
                  </DataTableRow>
                )
              })}
            </DataTableBody>
          </DataTable>
        )}

        <CataloguePaginationControls
          page={page}
          pageSize={pageSize}
          total={total}
          disabled={loading}
          onPageChange={onPageChange}
          onPageSizeChange={(nextPageSize) => {
            setPageSize(nextPageSize)
            if (page !== 1) onPageChange(1)
          }}
        />
      </CatalogueSurface>

      <CreateResourceDialog
        open={showCreate}
        onClose={() => setShowCreate(false)}
        onCreate={createResource}
      />
    </CataloguePage>
  )
}
