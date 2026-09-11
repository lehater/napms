import { useEffect, useState } from "react"
import { Plus, X } from "lucide-react"

import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Field"
import {
  DataTable,
  DataTableBody,
  DataTableCell,
  DataTableHeadCell,
  DataTableHeader,
  DataTableHeaderRow,
  DataTableRow,
} from "@/design-system/components/DataTable"
import { EmptyState, ErrorState, LoadingState } from "@/design-system/components/PageState"
import { SearchInput } from "@/design-system/components/SearchInput"
import { StatusIndicator } from "@/design-system/components/StatusIndicator"
import { PrimaryTableAction, ReferenceText } from "@/design-system/components/TableValue"
import {
  CataloguePage,
  CataloguePagination,
  CatalogueSurface,
  CatalogueToolbar,
} from "@/design-system/patterns/catalogue/CataloguePage"
import {
  createCatalogueApplication,
  listCatalogueApplications,
  type ApplicationDto,
} from "@/features/catalogues/api/catalogue"
import { shortId } from "@/features/catalogues/components/CatalogueIdentity"
import { ApiError } from "@/lib/api"

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError
    ? caught
    : new ApiError(500, "InternalError", fallback)
}

function LifecycleIndicator({ value }: { value: ApplicationDto["lifecycle"] }) {
  return (
    <StatusIndicator tone={value === "Active" ? "positive" : "critical"}>
      {value}
    </StatusIndicator>
  )
}

