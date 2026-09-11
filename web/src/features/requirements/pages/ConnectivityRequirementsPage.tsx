import { useEffect, useState } from "react"

import { Button } from "@/design-system/components/Button"
import { Field, Input } from "@/design-system/components/Field"
import { EmptyState, ErrorState, LoadingState } from "@/design-system/components/PageState"
import { PageHeader } from "@/design-system/layout/PageHeader"
import { PageWorkspace } from "@/design-system/layout/PageWorkspace"
import { ListPagination } from "@/design-system/patterns/list/ListPage"
import { Surface } from "@/design-system/primitives/Surface"
import {
  listConnectivityRequirementAlignment,
  listConnectivityRequirements,
  type ConnectivityRequirementDto,
  type RequirementPolicyAlignmentStatus,
} from "@/features/requirements/api"
import { RequirementDeclarationPanel } from "@/features/requirements/components/RequirementDeclarationPanel"
import { RequirementsTable } from "@/features/requirements/components/RequirementsTable"
import { ApiError } from "@/lib/api"
import { nowLocalDateTimeInput, toOffsetAwareIso } from "@/lib/datetime"

export function ConnectivityRequirementsPage({
  page,
  onPageChange,
  onOpenRequirement,
}: {
  page: number
  onPageChange: (page: number) => void
  onOpenRequirement: (requirementId: string) => void
}) {
  const [requirements, setRequirements] = useState<ConnectivityRequirementDto[]>([])
  const [hasMore, setHasMore] = useState(false)
  const [ambiguousReadScopes, setAmbiguousReadScopes] = useState<string[]>([])
  const [loadingList, setLoadingList] = useState(true)
  const [listError, setListError] = useState<ApiError | null>(null)
  const [alignmentAsOf, setAlignmentAsOf] = useState(nowLocalDateTimeInput())
  const [alignmentById, setAlignmentById] = useState<Record<string, RequirementPolicyAlignmentStatus>>({})
  const [loadingAlignment, setLoadingAlignment] = useState(true)
  const [alignmentError, setAlignmentError] = useState<ApiError | null>(null)

  async function loadList() {
    setLoadingList(true)
    setListError(null)
    try {
      const result = await listConnectivityRequirements(page)
      setRequirements(result.items)
      setHasMore(result.hasMore)
      setAmbiguousReadScopes(result.ambiguousScopes.map((item) => item.scope))
    } catch (caught) {
      setListError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Connectivity Requirements could not be loaded."))
    } finally {
      setLoadingList(false)
    }
  }

  async function loadAlignment() {
    setLoadingAlignment(true)
    setAlignmentError(null)
    try {
      const result = await listConnectivityRequirementAlignment(toOffsetAwareIso(alignmentAsOf), page)
      setAlignmentById(Object.fromEntries(result.items.map((item) => [item.requirementId, item.status])))
    } catch (caught) {
      setAlignmentById({})
      setAlignmentError(caught instanceof ApiError ? caught : new ApiError(422, "InvalidAsOf", "Select a valid alignment date and time."))
    } finally {
      setLoadingAlignment(false)
    }
  }

  useEffect(() => { void loadList() }, [page])
  useEffect(() => { void loadAlignment() }, [page, alignmentAsOf])

  async function refreshAfterDeclaration() {
    await Promise.all([loadList(), loadAlignment()])
  }

  return (
    <PageWorkspace>
      <PageHeader
        title="My Connectivity Needs"
        description="Declare semantic connectivity that is required. A Requirement records need only: it does not mean the connection is Allowed, authorized by Access Policy, or configured."
      />

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_430px]">
        <Surface className="min-w-0 overflow-hidden">
          <div className="flex flex-wrap items-end justify-between gap-4 border-b border-[var(--napms-color-border)] px-5 py-4">
            <div>
              <h2 className="text-base font-semibold text-[var(--napms-color-text-primary)]">Visible Connectivity Requirements</h2>
              <p className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">Page {page}</p>
            </div>
            <Field label="Policy coverage as of" hint="Same logical time is used for Requirement applicability and Rule effectiveness.">
              <Input type="datetime-local" step="1" value={alignmentAsOf} onChange={(event) => setAlignmentAsOf(event.target.value)} />
            </Field>
          </div>
          {ambiguousReadScopes.length > 0 ? <div className="m-4 rounded-[var(--napms-control-radius)] border border-[var(--napms-color-warning-dot)] bg-[var(--napms-color-warning-bg)] p-3 text-sm text-[var(--napms-color-warning)]">{ambiguousReadScopes.length} scope(s) have ambiguous read authority and remain fail-closed.</div> : null}
          {listError ? <div className="m-4"><ErrorState message={`${listError.code}: ${listError.message}`} /></div> : null}
          {alignmentError ? <div className="m-4"><ErrorState message={`${alignmentError.code}: ${alignmentError.message}`} /></div> : null}
          {loadingList ? <LoadingState>Loading Requirements…</LoadingState> : requirements.length === 0 ? <EmptyState title="No visible Connectivity Requirements" description="Declare the first semantic connectivity need from the form." /> : <RequirementsTable requirements={requirements} alignmentById={alignmentById} loadingAlignment={loadingAlignment} onOpenRequirement={onOpenRequirement} />}
          <ListPagination>
            <span className="text-xs text-[var(--napms-color-text-secondary)]">Page {page}</span>
            <div className="flex gap-2">
              <Button variant="secondary" size="sm" disabled={page === 1 || loadingList} onClick={() => onPageChange(Math.max(1, page - 1))}>Previous</Button>
              <Button variant="secondary" size="sm" disabled={!hasMore || loadingList} onClick={() => onPageChange(page + 1)}>Next</Button>
            </div>
          </ListPagination>
        </Surface>
        <RequirementDeclarationPanel onDeclared={refreshAfterDeclaration} />
      </div>
    </PageWorkspace>
  )
}
