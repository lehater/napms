import { useEffect, useState } from "react"

import { Button } from "@/design-system/components/Button"
import { EmptyState, ErrorState, LoadingState } from "@/design-system/components/PageState"
import { CataloguePaginationControls } from "@/design-system/patterns/catalogue/CataloguePage"
import type {
  DependencyGroupDto,
  DependencyReferenceDto,
} from "@/features/catalogues/api/targetCommands"
import {
  listRetirementDependencyPage,
  type RetirementSubjectPath,
} from "@/features/catalogues/api/targetDependencies"
import { ApiError } from "@/lib/api"

function displayKind(kind: string) {
  return kind.replace(/([a-z])([A-Z])/g, "$1 $2")
}

export function DependencyBlockPanel({
  groups,
  subjectKind,
  subjectId,
  onClose,
}: {
  groups: DependencyGroupDto[]
  subjectKind?: RetirementSubjectPath
  subjectId?: string
  onClose: () => void
}) {
  const [selectedKind, setSelectedKind] = useState<string | null>(null)
  const [items, setItems] = useState<DependencyReferenceDto[]>([])
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(50)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)

  useEffect(() => {
    if (!selectedKind || !subjectKind || !subjectId) return
    let active = true
    setLoading(true)
    setError(null)
    void listRetirementDependencyPage({
      subjectKind,
      subjectId,
      dependencyKind: selectedKind,
      page,
      pageSize,
    })
      .then((result) => {
        if (!active) return
        setItems(result.items)
        setTotal(result.total)
      })
      .catch((caught) => {
        if (active) {
          setError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Dependencies could not be loaded."))
        }
      })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [selectedKind, subjectKind, subjectId, page, pageSize])

  const drillable = Boolean(subjectKind && subjectId)

  return (
    <div className="rounded-[var(--napms-surface-radius)] border border-[var(--napms-color-warning-dot)] bg-[var(--napms-color-warning-bg)] p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="font-semibold text-[var(--napms-color-warning)]">Action blocked by active references</h3>
          <p className="mt-1 text-sm text-[var(--napms-color-text-body)]">Resolve or retire the listed dependants before retrying this catalogue change.</p>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose}>Close</Button>
      </div>

      <div className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {groups.map((group) => (
          <button
            key={group.kind}
            type="button"
            disabled={!drillable}
            className={`rounded-[var(--napms-control-radius)] border border-[var(--napms-color-warning-dot)] bg-[var(--napms-color-surface)] px-4 py-3 text-left ${drillable ? "hover:border-[var(--napms-color-warning)]" : "cursor-default"}`}
            onClick={() => {
              if (!drillable) return
              setPage(1)
              setSelectedKind(group.kind)
            }}
          >
            <div className="text-xs font-semibold uppercase tracking-wide text-[var(--napms-color-warning)]">{displayKind(group.kind)}</div>
            <div className="mt-1 text-2xl font-bold tabular-nums text-[var(--napms-color-text-primary)]">{group.count}</div>
          </button>
        ))}
      </div>

      {!drillable ? (
        <div className="mt-4 grid gap-3">
          {groups.flatMap((group) => group.preview.map((item) => (
            <div key={`${group.kind}:${item.reference}`} className="rounded-[var(--napms-control-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)] px-4 py-2 text-sm text-[var(--napms-color-text-body)]">
              {item.displayName ?? item.reference}
            </div>
          )))}
        </div>
      ) : selectedKind ? (
        <div className="mt-5 overflow-hidden rounded-[var(--napms-control-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)]">
          <div className="border-b border-[var(--napms-color-border)] px-4 py-3 text-sm font-semibold text-[var(--napms-color-text-primary)]">{displayKind(selectedKind)}</div>
          {loading ? (
            <LoadingState>Loading references…</LoadingState>
          ) : error ? (
            <ErrorState message={error.message} />
          ) : items.length === 0 ? (
            <EmptyState title="No active references remain" />
          ) : (
            <div className="divide-y divide-[var(--napms-color-border)]">
              {items.map((item) => (
                <div key={item.reference} className="px-4 py-3 text-sm text-[var(--napms-color-text-body)]">{item.displayName ?? item.reference}</div>
              ))}
            </div>
          )}
          {!loading && !error ? (
            <CataloguePaginationControls
              page={page}
              pageSize={pageSize}
              total={total}
              onPageChange={setPage}
              onPageSizeChange={(nextPageSize) => { setPageSize(nextPageSize); setPage(1) }}
            />
          ) : null}
        </div>
      ) : null}
    </div>
  )
}
