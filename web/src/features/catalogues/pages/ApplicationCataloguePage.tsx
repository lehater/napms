import { useEffect, useState } from "react"
import { ChevronRight, Plus } from "lucide-react"

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
import { Input } from "@/design-system/components/Field"
import { EmptyState, ErrorState, LoadingState } from "@/design-system/components/PageState"
import { SearchInput } from "@/design-system/components/SearchInput"
import { PageTab, PageTabs } from "@/design-system/layout/PageTabs"
import {
  CatalogueFilterBar,
  CatalogueFilterField,
  CataloguePage,
  CataloguePaginationControls,
  CatalogueSurface,
  CatalogueToolbar,
} from "@/design-system/patterns/catalogue/CataloguePage"
import {
  listApplicationDefinitions,
  listApplicationDeployments,
  type ApplicationDefinitionSummaryDto,
  type ApplicationDeploymentSummaryDto,
} from "@/features/catalogues/api/targetCatalogue"
import { CreateDefinitionPanel } from "@/features/catalogues/components/TargetCatalogueForms"
import { ApiError } from "@/lib/api"

export type ApplicationCatalogueView = "definitions" | "deployments"

type Filters = {
  search: string
  first: string
  second: string
  third: string
}

const EMPTY_FILTERS: Filters = { search: "", first: "", second: "", third: "" }

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError
    ? caught
    : new ApiError(500, "InternalError", fallback)
}

