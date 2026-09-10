import { useEffect, useState } from "react"

import { ApiError } from "@/api"
import { Button } from "@/components/ui/Button"
import { CataloguePager } from "@/features/catalogues/CataloguePager"
import type {
  DependencyGroupDto,
  DependencyReferenceDto,
} from "@/features/catalogues/targetCatalogueCommands"
import {
  listRetirementDependencyPage,
  type RetirementSubjectPath,
} from "@/features/catalogues/targetCatalogueDependencies"

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
    })
      .then((result) => {
        if (!active) return
        setItems(result.items)
        setPageSize(result.pageSize)
        setTotal(result.total)
      })
      .catch((caught) => {
        if (active) {
          setError(
            caught instanceof ApiError
              ? caught
              : new ApiError(500, "InternalError", "Dependencies could not be loaded."),
          )
        }
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [selectedKind, subjectKind, subjectId, page])

  const drillable = Boolean(subjectKind && subjectId)

  return (
    <div className="rounded-lg border border-amber-300 bg-amber-50 p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="font-semibold text-amber-950">Action blocked by active references</h3>
          <p className="mt-1 text-sm text-amber-900">
            Resolve or retire the listed dependants before retrying this catalogue change.
          </p>
        </div>
        <Button variant="ghost" onClick={onClose}>Close</Button>
      </div>

      <div className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {groups.map((group) => (
          <button
            key={group.kind}
            type="button"
            disabled={!drillable}
            className={`rounded-md border border-amber-200 bg-white px-4 py-3 text-left ${drillable ? "hover:border-amber-400" : "cursor-default"}`}
            onClick={() => {
              if (!drillable) return
              setPage(1)
              setSelectedKind(group.kind)
            }}
          >
            <div className="text-xs font-semibold uppercase tracking-wide text-amber-800">{displayKind(group.kind)}</div>
            <div className="mt-1 text-2xl font-bold tabular-nums text-amber-950">{group.count}</div>
          </button>
        ))}
      </div>

      {!drillable ? (
        <div className="mt-4 grid gap-3">
          {groups.flatMap((group) =>
            group.preview.map((item) => (
              <div key={`${group.kind}:${item.reference}`} className="rounded-md border border-amber-200 bg-white px-4 py-2 text-sm text-[#475569]">
                {item.displayName ?? item.reference}
              </div>
            )),
          )}
        </div>
      ) : selectedKind ? (
        <div className="mt-5 overflow-hidden rounded-md border border-amber-200 bg-white">
          <div className="border-b border-amber-100 px-4 py-3 text-sm font-semibold text-amber-950">
            {displayKind(selectedKind)}
          </div>
          {loading ? (
            <div className="p-4 text-sm text-[#64748B]">Loading references…</div>
          ) : error ? (
            <div className="p-4 text-sm text-red-700">{error.message}</div>
          ) : items.length === 0 ? (
            <div className="p-4 text-sm text-[#64748B]">No active references remain.</div>
          ) : (
            <div className="divide-y divide-[#E2E8F0]">
              {items.map((item) => (
                <div key={item.reference} className="px-4 py-3 text-sm text-[#475569]">
                  {item.displayName ?? item.reference}
                </div>
              ))}
            </div>
          )}
          {!loading && !error ? (
            <CataloguePager page={page} pageSize={pageSize} total={total} onPageChange={setPage} />
          ) : null}
        </div>
      ) : null}
    </div>
  )
}
