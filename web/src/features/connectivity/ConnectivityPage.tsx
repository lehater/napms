import { FormEvent, useEffect, useMemo, useState } from "react"
import {
  ArrowLeft,
  ArrowRight,
  CircleAlert,
  Network,
  RefreshCw,
  Search,
} from "lucide-react"

import {
  ApiError,
  getScopedConnectivityInventory,
  listScopedConnectivityScopes,
  type ScopedConnectivityDecisionSummary,
  type ScopedConnectivityInventoryPage,
  type ScopedConnectivityNeedSummary,
  type ScopedConnectivityPolicySummary,
  type ScopedConnectivityResource,
} from "@/api"
import { Button } from "@/components/ui/Button"
import { Field, Select } from "@/components/ui/Field"

function badgeClasses(
  tone: "good" | "warn" | "bad" | "muted" | "unknown",
): string {
  return {
    good: "border-green-200 bg-green-50 text-green-800",
    warn: "border-amber-200 bg-amber-50 text-amber-900",
    bad: "border-red-200 bg-red-50 text-red-800",
    muted: "border-slate-200 bg-slate-100 text-slate-700",
    unknown: "border-orange-200 bg-orange-50 text-orange-800",
  }[tone]
}

function Badge({
  children,
  tone,
  title,
}: {
  children: React.ReactNode
  tone: "good" | "warn" | "bad" | "muted" | "unknown"
  title?: string
}) {
  return (
    <span
      className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${badgeClasses(tone)}`}
      title={title}
    >
      {children}
    </span>
  )
}

function NeedCell({ value }: { value: ScopedConnectivityNeedSummary }) {
  const need =
    value.current === "Required" ? (
      <Badge tone="good">Required</Badge>
    ) : value.current === "Unknown" ? (
      <Badge tone="unknown">Unknown need</Badge>
    ) : value.historicalOnly ? (
      <Badge tone="muted">Not current</Badge>
    ) : (
      <Badge tone="muted">No current need</Badge>
    )

  const coverage =
    value.coverage === "Covered" ? (
      <Badge tone="good">Covered</Badge>
    ) : value.coverage === "Uncovered" ? (
      <Badge
        tone="warn"
        title="No exact matching Rule contributes effective desired policy. This does not mean Denied."
      >
        Uncovered
      </Badge>
    ) : value.coverage === "Unknown" ? (
      <Badge tone="unknown">Coverage unknown</Badge>
    ) : value.coverage === "NotCurrent" ? (
      <Badge tone="muted">Not current</Badge>
    ) : null

  return (
    <div className="flex flex-wrap gap-1.5">
      {need}
      {coverage}
    </div>
  )
}

function DecisionCell({
  value,
}: {
  value: ScopedConnectivityDecisionSummary
}) {
  switch (value.state) {
    case "Allowed":
      return <Badge tone="good">Allowed</Badge>
    case "NotAllowed":
      return <Badge tone="bad">Not allowed</Badge>
    case "NoFinalDecision":
      return <Badge tone="muted">No final decision</Badge>
    case "Unknown":
      return (
        <Badge
          tone="unknown"
          title="The final Decision cannot currently be established. This is not a Pending decision state."
        >
          Unknown
        </Badge>
      )
  }
}

function PolicyCell({ value }: { value: ScopedConnectivityPolicySummary }) {
  if (value.ruleExists === "Unknown") {
    return <Badge tone="unknown">Unknown</Badge>
  }
  if (value.ruleExists === "No") {
    return <Badge tone="muted">No rule</Badge>
  }
  if (value.operationalState === "Inactive") {
    return <Badge tone="muted">Inactive</Badge>
  }
  if (
    value.operationalState === "Active" &&
    value.effectiveAtAsOf === "Yes"
  ) {
    return <Badge tone="good">Active · effective</Badge>
  }
  if (
    value.operationalState === "Active" &&
    value.effectiveAtAsOf === "No"
  ) {
    return <Badge tone="warn">Active · not effective</Badge>
  }
  return <Badge tone="unknown">Unknown</Badge>
}

function endpointText(resource: ScopedConnectivityResource): string {
  if (resource.realizationState === "Unknown") return "Realization unknown"
  if (resource.endpoints.length === 0) {
    return resource.realizationState === "Unresolved"
      ? "No current endpoint realization"
      : "No endpoints"
  }
  return resource.endpoints
    .map((endpoint) => endpoint.technicalAddress)
    .join(", ")
}

function RemoteSide({
  resourcesKnown,
  resources,
  componentName,
  componentId,
}: {
  resourcesKnown: boolean
  resources: ScopedConnectivityResource[]
  componentName: string | null
  componentId: string
}) {
  return (
    <div className="min-w-[180px]">
      <div className="font-medium text-[#172033]">
        {componentName?.trim() || componentId}
      </div>
      {componentName?.trim() ? (
        <div className="mt-0.5 font-mono text-[11px] text-[#94A3B8]">
          {componentId}
        </div>
      ) : null}
      <div className="mt-1 text-xs text-[#64748B]">
        {!resourcesKnown
          ? "Remote resource data unavailable"
          : resources.length === 0
            ? "Remote resource unresolved"
            : resources
                .map(
                  (resource) =>
                    `${resource.resourceReference} · ${endpointText(resource)}`,
                )
                .join(" · ")}
      </div>
    </div>
  )
}

export function ConnectivityPage({
  page,
  onPageChange,
}: {
  page: number
  onPageChange: (page: number) => void
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

  function submitSearch(event: FormEvent) {
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
                </tr>
              </thead>
              <tbody>
                {inventory.items.map((resourceItem) => (
                  <ResourceRows
                    key={resourceItem.resource.resourceReference}
                    item={resourceItem}
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

function ResourceRows({
  item,
}: {
  item: ScopedConnectivityInventoryPage["items"][number]
}) {
  const resource = item.resource
  const endpointSummary = endpointText(resource)

  return (
    <>
      <tr className="border-t border-[#CBD5E1] bg-[#F8FAFC]">
        <td colSpan={7} className="px-4 py-3">
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
            <div className="font-semibold text-[#172033]">
              {resource.resourceReference}
            </div>
            <div className="font-mono text-xs text-[#64748B]">
              {endpointSummary}
            </div>
            {resource.realizationState !== "Resolved" ? (
              <Badge
                tone={
                  resource.realizationState === "Unknown"
                    ? "unknown"
                    : "muted"
                }
              >
                {resource.realizationState === "Unknown"
                  ? "Realization unknown"
                  : "No current realization"}
              </Badge>
            ) : null}
          </div>
        </td>
      </tr>

      {!item.componentsKnown ? (
        <tr className="border-t border-[#E2E8F0]">
          <td colSpan={7} className="px-8 py-4 text-sm text-[#64748B]">
            Component binding information is unavailable.
          </td>
        </tr>
      ) : item.components.length === 0 ? (
        <tr className="border-t border-[#E2E8F0]">
          <td colSpan={7} className="px-8 py-4 text-sm text-[#64748B]">
            No Component Deployment is currently bound to this Resource.
          </td>
        </tr>
      ) : (
        item.components.flatMap((component) => {
          const componentCell = (
            <div>
              <div className="font-medium text-[#172033]">
                {component.displayName?.trim() ||
                  component.componentDeploymentId}
              </div>
              {component.displayName?.trim() ? (
                <div className="mt-0.5 font-mono text-[11px] text-[#94A3B8]">
                  {component.componentDeploymentId}
                </div>
              ) : null}
            </div>
          )

          if (!component.relationshipsKnown) {
            return [
              <tr
                key={`${resource.resourceReference}:${component.componentDeploymentId}:unknown`}
                className="border-t border-[#E2E8F0] align-top"
              >
                <td className="px-4 py-3 pl-8">{componentCell}</td>
                <td colSpan={6} className="px-4 py-3 text-[#64748B]">
                  Connectivity relationship data is unavailable.
                </td>
              </tr>,
            ]
          }

          if (component.relationships.length === 0) {
            return [
              <tr
                key={`${resource.resourceReference}:${component.componentDeploymentId}:empty`}
                className="border-t border-[#E2E8F0] align-top"
              >
                <td className="px-4 py-3 pl-8">{componentCell}</td>
                <td colSpan={6} className="px-4 py-3 text-[#64748B]">
                  No connectivity is declared for this Component.
                </td>
              </tr>,
            ]
          }

          return component.relationships.map((relationship, index) => (
            <tr
              key={`${resource.resourceReference}:${component.componentDeploymentId}:${relationship.semanticIdentity.dcsContractRevisionId}:${relationship.direction}:${index}`}
              className="border-t border-[#E2E8F0] align-top hover:bg-[#FCFDFE]"
            >
              <td className="px-4 py-3 pl-8">
                {index === 0 ? componentCell : null}
              </td>
              <td className="px-4 py-3">
                <span className="inline-flex items-center gap-1.5 font-medium text-[#334155]">
                  {relationship.direction === "Outgoing" ? (
                    <>
                      <ArrowRight className="size-4" aria-hidden="true" />
                      Out
                    </>
                  ) : (
                    <>
                      <ArrowLeft className="size-4" aria-hidden="true" />
                      In
                    </>
                  )}
                </span>
              </td>
              <td className="px-4 py-3">
                <div className="font-medium text-[#172033]">
                  {relationship.dcsDisplayName?.trim() || "Communication"}
                </div>
                <div className="mt-1 font-mono text-xs text-[#64748B]">
                  {relationship.accessSummary || "Technical details unavailable"}
                </div>
              </td>
              <td className="px-4 py-3">
                <RemoteSide
                  resourcesKnown={relationship.remoteResourcesKnown}
                  resources={relationship.remoteResources}
                  componentName={relationship.remoteComponent.displayName}
                  componentId={relationship.remoteComponent.componentDeploymentId}
                />
              </td>
              <td className="px-4 py-3">
                <NeedCell value={relationship.need} />
              </td>
              <td className="px-4 py-3">
                <DecisionCell value={relationship.decision} />
              </td>
              <td className="px-4 py-3">
                <PolicyCell value={relationship.policy} />
              </td>
            </tr>
          ))
        })
      )}
    </>
  )
}
