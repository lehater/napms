import { useEffect, useMemo, useState } from "react"
import { RefreshCw } from "lucide-react"

import { Button } from "@/design-system/components/Button"
import {
  DataTable,
  DataTableBody,
  DataTableHeadCell,
  DataTableHeader,
  DataTableHeaderRow,
} from "@/design-system/components/DataTable"
import { Field, Select } from "@/design-system/components/Field"
import { EmptyState, ErrorState, LoadingState } from "@/design-system/components/PageState"
import { SearchInput } from "@/design-system/components/SearchInput"
import { PageHeader } from "@/design-system/layout/PageHeader"
import { PageWorkspace } from "@/design-system/layout/PageWorkspace"
import { ListPagination } from "@/design-system/patterns/list/ListPage"
import { Surface } from "@/design-system/primitives/Surface"
import {
  getScopedConnectivityInventory,
  listScopedConnectivityScopes,
  type ScopedConnectivityInventoryPage,
} from "@/features/connectivity/api"
import { ConnectivityInventoryRows } from "@/features/connectivity/components/ConnectivityInventoryRows"
import type { RequestConnectivityContext } from "@/features/connectivity/model"
import { ApiError } from "@/lib/api"

export function ConnectivityPage({
  page,
  onPageChange,
  onRequestAccess,
}: {
  page: number
  onPageChange: (page: number) => void
  onRequestAccess: (context: RequestConnectivityContext) => void
}) {
  const [asOf, setAsOf] = useState(() => new Date().toISOString())
  const [scopes, setScopes] = useState<string[]>([])
  const [ambiguousScopes, setAmbiguousScopes] = useState<string[]>([])
  const [scope, setScope] = useState("")
  const [loadingScopes, setLoadingScopes] = useState(true)
  const [scopeError, setScopeError] = useState<ApiError | null>(null)
  const [inventory, setInventory] = useState<ScopedConnectivityInventoryPage | null>(null)
  const [loadingInventory, setLoadingInventory] = useState(false)
  const [inventoryError, setInventoryError] = useState<ApiError | null>(null)
  const [searchInput, setSearchInput] = useState("")
  const [search, setSearch] = useState("")

  useEffect(() => {
    let active = true
    setLoadingScopes(true)
    setScopeError(null)
    void listScopedConnectivityScopes(asOf)
      .then((result) => {
        if (!active) return
        const permitted = result.scopes.map((item) => item.scope)
        setScopes(permitted)
        setAmbiguousScopes(result.ambiguousScopes.map((item) => item.scope))
        setScope((current) => current && permitted.includes(current) ? current : (permitted[0] ?? ""))
      })
      .catch((caught) => {
        if (!active) return
        setScopes([])
        setAmbiguousScopes([])
        setScope("")
        setScopeError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Responsibility scopes could not be loaded."))
      })
      .finally(() => { if (active) setLoadingScopes(false) })
    return () => { active = false }
  }, [asOf])

  useEffect(() => {
    if (!scope) {
      setInventory(null)
      setLoadingInventory(false)
      return
    }
    let active = true
    setLoadingInventory(true)
    setInventoryError(null)
    void getScopedConnectivityInventory(scope, asOf, page, search)
      .then((result) => { if (active) setInventory(result) })
      .catch((caught) => {
        if (!active) return
        setInventory(null)
        setInventoryError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Connectivity inventory could not be loaded."))
      })
      .finally(() => { if (active) setLoadingInventory(false) })
    return () => { active = false }
  }, [scope, asOf, page, search])

  const updatedText = useMemo(() => new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "medium" }).format(new Date(asOf)), [asOf])

  function submitSearch(event: React.FormEvent) {
    event.preventDefault()
    setSearch(searchInput.trim())
    if (page !== 1) onPageChange(1)
  }

  const currentError = scopeError ?? inventoryError

  return (
    <PageWorkspace>
      <PageHeader
        title="Connectivity"
        description="Resources in your selected area of responsibility, the application components bound to them, and their connectivity to other systems."
        actions={
          <div className="text-right text-xs text-[var(--napms-color-text-secondary)]">
            <div>As of {updatedText}</div>
            <Button variant="ghost" size="sm" className="mt-1" onClick={() => setAsOf(new Date().toISOString())}>
              <RefreshCw className="size-3.5" aria-hidden="true" />Refresh
            </Button>
          </div>
        }
      />

      <Surface className="p-4">
        <div className="grid gap-4 lg:grid-cols-[minmax(240px,360px)_minmax(280px,1fr)_auto] lg:items-end">
          <Field label="Responsibility scope">
            <Select value={scope} disabled={loadingScopes || scopes.length === 0} onChange={(event) => { setScope(event.target.value); if (page !== 1) onPageChange(1) }}>
              {scopes.length === 0 ? <option value="">{loadingScopes ? "Loading scopes…" : "No available scopes"}</option> : null}
              {scopes.map((value) => <option key={value} value={value}>{value}</option>)}
            </Select>
          </Field>
          <form className="flex min-w-0 items-end gap-2" onSubmit={submitSearch}>
            <Field label="Search resources"><SearchInput value={searchInput} onChange={(event) => setSearchInput(event.target.value)} placeholder="Resource reference…" aria-label="Search resources" /></Field>
            <Button type="submit" variant="secondary">Search</Button>
          </form>
          {search ? <Button type="button" variant="ghost" onClick={() => { setSearchInput(""); setSearch(""); if (page !== 1) onPageChange(1) }}>Clear</Button> : <div />}
        </div>
      </Surface>

      {ambiguousScopes.length > 0 ? (
        <div className="rounded-[var(--napms-control-radius)] border border-[var(--napms-color-warning-dot)] bg-[var(--napms-color-warning-bg)] p-4 text-sm text-[var(--napms-color-warning)]">
          <div className="font-semibold">Some scopes are unavailable</div>
          <div className="mt-1">{ambiguousScopes.length} scope(s) have ambiguous ReadScopedConnectivity authority and remain fail-closed.</div>
        </div>
      ) : null}

      {inventory?.partial ? (
        <div className="rounded-[var(--napms-control-radius)] border border-[var(--napms-color-warning-dot)] bg-[var(--napms-color-warning-bg)] p-4 text-sm text-[var(--napms-color-warning)]">
          <div className="font-semibold">Some information is unavailable</div>
          <div className="mt-1">The resource topology below is trustworthy, but one or more Need, Decision, Policy, component, or realization dimensions could not be established. Unknown values are kept explicit.</div>
        </div>
      ) : null}

      {currentError ? <ErrorState message={`${currentError.code}: ${currentError.message}${currentError.correlationId ? ` · Correlation: ${currentError.correlationId}` : ""}`} /> : null}

      <Surface className="min-w-0 overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--napms-color-border)] px-5 py-4">
          <div>
            <h2 className="text-base font-semibold text-[var(--napms-color-text-primary)]">Resources and connectivity</h2>
            <p className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">{scope ? `Scope ${scope} · Resource page ${page}` : "Select a scope"}</p>
          </div>
          <div className="flex items-center gap-4 text-xs text-[var(--napms-color-text-secondary)]"><span>Need</span><span>Decision</span><span>Policy</span></div>
        </div>

        {loadingScopes || loadingInventory ? (
          <LoadingState>Loading connectivity…</LoadingState>
        ) : !scope ? (
          <EmptyState title="No responsibility scope available" description="No unambiguous ReadScopedConnectivity scope is currently available for this workspace." />
        ) : !inventory || inventory.items.length === 0 ? (
          <EmptyState title="No resources in this scope" description="No Resource is effectively affiliated with the selected responsibility scope at this time." />
        ) : (
          <DataTable width="wide">
            <DataTableHeader>
              <DataTableHeaderRow>
                <DataTableHeadCell className="w-[220px]">Component</DataTableHeadCell>
                <DataTableHeadCell className="w-[90px]">Direction</DataTableHeadCell>
                <DataTableHeadCell className="w-[180px]">Access</DataTableHeadCell>
                <DataTableHeadCell className="min-w-[260px]">Remote side</DataTableHeadCell>
                <DataTableHeadCell className="w-[190px]">Need</DataTableHeadCell>
                <DataTableHeadCell className="w-[150px]">Decision</DataTableHeadCell>
                <DataTableHeadCell className="w-[170px]">Policy</DataTableHeadCell>
                <DataTableHeadCell className="w-[140px]">Action</DataTableHeadCell>
              </DataTableHeaderRow>
            </DataTableHeader>
            <DataTableBody>
              {inventory.items.map((resourceItem) => <ConnectivityInventoryRows key={resourceItem.resource.resourceReference} item={resourceItem} scope={scope} onRequestAccess={onRequestAccess} />)}
            </DataTableBody>
          </DataTable>
        )}

        <ListPagination>
          <span className="text-xs text-[var(--napms-color-text-secondary)]">{inventory ? `Resource page ${inventory.page}` : null}</span>
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" disabled={page === 1 || loadingInventory} onClick={() => onPageChange(Math.max(1, page - 1))}>Previous</Button>
            <Button variant="secondary" size="sm" disabled={!inventory?.hasMore || loadingInventory} onClick={() => onPageChange(page + 1)}>Next</Button>
          </div>
        </ListPagination>
      </Surface>
    </PageWorkspace>
  )
}
