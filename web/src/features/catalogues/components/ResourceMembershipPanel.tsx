import { useEffect, useState } from "react"
import { Search } from "lucide-react"

import { ApiError } from "@/lib/api"
import { Button } from "@/components/ui/Button"
import { listCatalogueResourceWorkspace, type ResourceWorkspaceItemDto } from "@/features/catalogues/api/resourceWorkspace"
import { createDeploymentResourceBinding } from "@/features/catalogues/api/targetCommands"
import type { DeploymentInteractionSide } from "@/features/catalogues/api/targetCatalogue"

const inputClass =
  "min-h-10 min-w-0 rounded-md border border-[#CBD5E1] bg-white px-3 py-2 text-sm text-[#172033] outline-none focus:border-[#2563EB] focus:ring-2 focus:ring-[#DBEAFE]"

function errorFrom(caught: unknown) {
  return caught instanceof ApiError
    ? caught
    : new ApiError(500, "InternalError", "Resource membership could not be changed.")
}

export function ResourceMembershipPanel({
  deploymentInteractionId,
  side,
  activeResourceReferences,
  onChanged,
  onCancel,
}: {
  deploymentInteractionId: string
  side: DeploymentInteractionSide
  activeResourceReferences: Set<string>
  onChanged: () => void
  onCancel: () => void
}) {
  const [items, setItems] = useState<ResourceWorkspaceItemDto[]>([])
  const [selected, setSelected] = useState<ResourceWorkspaceItemDto | null>(null)
  const [query, setQuery] = useState("")
  const [scopeQuery, setScopeQuery] = useState("")
  const [search, setSearch] = useState("")
  const [scope, setScope] = useState("")
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)
  const [hasMore, setHasMore] = useState(false)

  useEffect(() => {
    let active = true
    setLoading(true)
    setError(null)
    void listCatalogueResourceWorkspace(1, search, scope)
      .then((result) => {
        if (!active) return
        setItems(result.items)
        setHasMore(result.hasMore)
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
  }, [search, scope])

  async function addSelected() {
    if (!selected || activeResourceReferences.has(selected.resourceReference)) return
    setSaving(true)
    setError(null)
    try {
      await createDeploymentResourceBinding({
        deploymentInteractionId,
        side,
        resourceReference: selected.resourceReference,
        validFrom: new Date().toISOString(),
      })
      onChanged()
      onCancel()
    } catch (caught) {
      setError(errorFrom(caught))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div
      role="group"
      aria-label="Add resource"
      className="grid gap-4 border-b border-[#E2E8F0] bg-[#F8FAFC] p-5"
    >
      <div>
        <h3 className="font-semibold text-[#172033]">Add resource</h3>
        <p className="mt-1 text-xs text-[#64748B]">
          Select an existing Resource Catalogue entry. Membership becomes effective now.
        </p>
      </div>

      <form
        className="grid gap-2 md:grid-cols-[minmax(16rem,1fr)_minmax(10rem,16rem)_auto]"
        onSubmit={(event) => {
          event.preventDefault()
          setSelected(null)
          setSearch(query.trim())
          setScope(scopeQuery.trim())
        }}
      >
        <div className="relative min-w-0">
          <Search className="pointer-events-none absolute left-3 top-3 size-4 text-[#94A3B8]" aria-hidden="true" />
          <input
            className={`${inputClass} w-full pl-9`}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search Resource Catalogue"
            aria-label="Search Resource Catalogue"
          />
        </div>
        <input
          className={inputClass}
          value={scopeQuery}
          onChange={(event) => setScopeQuery(event.target.value)}
          placeholder="Scope"
          aria-label="Resource scope"
        />
        <Button type="submit" variant="secondary">Search</Button>
      </form>

      {loading ? (
        <div className="text-sm text-[#64748B]">Loading Resource Catalogue…</div>
      ) : error ? (
        <div className="text-sm text-red-700">{error.message}</div>
      ) : (
        <div className="max-h-64 overflow-y-auto rounded-md border border-[#E2E8F0] bg-white">
          {items.map((item) => {
            const alreadyBound = activeResourceReferences.has(item.resourceReference)
            return (
              <button
                key={item.resourceReference}
                type="button"
                disabled={alreadyBound}
                className={`flex w-full items-center justify-between gap-4 border-b border-[#F1F5F9] px-4 py-3 text-left last:border-0 ${alreadyBound ? "cursor-default bg-[#F8FAFC] text-[#94A3B8]" : "hover:bg-[#F8FAFC]"}`}
                onClick={() => setSelected(item)}
              >
                <span>
                  <span className="block text-sm font-semibold">{item.displayName ?? item.resourceReference}</span>
                  {item.displayName ? <span className="mt-0.5 block text-xs text-[#94A3B8]">{item.resourceReference}</span> : null}
                </span>
                <span className="text-xs font-semibold">{alreadyBound ? "Already added" : selected?.resourceReference === item.resourceReference ? "Selected" : ""}</span>
              </button>
            )
          })}
          {items.length === 0 ? <div className="px-4 py-4 text-sm text-[#64748B]">No Resources found.</div> : null}
        </div>
      )}

      {hasMore ? (
        <div className="text-xs text-[#64748B]">More Resources match. Refine search or Scope to narrow the selection.</div>
      ) : null}

      <div className="flex justify-end gap-2">
        <Button variant="secondary" onClick={onCancel}>Cancel</Button>
        <Button
          loading={saving}
          disabled={!selected || activeResourceReferences.has(selected.resourceReference)}
          onClick={() => void addSelected()}
        >
          Add resource
        </Button>
      </div>
    </div>
  )
}
