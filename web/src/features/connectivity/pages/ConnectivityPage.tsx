import { useEffect, useMemo, useState } from "react"
import { CircleAlert, Network, RefreshCw, Search } from "lucide-react"

import { Button } from "@/design-system/components/Button"
import { Field, Select } from "@/design-system/components/Field"
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

  const [inventory, setInventory] =
    useState<ScopedConnectivityInventoryPage | null>(null)
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
        setAmbiguousScopes(
          result.ambiguousScopes.map((item) => item.scope),
        )
        setScope((current) =>
          current && permitted.includes(current)
            ? current
            : (permitted[0] ?? ""),
        )
      })
      .catch((caught) => {
        if (!active) return
        setScopes([])
        setAmbiguousScopes([])
        setScope("")
        setScopeError(
          caught instanceof ApiError
            ? caught
            : new ApiError(
                500,
                "InternalError",
                "Responsibility scopes could not be loaded.",
              ),
        )
      })
      .finally(() => {
        if (active) setLoadingScopes(false)
      })

    return () => {
      active = false
    }
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
      .then((result) => {
        if (active) setInventory(result)
      })
      .catch((caught) => {
        if (!active) return
        setInventory(null)
        setInventoryError(
          caught instanceof ApiError
            ? caught
            : new ApiError(
                500,
                "InternalError",
                "Connectivity inventory could not be loaded.",
              ),
        )
      })
      .finally(() => {
        if (active) setLoadingInventory(false)
      })

    return () => {
      active = false
    }
  }, [scope, asOf, page, search])

  const updatedText = useMemo(
    () =>
      new Intl.DateTimeFormat(undefined, {
        dateStyle: "medium",
        timeStyle: "medium",
      }).format(new Date(asOf)),
    [asOf],
  )

  function submitSearch(event: React.FormEvent) {
    event.preventDefault()
    const normalized = searchInput.trim()
    setSearch(normalized)
    if (page !== 1) onPageChange(1)
  }

  return (
    <div className="w-full">
      <header className="mb-5 flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#64748B]">
            Connectivity
          </div>
          <h1 className="text-[28px] font-bold tracking-tight text-[#172033]">
            Connectivity
          </h1>
          <p className="mt-2 max-w-4xl text-sm text-[#64748B]">
            Resources in your selected area of responsibility, the application
            components bound to them, and their connectivity to other systems.
          </p>
        </div>
        <div className="text-right text-xs text-[#64748B]">
          <div>As of {updatedText}</div>
          <button
            type="button"
            onClick={() => setAsOf(new Date().toISOString())}
            className="mt-1 inline-flex items-center gap-1.5 font-semibold text-[#2563EB] hover:text-[#1D4ED8]"
          >
            <RefreshCw className="size-3.5" aria-hidden="true" />
            Refresh
          </button>
        </div>
      </header>

      <section className="mb-5 rounded-lg border border-[#E2E8F0] bg-white p-4">
        <div className="grid gap-4 lg:grid-cols-[minmax(240px,360px)_minmax(280px,1fr)_auto] lg:items-end">
          <Field label="Responsibility scope">
            <Select
              value={scope}
              disabled={loadingScopes || scopes.length === 0}
              onChange={(event) => {
                setScope(event.target.value)
                if (page !== 1) onPageChange(1)
              }}
            >
              {scopes.length === 0 ? (
                <option value="">
                  {loadingScopes ? "Loading scopes…" : "No available scopes"}
                </option>
              ) : null}
              {scopes.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </Select>
          </Field>

          <form
            className="flex min-w-0 items-end gap-2"
            onSubmit={submitSearch}
          >
            <Field label="Search resources">
              <div className="relative">
                <Search
                  className="pointer-events-none absolute left-3 top-3 size-4 text-[#94A3B8]"
                  aria-hidden="true"
                />
                <input
                  type="search"
                  value={searchInput}
                  maxLength={256}
                  onChange={(event) => setSearchInput(event.target.value)}
                  placeholder="Resource reference…"
                  className="min-h-10 w-full rounded-md border border-[#CBD5E1] py-2 pl-9 pr-3 text-sm"
                />
              </div>
            </Field>
            <Button type="submit" variant="secondary">
              Search
            </Button>
          </form>

          {search ? (
            <Button
              type="button"
              variant="ghost"
              onClick={() => {
                setSearchInput("")
                setSearch("")
                if (page !== 1) onPageChange(1)
              }}
            >
              Clear
            </Button>
          ) : (
            <div />
          )}
        </div>
      </section>

      {ambiguousScopes.length > 0 ? (
        <div className="mb-4 rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          <div className="font-semibold">Some scopes are unavailable</div>
          <div className="mt-1">
            {ambiguousScopes.length} scope(s) have ambiguous
            ReadScopedConnectivity authority and remain fail-closed.
          </div>
        </div>
      ) : null}

      {inventory?.partial ? (
        <div className="mb-4 rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          <div className="font-semibold">Some information is unavailable</div>
          <div className="mt-1">
            The resource topology below is trustworthy, but one or more Need,
            Decision, Policy, component, or realization dimensions could not be
            established. Unknown values are kept explicit.
          </div>
        </div>
      ) : null}

      {scopeError || inventoryError ? (
        <div
          role="alert"
          className="mb-4 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800"
        >
          <div className="flex gap-3">
            <CircleAlert
              className="mt-0.5 size-4 shrink-0"
              aria-hidden="true"
            />
            <div>
              <div className="font-semibold">
                {(scopeError ?? inventoryError)?.code}
              </div>
              <div className="mt-1">
                {(scopeError ?? inventoryError)?.message}
              </div>
              {(scopeError ?? inventoryError)?.correlationId ? (
                <div className="mt-2 text-xs">
                  Correlation: {(scopeError ?? inventoryError)?.correlationId}
                </div>
              ) : null}
            </div>
          </div>
        </div>
      ) : null}

      <section className="overflow-hidden rounded-lg border border-[#E2E8F0] bg-white">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#E2E8F0] px-5 py-4">
          <div>
            <h2 className="text-base font-semibold text-[#172033]">
              Resources and connectivity
            </h2>
            <p className="mt-1 text-xs text-[#64748B]">
              {scope ? `Scope ${scope} · Resource page ${page}` : "Select a scope"}
            </p>
          </div>
          <div className="flex items-center gap-4 text-xs text-[#64748B]">
            <span>Need</span>
            <span>Decision</span>
            <span>Policy</span>
          </div>
        </div>

        {loadingScopes || loadingInventory ? (
          <div className="p-8 text-sm text-[#64748B]">
            Loading connectivity…
          </div>
        ) : !scope ? (
          <div className="p-10 text-center">
            <Network
              className="mx-auto size-7 text-[#94A3B8]"
              aria-hidden="true"
            />
            <div className="mt-3 text-sm font-semibold text-[#334155]">
              No responsibility scope available
            </div>
            <div className="mt-2 text-sm text-[#64748B]">
              No unambiguous ReadScopedConnectivity scope is currently
              available for this workspace.
            </div>
          </div>
        ) : !inventory || inventory.items.length === 0 ? (
          <div className="p-10 text-center">
            <Network
              className="mx-auto size-7 text-[#94A3B8]"
              aria-hidden="true"
            />
            <div className="mt-3 text-sm font-semibold text-[#334155]">
              No resources in this scope
            </div>
            <div className="mt-2 text-sm text-[#64748B]">
              No Resource is effectively affiliated with the selected
              responsibility scope at this time.
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[1180px] border-collapse text-left text-sm">
              <thead className="bg-[#F8FAFC] text-xs uppercase tracking-wide text-[#64748B]">
                <tr>
                  <th className="w-[220px] px-4 py-3 font-semibold">
                    Component
                  </th>
                  <th className="w-[90px] px-4 py-3 font-semibold">
                    Direction
                  </th>
                  <th className="w-[180px] px-4 py-3 font-semibold">Access</th>
                  <th className="min-w-[260px] px-4 py-3 font-semibold">
                    Remote side
                  </th>
                  <th className="w-[190px] px-4 py-3 font-semibold">Need</th>
                  <th className="w-[150px] px-4 py-3 font-semibold">
                    Decision
                  </th>
                  <th className="w-[170px] px-4 py-3 font-semibold">Policy</th>
                  <th className="w-[140px] px-4 py-3 font-semibold">Action</th>
                </tr>
              </thead>
              <tbody>
                {inventory.items.map((resourceItem) => (
                  <ConnectivityInventoryRows
                    key={resourceItem.resource.resourceReference}
                    item={resourceItem}
                    scope={scope}
                    onRequestAccess={onRequestAccess}
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="flex items-center justify-between border-t border-[#E2E8F0] px-5 py-4">
          <div className="text-xs text-[#64748B]">
            {inventory ? `Resource page ${inventory.page}` : null}
          </div>
          <div className="flex gap-2">
            <Button
              variant="secondary"
              disabled={page === 1 || loadingInventory}
              onClick={() => onPageChange(Math.max(1, page - 1))}
            >
              Previous
            </Button>
            <Button
              variant="secondary"
              disabled={!inventory?.hasMore || loadingInventory}
              onClick={() => onPageChange(page + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      </section>
    </div>
  )
}
