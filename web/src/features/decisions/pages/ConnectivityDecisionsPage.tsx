import { useEffect, useState } from "react"

import { Button } from "@/design-system/components/Button"
import { EmptyState, ErrorState, LoadingState } from "@/design-system/components/PageState"
import { PageHeader } from "@/design-system/layout/PageHeader"
import { PageWorkspace } from "@/design-system/layout/PageWorkspace"
import { ListPagination } from "@/design-system/patterns/list/ListPage"
import { Surface } from "@/design-system/primitives/Surface"
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
  const [listState, setListState] = useState<DecisionListState>(() => ({ page, refreshGeneration: 0, loading: true, decisions: [], hasMore: false, ambiguousReadScopes: [], error: null }))

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

  const current = listState.page === page && listState.refreshGeneration === listRefreshGeneration
  const visibleDecisions = current ? listState.decisions : []
  const visibleHasMore = current ? listState.hasMore : false
  const visibleAmbiguousReadScopes = current ? listState.ambiguousReadScopes : []
  const visibleListError = current ? listState.error : null
  const visibleLoadingList = !current || listState.loading

  return (
    <PageWorkspace>
      <PageHeader title="Decisions" description="Inspect final Connectivity Decisions visible through independent read authority, or record a final Allowed / NotAllowed result for an exact ACC-backed subject admitted by DecideConnectivity." />
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_460px]">
        <Surface className="min-w-0 overflow-hidden">
          <div className="border-b border-[var(--napms-color-border)] px-5 py-4">
            <h2 className="text-base font-semibold text-[var(--napms-color-text-primary)]">Visible final Decisions</h2>
            <p className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">Page {page}</p>
          </div>
          {visibleAmbiguousReadScopes.length > 0 ? <div className="m-4 rounded-[var(--napms-control-radius)] border border-[var(--napms-color-warning-dot)] bg-[var(--napms-color-warning-bg)] p-3 text-sm text-[var(--napms-color-warning)]">{visibleAmbiguousReadScopes.length} read scope(s) are ambiguous and remain fail-closed. Decisions from those scopes are not exposed.</div> : null}
          {visibleListError ? <div className="m-4"><ErrorState message={`${visibleListError.code}: ${visibleListError.message}`} /></div> : null}
          {visibleLoadingList ? <LoadingState>Loading Decisions…</LoadingState> : visibleDecisions.length === 0 ? <EmptyState title="No visible Connectivity Decisions" description="No Decisions are visible through the current read-authority result. Decide authority is evaluated separately in the record form." /> : <DecisionsTable decisions={visibleDecisions} onOpenDecision={onOpenDecision} />}
          <ListPagination>
            <span className="text-xs text-[var(--napms-color-text-secondary)]">Page {page}</span>
            <div className="flex gap-2">
              <Button variant="secondary" size="sm" disabled={page === 1 || visibleLoadingList} onClick={() => onPageChange(Math.max(1, page - 1))}>Previous</Button>
              <Button variant="secondary" size="sm" disabled={!visibleHasMore || visibleLoadingList} onClick={() => onPageChange(page + 1)}>Next</Button>
            </div>
          </ListPagination>
        </Surface>
        <DecisionRecordingPanel onRecorded={() => setListRefreshGeneration((currentGeneration) => currentGeneration + 1)} />
      </div>
    </PageWorkspace>
  )
}
