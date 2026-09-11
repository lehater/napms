import { useEffect, useState } from "react"

import { Button } from "@/design-system/components/Button"
import { Field, Input } from "@/design-system/components/Field"
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
    <div className="mx-auto max-w-[1380px]">
      <header className="mb-6">
        <div className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#64748B]">Connectivity Needs</div>
        <h1 className="text-[28px] font-bold tracking-tight text-[#172033]">My Connectivity Needs</h1>
        <p className="mt-2 max-w-4xl text-sm text-[#64748B]">Declare semantic connectivity that is required. A Requirement records need only: it does not mean the connection is Allowed, authorized by Access Policy, or configured.</p>
      </header>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_430px]">
        <section className="overflow-hidden rounded-lg border border-[#E2E8F0] bg-white">
          <div className="flex flex-wrap items-end justify-between gap-4 border-b border-[#E2E8F0] px-5 py-4">
            <div><h2 className="text-base font-semibold text-[#172033]">Visible Connectivity Requirements</h2><p className="mt-1 text-xs text-[#64748B]">Page {page}</p></div>
            <Field label="Policy coverage as of" hint="Same logical time is used for Requirement applicability and Rule effectiveness."><Input type="datetime-local" step="1" value={alignmentAsOf} onChange={(event) => setAlignmentAsOf(event.target.value)} /></Field>
          </div>
          {ambiguousReadScopes.length > 0 ? <div className="m-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">{ambiguousReadScopes.length} scope(s) have ambiguous read authority and remain fail-closed.</div> : null}
          {listError ? <div className="m-4 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800"><div className="font-semibold">{listError.code}</div><div className="mt-1">{listError.message}</div></div> : null}
          {alignmentError ? <div className="m-4 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800"><div className="font-semibold">{alignmentError.code}</div><div className="mt-1">{alignmentError.message}</div></div> : null}
          {loadingList ? <div className="p-8 text-sm text-[#64748B]">Loading Requirements…</div> : requirements.length === 0 ? <div className="p-10 text-center"><div className="text-sm font-semibold text-[#334155]">No visible Connectivity Requirements</div><div className="mt-2 text-sm text-[#64748B]">Declare the first semantic connectivity need from the form.</div></div> : <RequirementsTable requirements={requirements} alignmentById={alignmentById} loadingAlignment={loadingAlignment} onOpenRequirement={onOpenRequirement} />}
          <div className="flex justify-end gap-2 border-t border-[#E2E8F0] px-5 py-4"><Button variant="secondary" disabled={page === 1 || loadingList} onClick={() => onPageChange(Math.max(1, page - 1))}>Previous</Button><Button variant="secondary" disabled={!hasMore || loadingList} onClick={() => onPageChange(page + 1)}>Next</Button></div>
        </section>
        <RequirementDeclarationPanel onDeclared={refreshAfterDeclaration} />
      </div>
    </div>
  )
}
