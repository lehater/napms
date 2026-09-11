import { useEffect, useState } from "react"

import { Button } from "@/design-system/components/Button"
import { Input } from "@/design-system/components/Field"
import { SearchInput } from "@/design-system/components/SearchInput"
import { createDeploymentResourceBinding } from "@/features/catalogues/api/targetCommands"
import type { DeploymentInteractionSide } from "@/features/catalogues/api/targetCatalogue"
import { listCatalogueResourceWorkspace, type ResourceWorkspaceItemDto } from "@/features/catalogues/api/resourceWorkspace"
import { ApiError } from "@/lib/api"

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
      .catch((caught) => { if (active) setError(errorFrom(caught)) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
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
    <div role="group" aria-label="Add resource" className="my-3 grid gap-4 rounded-[var(--napms-control-radius)] bg-[var(--napms-color-surface-subtle)] p-4">
      <div>
        <h3 className="font-semibold text-[var(--napms-color-text-primary)]">Add resource</h3>
        <p className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">Select an existing Resource Catalogue entry. Membership becomes effective now.</p>
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
        <SearchInput value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search Resource Catalogue" aria-label="Search Resource Catalogue" />
        <Input value={scopeQuery} onChange={(event) => setScopeQuery(event.target.value)} placeholder="Scope" aria-label="Resource scope" />
        <Button type="submit" variant="secondary">Search</Button>
      </form>

      {loading ? (
        <div className="text-sm text-[var(--napms-color-text-secondary)]">Loading Resource Catalogue…</div>
      ) : error ? (
        <div className="text-sm text-[var(--napms-color-danger)]">{error.message}</div>
      ) : (
        <div className="max-h-64 overflow-y-auto rounded-[var(--napms-control-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)]">
          {items.map((item) => {
            const alreadyBound = activeResourceReferences.has(item.resourceReference)
            const selectedItem = selected?.resourceReference === item.resourceReference
            return (
              <button
                key={item.resourceReference}
                type="button"
                disabled={alreadyBound}
                className={`flex w-full items-center justify-between gap-4 border-b border-[var(--napms-color-surface-muted)] px-4 py-3 text-left last:border-0 ${alreadyBound ? "cursor-default bg-[var(--napms-color-surface-subtle)] text-[var(--napms-color-text-muted)]" : selectedItem ? "bg-[var(--napms-color-primary-subtle)]" : "hover:bg-[var(--napms-color-surface-subtle)]"}`}
                onClick={() => setSelected(item)}
              >
                <span>
                  <span className="block text-sm font-semibold">{item.displayName ?? item.resourceReference}</span>
                  {item.displayName ? <span className="mt-0.5 block text-xs text-[var(--napms-color-text-muted)]">{item.resourceReference}</span> : null}
                </span>
                <span className="text-xs font-semibold">{alreadyBound ? "Already added" : selectedItem ? "Selected" : ""}</span>
              </button>
            )
          })}
          {items.length === 0 ? <div className="px-4 py-4 text-sm text-[var(--napms-color-text-secondary)]">No Resources found.</div> : null}
        </div>
      )}

      {hasMore ? <div className="text-xs text-[var(--napms-color-text-secondary)]">More Resources match. Refine search or Scope to narrow the selection.</div> : null}

      <div className="flex justify-end gap-2">
        <Button variant="secondary" onClick={onCancel}>Cancel</Button>
        <Button loading={saving} disabled={!selected || activeResourceReferences.has(selected.resourceReference)} onClick={() => void addSelected()}>Add resource</Button>
      </div>
    </div>
  )
}
