import { useEffect, useState } from "react"
import { Plus } from "lucide-react"

import { Button } from "@/design-system/components/Button"
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
import { CatalogueLifecycleStatus } from "@/features/catalogues/components/CatalogueLifecycleStatus"
import { CreateApplicationDialog } from "@/features/catalogues/components/CreateApplicationDialog"
import { ApiError } from "@/lib/api"

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError
    ? caught
    : new ApiError(500, "InternalError", fallback)
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

  async function createApplication(displayName: string) {
    try {
      const created = await createCatalogueApplication(displayName)
      onOpenApplication(created.applicationId)
      return null
    } catch (caught) {
      return errorFrom(caught, "Application could not be created.").message
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
                    <CatalogueLifecycleStatus value={item.lifecycle} />
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

      <CreateApplicationDialog
        open={showCreate}
        onClose={() => setShowCreate(false)}
        onCreate={createApplication}
      />
    </CataloguePage>
  )
}
