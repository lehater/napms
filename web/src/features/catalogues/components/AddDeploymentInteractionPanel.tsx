import { useEffect, useState } from "react"

import { Button } from "@/design-system/components/Button"
import { Checkbox } from "@/design-system/components/Checkbox"
import {
  DataTable,
  DataTableBody,
  DataTableCell,
  DataTableHeadCell,
  DataTableHeader,
  DataTableHeaderRow,
  DataTableRow,
} from "@/design-system/components/DataTable"
import { Input } from "@/design-system/components/Field"
import { EmptyState, ErrorState, LoadingState } from "@/design-system/components/PageState"
import { SearchInput } from "@/design-system/components/SearchInput"
import {
  CatalogueFilterBar,
  CatalogueFilterField,
  CataloguePaginationControls,
  CatalogueToolbar,
} from "@/design-system/patterns/catalogue/CataloguePage"
import {
  listAvailableInteractions,
  selectDeploymentInteraction,
  type InteractionDefinitionSummaryDto,
} from "@/features/catalogues/api/targetCatalogue"
import { trafficSummary } from "@/features/catalogues/model/targetPresentation"
import { ApiError } from "@/lib/api"

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
      pageSize,
      search,
      protocol,
    })
      .then((result) => {
        if (!active) return
        setItems(result.items)
        setTotal(result.total)
      })
      .catch((caught) => { if (active) setLoadError(errorFrom(caught)) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [deploymentId, page, pageSize, search, protocol, reloadToken])

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
    <div className="my-3 grid gap-4 rounded-[var(--napms-control-radius)] bg-[var(--napms-color-surface-subtle)] p-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="font-semibold text-[var(--napms-color-text-primary)]">Add interaction</h3>
          <p className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">Select Interaction Definitions already owned by this Application Definition.</p>
        </div>
        <Button variant="ghost" size="sm" onClick={onCancel}>Close</Button>
      </div>

      <form
        onSubmit={(event) => {
          event.preventDefault()
          setPage(1)
          setSelected(new Set())
          setActionError(null)
          setSearch(draftSearch.trim())
          setProtocol(draftProtocol.trim())
        }}
      >
        <CatalogueToolbar>
          <SearchInput value={draftSearch} onChange={(event) => setDraftSearch(event.target.value)} placeholder="Search interactions" aria-label="Search interactions" />
          <CatalogueFilterBar>
            <CatalogueFilterField label="Protocol" className="xl:w-[190px]">
              <Input value={draftProtocol} onChange={(event) => setDraftProtocol(event.target.value)} aria-label="Protocol" />
            </CatalogueFilterField>
            <Button type="submit" variant="secondary" size="sm" className="xl:ml-auto">Apply</Button>
          </CatalogueFilterBar>
        </CatalogueToolbar>
      </form>

      {actionError ? (
        <div className="rounded-[var(--napms-control-radius)] border border-[var(--napms-color-danger-dot)] bg-[var(--napms-color-danger-bg)] px-4 py-3 text-sm text-[var(--napms-color-danger)]">
          {actionError.message} Server state has been refreshed; already completed selections remain applied.
        </div>
      ) : null}

      {loading ? (
        <LoadingState>Loading available interactions…</LoadingState>
      ) : loadError ? (
        <ErrorState message={loadError.message} />
      ) : items.length === 0 ? (
        <EmptyState title="No additional interactions are available" />
      ) : (
        <DataTable minWidth={760}>
          <DataTableHeader>
            <DataTableHeaderRow>
              <DataTableHeadCell className="w-16">Use</DataTableHeadCell>
              <DataTableHeadCell>Source</DataTableHeadCell>
              <DataTableHeadCell>Destination</DataTableHeadCell>
              <DataTableHeadCell>Traffic</DataTableHeadCell>
            </DataTableHeaderRow>
          </DataTableHeader>
          <DataTableBody>
            {items.map((item) => (
              <DataTableRow key={item.interactionDefinitionId}>
                <DataTableCell>
                  <Checkbox
                    checked={selected.has(item.interactionDefinitionId)}
                    onChange={() => toggle(item.interactionDefinitionId)}
                    aria-label={`Select ${item.sourceComponentName} to ${item.destinationComponentName}`}
                  />
                </DataTableCell>
                <DataTableCell className="font-semibold text-[var(--napms-color-text-primary)]">{item.sourceComponentName}</DataTableCell>
                <DataTableCell className="font-semibold text-[var(--napms-color-text-primary)]">{item.destinationComponentName}</DataTableCell>
                <DataTableCell>{trafficSummary(item.trafficAlternatives)}</DataTableCell>
              </DataTableRow>
            ))}
          </DataTableBody>
        </DataTable>
      )}

      {!loading && !loadError ? (
        <CataloguePaginationControls
          page={page}
          pageSize={pageSize}
          total={total}
          onPageChange={(next) => { setSelected(new Set()); setPage(next) }}
          onPageSizeChange={(nextPageSize) => { setSelected(new Set()); setPageSize(nextPageSize); setPage(1) }}
        />
      ) : null}
      <div className="flex justify-end gap-2 border-t border-[var(--napms-color-border)] pt-4">
        <Button variant="secondary" onClick={onCancel}>Cancel</Button>
        <Button loading={saving} disabled={selected.size === 0} onClick={() => void addSelected()}>Add selected</Button>
      </div>
    </div>
  )
}