export function ApplicationCataloguePage({
  view,
  page,
  onViewChange,
  onPageChange,
  onOpenDefinition,
  onOpenDeployment,
}: {
  view: ApplicationCatalogueView
  page: number
  onViewChange: (view: ApplicationCatalogueView) => void
  onPageChange: (page: number) => void
  onOpenDefinition: (applicationId: string) => void
  onOpenDeployment: (deploymentId: string) => void
}) {
  const [definitions, setDefinitions] = useState<ApplicationDefinitionSummaryDto[]>([])
  const [deployments, setDeployments] = useState<ApplicationDeploymentSummaryDto[]>([])
  const [total, setTotal] = useState(0)
  const [pageSize, setPageSize] = useState(50)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)
  const [draft, setDraft] = useState<Filters>(EMPTY_FILTERS)
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS)
  const [showCreate, setShowCreate] = useState(false)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      if (view === "definitions") {
        const result = await listApplicationDefinitions({
          page,
          pageSize,
          search: filters.search,
          domain: filters.first,
          ownerReference: filters.second,
          sort: "name",
        })
        setDefinitions(result.items)
        setDeployments([])
        setTotal(result.total)
      } else {
        const result = await listApplicationDeployments({
          page,
          pageSize,
          search: filters.search,
          companyReference: filters.first,
          environment: filters.second,
          scopeReference: filters.third,
          sort: "application",
        })
        setDefinitions([])
        setDeployments(result.items)
        setTotal(result.total)
      }
    } catch (caught) {
      setError(errorFrom(caught, "Application Catalogue could not be loaded."))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [view, page, pageSize, filters])

  function switchView(next: ApplicationCatalogueView) {
    setDraft(EMPTY_FILTERS)
    setFilters(EMPTY_FILTERS)
    setShowCreate(false)
    setPageSize(50)
    onViewChange(next)
  }

  function changeDraft(field: keyof Filters, value: string) {
    setDraft((current) => ({ ...current, [field]: value }))
  }

  function applyFilters(event: React.FormEvent) {
    event.preventDefault()
    if (page !== 1) onPageChange(1)
    setFilters({
      search: draft.search.trim(),
      first: draft.first.trim(),
      second: draft.second.trim(),
      third: draft.third.trim(),
    })
  }

  return (
    <CataloguePage
      title="Applications"
      description="Define applications and inspect their deployed instances."
      actions={view === "definitions" ? (
        <Button onClick={() => setShowCreate((value) => !value)}>
          <Plus className="size-[var(--napms-icon-size-control)]" aria-hidden="true" />
          Add application
        </Button>
      ) : undefined}
    >
      <PageTabs>
        <PageTab active={view === "definitions"} onClick={() => switchView("definitions")}>Definitions</PageTab>
        <PageTab active={view === "deployments"} onClick={() => switchView("deployments")}>Deployments</PageTab>
      </PageTabs>

      {showCreate && view === "definitions" ? (
        <CreateDefinitionPanel
          onCancel={() => setShowCreate(false)}
          onCreated={(definition) => {
            setShowCreate(false)
            onOpenDefinition(definition.applicationId)
          }}
        />
      ) : null}

      <CatalogueSurface>
        <form onSubmit={applyFilters}>
          <CatalogueToolbar>
            <SearchInput
              value={draft.search}
              onChange={(event) => changeDraft("search", event.target.value)}
              placeholder={view === "definitions" ? "Search definitions" : "Search deployments"}
              aria-label="Search applications"
            />
            <CatalogueFilterBar>
              {view === "definitions" ? (
                <>
                  <CatalogueFilterField label="Domain" className="xl:w-[190px]">
                    <Input value={draft.first} onChange={(event) => changeDraft("first", event.target.value)} aria-label="Domain" />
                  </CatalogueFilterField>
                  <CatalogueFilterField label="Owner" className="xl:w-[190px]">
                    <Input value={draft.second} onChange={(event) => changeDraft("second", event.target.value)} aria-label="Owner" />
                  </CatalogueFilterField>
                </>
              ) : (
                <>
                  <CatalogueFilterField label="Company" className="xl:w-[190px]">
                    <Input value={draft.first} onChange={(event) => changeDraft("first", event.target.value)} aria-label="Company" />
                  </CatalogueFilterField>
                  <CatalogueFilterField label="Environment" className="xl:w-[190px]">
                    <Input value={draft.second} onChange={(event) => changeDraft("second", event.target.value)} aria-label="Environment" />
                  </CatalogueFilterField>
                  <CatalogueFilterField label="Scope" className="xl:w-[190px]">
                    <Input value={draft.third} onChange={(event) => changeDraft("third", event.target.value)} aria-label="Scope" />
                  </CatalogueFilterField>
                </>
              )}
              <Button type="submit" variant="secondary" size="sm" className="xl:ml-auto">Apply</Button>
            </CatalogueFilterBar>
          </CatalogueToolbar>
        </form>

        {loading ? (
          <LoadingState>Loading applications…</LoadingState>
        ) : error ? (
          <ErrorState message={error.message} onRetry={() => void load()} />
        ) : view === "definitions" ? (
          definitions.length === 0 ? (
            <EmptyState title="No application definitions" description="Change the filters or add an application." />
          ) : (
            <DataTable width="compact">
              <DataTableHeader>
                <DataTableHeaderRow>
                  <DataTableHeadCell>Name</DataTableHeadCell>
                  <DataTableHeadCell>Domain</DataTableHeadCell>
                  <DataTableHeadCell className="text-right">Components</DataTableHeadCell>
                  <DataTableHeadCell className="text-right">Interactions</DataTableHeadCell>
                  <DataTableHeadCell className="text-right">Deployments</DataTableHeadCell>
                  <DataTableHeadCell className="w-10" />
                </DataTableHeaderRow>
              </DataTableHeader>
              <DataTableBody>
                {definitions.map((item) => (
                  <DataTableRow key={item.applicationId} onClick={() => onOpenDefinition(item.applicationId)}>
                    <DataTableCell className="font-semibold text-[var(--napms-color-text-primary)]">{item.displayName}</DataTableCell>
                    <DataTableCell className="text-[var(--napms-color-text-body)]">{item.domain ?? "—"}</DataTableCell>
                    <DataTableCell className="text-right tabular-nums">{item.componentCount}</DataTableCell>
                    <DataTableCell className="text-right tabular-nums">{item.interactionCount}</DataTableCell>
                    <DataTableCell className="text-right tabular-nums">{item.deploymentCount}</DataTableCell>
                    <DataTableCell><ChevronRight className="size-4 text-[var(--napms-color-text-muted)]" aria-hidden="true" /></DataTableCell>
                  </DataTableRow>
                ))}
              </DataTableBody>
            </DataTable>
          )
        ) : deployments.length === 0 ? (
          <EmptyState title="No application deployments" description="Change the filters or create a deployment from an application definition." />
        ) : (
          <DataTable width="standard">
            <DataTableHeader>
              <DataTableHeaderRow>
                <DataTableHeadCell>Application</DataTableHeadCell>
                <DataTableHeadCell>Company</DataTableHeadCell>
                <DataTableHeadCell>Environment</DataTableHeadCell>
                <DataTableHeadCell>Scope</DataTableHeadCell>
                <DataTableHeadCell className="text-right">Interactions</DataTableHeadCell>
                <DataTableHeadCell className="w-10" />
              </DataTableHeaderRow>
            </DataTableHeader>
            <DataTableBody>
              {deployments.map((item) => (
                <DataTableRow key={item.applicationDeploymentId} onClick={() => onOpenDeployment(item.applicationDeploymentId)}>
                  <DataTableCell className="font-semibold text-[var(--napms-color-text-primary)]">{item.applicationName}</DataTableCell>
                  <DataTableCell>{item.companyReference}</DataTableCell>
                  <DataTableCell>{item.environment}</DataTableCell>
                  <DataTableCell>{item.scopeReference}</DataTableCell>
                  <DataTableCell className="text-right tabular-nums">{item.selectedInteractionCount} / {item.definedInteractionCount}</DataTableCell>
                  <DataTableCell><ChevronRight className="size-4 text-[var(--napms-color-text-muted)]" aria-hidden="true" /></DataTableCell>
                </DataTableRow>
              ))}
            </DataTableBody>
          </DataTable>
        )}

        {!loading && !error ? (
          <CataloguePaginationControls
            page={page}
            pageSize={pageSize}
            total={total}
            disabled={loading}
            onPageChange={onPageChange}
            onPageSizeChange={(nextPageSize) => {
              setPageSize(nextPageSize)
              if (page !== 1) onPageChange(1)
            }}
          />
        ) : null}
      </CatalogueSurface>
    </CataloguePage>
  )
}
