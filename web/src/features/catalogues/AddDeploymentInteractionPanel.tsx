import { useEffect, useState } from "react"
import { Search } from "lucide-react"

import { ApiError } from "@/api"
import { Button } from "@/components/ui/Button"
import { CataloguePager } from "@/features/catalogues/CataloguePager"
import {
  listAvailableInteractions,
  selectDeploymentInteraction,
  type InteractionDefinitionSummaryDto,
} from "@/features/catalogues/targetCatalogueApi"
import { trafficSummary } from "@/features/catalogues/targetPresentation"

const inputClass =
  "min-h-10 min-w-0 rounded-md border border-[#CBD5E1] bg-white px-3 py-2 text-sm text-[#172033] outline-none focus:border-[#2563EB] focus:ring-2 focus:ring-[#DBEAFE]"

function errorFrom(caught: unknown) {
  return caught instanceof ApiError
    ? caught
    : new ApiError(500, "InternalError", "Interaction selection could not be completed.")
}

export function AddDeploymentInteractionPanel({
  deploymentId,
  onChanged,
  onCancel,
}: {
  deploymentId: string
  onChanged: () => void
  onCancel: () => void
}) {
  const [items, setItems] = useState<InteractionDefinitionSummaryDto[]>([])
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(50)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [loadError, setLoadError] = useState<ApiError | null>(null)
  const [actionError, setActionError] = useState<ApiError | null>(null)
  const [draftSearch, setDraftSearch] = useState("")
  const [draftProtocol, setDraftProtocol] = useState("")
  const [search, setSearch] = useState("")
  const [protocol, setProtocol] = useState("")
  const [reloadToken, setReloadToken] = useState(0)

  useEffect(() => {
    let active = true
    setLoading(true)
    setLoadError(null)
    void listAvailableInteractions({
      applicationDeploymentId: deploymentId,
      page,
      search,
      protocol,
    })
      .then((result) => {
        if (!active) return
        setItems(result.items)
        setPageSize(result.pageSize)
        setTotal(result.total)
      })
      .catch((caught) => {
        if (active) setLoadError(errorFrom(caught))
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [deploymentId, page, search, protocol, reloadToken])

  function toggle(interactionId: string) {
    setSelected((current) => {
      const next = new Set(current)
      if (next.has(interactionId)) next.delete(interactionId)
      else next.add(interactionId)
      return next
    })
  }

  async function addSelected() {
    if (selected.size === 0) return
    setSaving(true)
    setActionError(null)
    try {
      for (const interactionId of selected) {
        await selectDeploymentInteraction(deploymentId, interactionId)
      }
      onChanged()
      onCancel()
    } catch (caught) {
      setActionError(errorFrom(caught))
      setSelected(new Set())
      setReloadToken((value) => value + 1)
      onChanged()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="border-b border-[#E2E8F0] bg-[#F8FAFC]">
      <div className="flex items-center justify-between px-5 py-4">
        <div>
          <h3 className="font-semibold text-[#172033]">Add interaction</h3>
          <p className="mt-1 text-xs text-[#64748B]">Select Interaction Definitions already owned by this Application Definition.</p>
        </div>
        <Button variant="ghost" onClick={onCancel}>Close</Button>
      </div>

      <form
        className="grid gap-2 border-y border-[#E2E8F0] bg-white p-4 sm:grid-cols-[minmax(14rem,1fr)_10rem_auto]"
        onSubmit={(event) => {
          event.preventDefault()
          setPage(1)
          setSelected(new Set())
          setActionError(null)
          setSearch(draftSearch.trim())
          setProtocol(draftProtocol.trim())
        }}
      >
        <div className="relative min-w-0">
          <Search className="pointer-events-none absolute left-3 top-3 size-4 text-[#94A3B8]" aria-hidden="true" />
          <input className={`${inputClass} w-full pl-9`} value={draftSearch} onChange={(event) => setDraftSearch(event.target.value)} placeholder="Search interactions" aria-label="Search interactions" />
        </div>
        <input className={inputClass} value={draftProtocol} onChange={(event) => setDraftProtocol(event.target.value)} placeholder="Protocol" aria-label="Protocol" />
        <Button type="submit" variant="secondary">Apply</Button>
      </form>

      {actionError ? (
        <div className="border-b border-red-200 bg-red-50 px-5 py-3 text-sm text-red-700">
          {actionError.message} Server state has been refreshed; already completed selections remain applied.
        </div>
      ) : null}

      {loading ? (
        <div className="p-6 text-sm text-[#64748B]">Loading available interactions…</div>
      ) : loadError ? (
        <div className="p-6 text-sm text-red-700">{loadError.message}</div>
      ) : items.length === 0 ? (
        <div className="p-6 text-sm text-[#64748B]">No additional interactions are available.</div>
      ) : (
        <div className="overflow-x-auto bg-white">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="bg-[#F8FAFC] text-xs font-semibold uppercase tracking-wide text-[#64748B]">
              <tr><th className="w-16 px-5 py-3">Use</th><th className="px-5 py-3">Source</th><th className="px-5 py-3">Destination</th><th className="px-5 py-3">Traffic</th></tr>
            </thead>
            <tbody className="divide-y divide-[#E2E8F0]">
              {items.map((item) => (
                <tr key={item.interactionDefinitionId}>
                  <td className="px-5 py-3"><input type="checkbox" checked={selected.has(item.interactionDefinitionId)} onChange={() => toggle(item.interactionDefinitionId)} aria-label={`Select ${item.sourceComponentName} to ${item.destinationComponentName}`} /></td>
                  <td className="px-5 py-3 font-semibold text-[#172033]">{item.sourceComponentName}</td>
                  <td className="px-5 py-3 font-semibold text-[#172033]">{item.destinationComponentName}</td>
                  <td className="px-5 py-3 text-[#475569]">{trafficSummary(item.trafficAlternatives)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loading && !loadError ? <CataloguePager page={page} pageSize={pageSize} total={total} onPageChange={(next) => { setSelected(new Set()); setPage(next) }} /> : null}
      <div className="flex justify-end gap-2 border-t border-[#E2E8F0] px-5 py-4">
        <Button variant="secondary" onClick={onCancel}>Cancel</Button>
        <Button loading={saving} disabled={selected.size === 0} onClick={() => void addSelected()}>Add selected</Button>
      </div>
    </div>
  )
}