export function ApplicationsPage({
  page,
  onPageChange,
  onOpenApplication,
}: {
  page: number
  onPageChange: (page: number) => void
  onOpenApplication: (applicationId: string) => void
}) {
  const [items, setItems] = useState<ApplicationDto[]>([])
  const [hasMore, setHasMore] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)
  const [searchInput, setSearchInput] = useState("")
  const [search, setSearch] = useState("")

  const [showCreate, setShowCreate] = useState(false)
  const [displayName, setDisplayName] = useState("")
  const [creating, setCreating] = useState(false)
  const [createError, setCreateError] = useState<ApiError | null>(null)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const result = await listCatalogueApplications(page, search)
      setItems(result.items)
      setHasMore(result.hasMore)
    } catch (caught) {
      setError(errorFrom(caught, "Applications could not be loaded."))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [page, search])

  useEffect(() => {
    const nextSearch = searchInput.trim()
    if (nextSearch === search) return

    const timeout = window.setTimeout(() => {
      if (page !== 1) onPageChange(1)
      setSearch(nextSearch)
    }, 250)

    return () => window.clearTimeout(timeout)
  }, [page, search, searchInput, onPageChange])

  async function create(event: React.FormEvent) {
    event.preventDefault()
    const name = displayName.trim()
    if (!name) return

    setCreating(true)
    setCreateError(null)
    try {
      const created = await createCatalogueApplication(name)
      setDisplayName("")
      setShowCreate(false)
      onOpenApplication(created.applicationId)
    } catch (caught) {
      setCreateError(errorFrom(caught, "Application could not be created."))
    } finally {
      setCreating(false)
    }
  }

  function applySearch(event: React.FormEvent) {
    event.preventDefault()
    if (page !== 1) onPageChange(1)
    setSearch(searchInput.trim())
  }

  return (
    <CataloguePage
      title="Applications"
      description="Maintain application structure used by governed connectivity."
      actions={
        <Button onClick={() => setShowCreate(true)}>
          <Plus className="size-[var(--napms-icon-size-control)]" aria-hidden="true" />
          New application
        </Button>
      }
    >
      <CatalogueSurface>
        <form onSubmit={applySearch}>
          <CatalogueToolbar>
            <SearchInput
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder="Search applications by name or reference…"
              aria-label="Search applications"
            />
          </CatalogueToolbar>
        </form>

        {loading ? (
          <LoadingState>Loading applications…</LoadingState>
        ) : error ? (
          <ErrorState message={error.message} onRetry={() => void load()} />
        ) : items.length === 0 ? (
          <EmptyState
            title="No applications found"
            description="Change the search or create a new application."
          />
        ) : (
          <DataTable minWidth={760}>
            <colgroup>
              <col style={{ width: "48%" }} />
              <col style={{ width: "30%" }} />
              <col style={{ width: "22%" }} />
            </colgroup>
            <DataTableHeader>
              <DataTableHeaderRow>
                <DataTableHeadCell>Name</DataTableHeadCell>
                <DataTableHeadCell>Reference</DataTableHeadCell>
                <DataTableHeadCell>Lifecycle</DataTableHeadCell>
              </DataTableHeaderRow>
            </DataTableHeader>
            <DataTableBody>
              {items.map((item) => (
                <DataTableRow key={item.applicationId}>
                  <DataTableCell>
                    <PrimaryTableAction onClick={() => onOpenApplication(item.applicationId)}>
                      {item.displayName}
                    </PrimaryTableAction>
                  </DataTableCell>
                  <DataTableCell>
                    <ReferenceText>{shortId(item.applicationId)}</ReferenceText>
                  </DataTableCell>
                  <DataTableCell>
                    <LifecycleIndicator value={item.lifecycle} />
                  </DataTableCell>
                </DataTableRow>
              ))}
            </DataTableBody>
          </DataTable>
        )}

        <CataloguePagination>
          <span className="text-[11px] text-[var(--napms-color-text-secondary)]">
            Page {page} · up to 50 applications per page
          </span>
          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              size="sm"
              disabled={page <= 1 || loading}
              onClick={() => onPageChange(page - 1)}
            >
              Previous
            </Button>
            <span className="flex size-[var(--napms-control-height-sm)] items-center justify-center rounded-[var(--napms-control-radius)] border border-[var(--napms-color-primary-border)] bg-[var(--napms-color-primary-subtle)] text-[11px] font-semibold text-[var(--napms-color-primary-hover)]">
              {page}
            </span>
            <Button
              variant="secondary"
              size="sm"
              disabled={!hasMore || loading}
              onClick={() => onPageChange(page + 1)}
            >
              Next
            </Button>
          </div>
        </CataloguePagination>
      </CatalogueSurface>

      {showCreate ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/30 p-4"
          role="presentation"
          onMouseDown={(event) => {
            if (event.currentTarget === event.target && !creating) setShowCreate(false)
          }}
        >
          <div
            className="w-full max-w-[500px] overflow-hidden rounded-xl border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)] shadow-2xl"
            role="dialog"
            aria-modal="true"
            aria-labelledby="create-application-title"
          >
            <div className="flex min-h-[89px] items-start justify-between border-b border-[var(--napms-color-border)] px-7 py-6">
              <div>
                <h2
                  id="create-application-title"
                  className="text-lg font-semibold text-[var(--napms-color-text-primary)]"
                >
                  New application
                </h2>
                <p className="mt-1 text-sm text-[var(--napms-color-text-secondary)]">
                  Create the application identity first. Components and deployments are added from its workspace.
                </p>
              </div>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                aria-label="Close new application dialog"
                disabled={creating}
                onClick={() => setShowCreate(false)}
              >
                <X className="size-4" aria-hidden="true" />
              </Button>
            </div>

            <form className="grid gap-5 px-7 py-6" onSubmit={create}>
              <label className="grid gap-2 text-sm font-medium text-[var(--napms-color-text-body)]">
                Display name
                <Input
                  autoFocus
                  value={displayName}
                  onChange={(event) => setDisplayName(event.target.value)}
                  placeholder="Application name"
                  maxLength={256}
                  aria-label="Application name"
                />
              </label>

              {createError ? (
                <p className="text-sm text-[var(--napms-color-danger)]">{createError.message}</p>
              ) : null}

              <div className="flex justify-end gap-2 border-t border-[var(--napms-color-border)] pt-5">
                <Button
                  type="button"
                  variant="secondary"
                  disabled={creating}
                  onClick={() => setShowCreate(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" loading={creating} disabled={!displayName.trim()}>
                  Create application
                </Button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </CataloguePage>
  )
}
