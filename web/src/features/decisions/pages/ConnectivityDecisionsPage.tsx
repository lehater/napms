import { useEffect, useState } from "react"

import { Button } from "@/design-system/components/Button"
import {
  listConnectivityDecisions,
  type ConnectivityDecisionDto,
} from "@/features/decisions/api"
import { DecisionRecordingPanel } from "@/features/decisions/components/DecisionRecordingPanel"
import { DecisionsTable } from "@/features/decisions/components/DecisionsTable"
import { ApiError } from "@/lib/api"

type DecisionListState = {
  page: number
  refreshGeneration: number
  loading: boolean
  decisions: ConnectivityDecisionDto[]
  hasMore: boolean
  ambiguousReadScopes: string[]
  error: ApiError | null
}

export function ConnectivityDecisionsPage({
  page,
  onPageChange,
  onOpenDecision,
}: {
  page: number
  onPageChange: (page: number) => void
  onOpenDecision: (decisionId: string) => void
}) {
  const [listRefreshGeneration, setListRefreshGeneration] = useState(0)
  const [listState, setListState] = useState<DecisionListState>(() => ({
    page,
    refreshGeneration: 0,
    loading: true,
    decisions: [],
    hasMore: false,
    ambiguousReadScopes: [],
    error: null,
  }))

  useEffect(() => {
    const requestPage = page
    const requestRefreshGeneration = listRefreshGeneration
    let active = true
    setListState({ page: requestPage, refreshGeneration: requestRefreshGeneration, loading: true, decisions: [], hasMore: false, ambiguousReadScopes: [], error: null })
    void listConnectivityDecisions(requestPage)
      .then((result) => {
        if (!active) return
        setListState({ page: requestPage, refreshGeneration: requestRefreshGeneration, loading: false, decisions: result.items, hasMore: result.hasMore, ambiguousReadScopes: result.ambiguousScopes.map((item) => item.scope), error: null })
      })
      .catch((caught) => {
        if (!active) return
        setListState({ page: requestPage, refreshGeneration: requestRefreshGeneration, loading: false, decisions: [], hasMore: false, ambiguousReadScopes: [], error: caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Connectivity Decisions could not be loaded.") })
      })
    return () => { active = false }
  }, [page, listRefreshGeneration])

  const listStateIsCurrent = listState.page === page && listState.refreshGeneration === listRefreshGeneration
  const visibleDecisions = listStateIsCurrent ? listState.decisions : []
  const visibleHasMore = listStateIsCurrent ? listState.hasMore : false
  const visibleAmbiguousReadScopes = listStateIsCurrent ? listState.ambiguousReadScopes : []
  const visibleListError = listStateIsCurrent ? listState.error : null
  const visibleLoadingList = !listStateIsCurrent || listState.loading

  return (
    <div className="mx-auto max-w-[1440px]">
      <header className="mb-6">
        <div className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#64748B]">Connectivity Decisions</div>
        <h1 className="text-[28px] font-bold tracking-tight text-[#172033]">Decisions</h1>
        <p className="mt-2 max-w-4xl text-sm text-[#64748B]">Inspect final Connectivity Decisions visible through independent read authority, or record a final Allowed / NotAllowed result for an exact ACC-backed subject admitted by DecideConnectivity.</p>
      </header>
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_460px]">
        <section className="overflow-hidden rounded-lg border border-[#E2E8F0] bg-white">
          <div className="flex items-center justify-between gap-4 border-b border-[#E2E8F0] px-5 py-4"><div><h2 className="text-base font-semibold text-[#172033]">Visible final Decisions</h2><p className="mt-1 text-xs text-[#64748B]">Page {page}</p></div></div>
          {visibleAmbiguousReadScopes.length > 0 ? <div className="m-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">{visibleAmbiguousReadScopes.length} read scope(s) are ambiguous and remain fail-closed. Decisions from those scopes are not exposed.</div> : null}
          {visibleListError ? <div className="m-4 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800"><div className="font-semibold">{visibleListError.code}</div><div className="mt-1">{visibleListError.message}</div></div> : null}
          {visibleLoadingList ? <div className="p-8 text-sm text-[#64748B]">Loading Decisions…</div> : visibleDecisions.length === 0 ? <div className="p-10 text-center"><div className="text-sm font-semibold text-[#334155]">No visible Connectivity Decisions</div><div className="mt-2 text-sm text-[#64748B]">No Decisions are visible through the current read-authority result. Decide authority is evaluated separately in the record form.</div></div> : <DecisionsTable decisions={visibleDecisions} onOpenDecision={onOpenDecision} />}
          <div className="flex justify-end gap-2 border-t border-[#E2E8F0] px-5 py-4"><Button variant="secondary" disabled={page === 1 || visibleLoadingList} onClick={() => onPageChange(Math.max(1, page - 1))}>Previous</Button><Button variant="secondary" disabled={!visibleHasMore || visibleLoadingList} onClick={() => onPageChange(page + 1)}>Next</Button></div>
        </section>
        <DecisionRecordingPanel onRecorded={() => setListRefreshGeneration((current) => current + 1)} />
      </div>
    </div>
  )
}
