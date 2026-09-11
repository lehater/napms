import { useEffect, useState } from "react"
import { ArrowLeft } from "lucide-react"

import { ErrorState, LoadingState } from "@/design-system/components/PageState"
import { StatusIndicator } from "@/design-system/components/StatusIndicator"
import { PageWorkspace } from "@/design-system/layout/PageWorkspace"
import { readCatalogueResource, type ResourceDetailDto } from "@/features/catalogues/api/catalogue"
import { readCatalogueResourceHistory, type ResourceHistoryDto } from "@/features/catalogues/api/resourceHistory"
import { shortId } from "@/features/catalogues/components/CatalogueIdentity"
import { ResourceLifecycleActions, ResourceOverviewEditors } from "@/features/catalogues/components/ResourceEditors"
import {
  ResourceBasicInformation,
  ResourceHistorySection,
  ResourceTechnicalDetails,
} from "@/features/catalogues/components/ResourceDetailSections"
import { ApiError } from "@/lib/api"

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError ? caught : new ApiError(500, "InternalError", fallback)
}

export function ResourceDetailsPage({
  resourceReference,
  onBack,
}: {
  resourceReference: string
  onBack: () => void
}) {
  const [detail, setDetail] = useState<ResourceDetailDto | null>(null)
  const [history, setHistory] = useState<ResourceHistoryDto | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)
  const [tab, setTab] = useState<"overview" | "history" | "technical">("overview")

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const [nextDetail, nextHistory] = await Promise.all([
        readCatalogueResource(resourceReference),
        readCatalogueResourceHistory(resourceReference),
      ])
      setDetail(nextDetail)
      setHistory(nextHistory)
    } catch (caught) {
      setError(errorFrom(caught, "Resource details could not be loaded."))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { void load() }, [resourceReference])

  if (loading && detail === null) return <LoadingState>Loading resource…</LoadingState>
  if (error && detail === null) return <ErrorState message={error.message} onRetry={() => void load()} />
  if (!detail) return null

  const resourceActive = detail.resource.lifecycle === "Active"
  const currentName = detail.resource.displayName || shortId(detail.resource.resourceReference)

  return (
    <PageWorkspace>
      <header className="grid gap-3 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-start">
        <div>
          <button type="button" className="mb-2 inline-flex items-center gap-1.5 text-xs font-medium text-[var(--napms-color-primary)] hover:underline" onClick={onBack}>
            <ArrowLeft className="size-3.5" aria-hidden="true" />Back to resources
          </button>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="truncate text-xl font-semibold text-[var(--napms-color-text-primary)]">{currentName}</h1>
            <StatusIndicator tone={resourceActive ? "positive" : "critical"}>{detail.resource.lifecycle}</StatusIndicator>
          </div>
          <div className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">Resource reference: <span className="font-mono">{detail.resource.resourceReference}</span></div>
        </div>
        <ResourceLifecycleActions detail={detail} onChanged={load} />
      </header>

      <div className="flex gap-6 border-b border-[var(--napms-color-border)] text-sm">
        {(["overview", "history", "technical"] as const).map((value) => (
          <button key={value} type="button" className={tab === value ? "border-b-2 border-[var(--napms-color-primary)] px-1 pb-2 font-semibold text-[var(--napms-color-primary)]" : "px-1 pb-2 text-[var(--napms-color-text-secondary)]"} onClick={() => setTab(value)}>
            {value === "overview" ? "Overview" : value === "history" ? "History" : "Technical details"}
          </button>
        ))}
      </div>

      {tab === "overview" ? (
        <div className="grid min-w-0 gap-4 xl:grid-cols-2">
          <div className="grid content-start gap-4"><ResourceBasicInformation detail={detail} /><ResourceOverviewEditors detail={detail} resourceReference={resourceReference} onChanged={load} /></div>
        </div>
      ) : null}
      {tab === "history" ? <ResourceHistorySection history={history} /> : null}
      {tab === "technical" ? <ResourceTechnicalDetails detail={detail} /> : null}
    </PageWorkspace>
  )
}
