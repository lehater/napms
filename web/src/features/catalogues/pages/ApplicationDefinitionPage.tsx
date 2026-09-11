import { useEffect, useState } from "react"
import { ArrowLeft, Pencil, Plus } from "lucide-react"

import { Button } from "@/design-system/components/Button"
import { EmptyState, ErrorState, LoadingState } from "@/design-system/components/PageState"
import { PageHeader } from "@/design-system/layout/PageHeader"
import { PageTab, PageTabs } from "@/design-system/layout/PageTabs"
import { PageWorkspace } from "@/design-system/layout/PageWorkspace"
import { CataloguePaginationControls } from "@/design-system/patterns/catalogue/CataloguePage"
import { DetailRow, DetailSection } from "@/design-system/patterns/detail/Detail"
import {
  listApplicationComponents,
  listApplicationDeployments,
  listInteractionDefinitions,
  readApplicationDefinition,
  type ApplicationComponentDto,
  type ApplicationDefinitionDto,
  type ApplicationDeploymentSummaryDto,
  type InteractionDefinitionSummaryDto,
} from "@/features/catalogues/api/targetCatalogue"
import {
  ApplicationComponentsTable,
  ApplicationDeploymentsTable,
  InteractionDefinitionsTable,
} from "@/features/catalogues/components/ApplicationDefinitionTables"
import {
  ApplicationDefinitionToolbar,
  type ApplicationDefinitionFilters,
  type ApplicationDefinitionTab,
} from "@/features/catalogues/components/ApplicationDefinitionToolbar"
import { InteractionDefinitionCreatePanel } from "@/features/catalogues/components/InteractionDefinitionCreatePanel"
import { InteractionDefinitionEditPanel } from "@/features/catalogues/components/InteractionDefinitionEditPanel"
import { ComponentEditPanel, DefinitionEditPanel } from "@/features/catalogues/components/TargetCatalogueEditPanels"
import { CreateComponentPanel, CreateDeploymentPanel } from "@/features/catalogues/components/TargetCatalogueForms"
import { ApiError } from "@/lib/api"

type Tab = "overview" | ApplicationDefinitionTab

const EMPTY_FILTERS: ApplicationDefinitionFilters = { search: "", first: "", second: "", third: "" }
const TAB_LABELS: Record<Tab, string> = {
  overview: "Overview",
  components: "Components",
  interactions: "Interactions",
  deployments: "Deployments",
}

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError ? caught : new ApiError(500, "InternalError", fallback)
}

export function ApplicationDefinitionPage({
  applicationId,
  onBack,
  onOpenDeployment,
}: {
  applicationId: string
  onBack: () => void
  onOpenDeployment: (deploymentId: string) => void
}) {
  const [definition, setDefinition] = useState<ApplicationDefinitionDto | null>(null)
  const [tab, setTab] = useState<Tab>("overview")
  const [tabPage, setTabPage] = useState(1)
  const [tabPageSize, setTabPageSize] = useState(50)
  const [tabTotal, setTabTotal] = useState(0)
  const [draftFilters, setDraftFilters] = useState<ApplicationDefinitionFilters>(EMPTY_FILTERS)
  const [filters, setFilters] = useState<ApplicationDefinitionFilters>(EMPTY_FILTERS)
  const [components, setComponents] = useState<ApplicationComponentDto[]>([])
  const [interactions, setInteractions] = useState<InteractionDefinitionSummaryDto[]>([])
  const [deployments, setDeployments] = useState<ApplicationDeploymentSummaryDto[]>([])
  const [loading, setLoading] = useState(true)
  const [tabLoading, setTabLoading] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)
  const [tabError, setTabError] = useState<ApiError | null>(null)
  const [createOpen, setCreateOpen] = useState(false)
  const [definitionEditOpen, setDefinitionEditOpen] = useState(false)
  const [editingComponent, setEditingComponent] = useState<ApplicationComponentDto | null>(null)
  const [editingInteraction, setEditingInteraction] = useState<InteractionDefinitionSummaryDto | null>(null)
  const [reloadToken, setReloadToken] = useState(0)

  useEffect(() => {
    let active = true
    setLoading(true)
    setError(null)
    void readApplicationDefinition(applicationId)
      .then((result) => { if (active) setDefinition(result.definition) })
      .catch((caught) => { if (active) setError(errorFrom(caught, "Application Definition could not be loaded.")) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [applicationId])

  useEffect(() => {
    if (tab === "overview") return
    let active = true
    setTabLoading(true)
    setTabError(null)
    const acceptPage = (result: { total: number }) => {
      if (active) setTabTotal(result.total)
    }
    const pending = tab === "components"
      ? listApplicationComponents({ applicationId, page: tabPage, pageSize: tabPageSize, search: filters.search, componentType: filters.first, sort: "name" })
          .then((result) => { if (active) setComponents(result.items); acceptPage(result) })
      : tab === "interactions"
        ? listInteractionDefinitions({ applicationId, page: tabPage, pageSize: tabPageSize, search: filters.search, protocol: filters.first, sort: "source" })
            .then((result) => { if (active) setInteractions(result.items); acceptPage(result) })
        : listApplicationDeployments({ applicationId, page: tabPage, pageSize: tabPageSize, search: filters.search, companyReference: filters.first, environment: filters.second, scopeReference: filters.third, sort: "company" })
            .then((result) => { if (active) setDeployments(result.items); acceptPage(result) })
    void pending
      .catch((caught) => { if (active) setTabError(errorFrom(caught, "Definition details could not be loaded.")) })
      .finally(() => { if (active) setTabLoading(false) })
    return () => { active = false }
  }, [applicationId, tab, tabPage, tabPageSize, filters, reloadToken])

  function selectTab(next: Tab) {
    setTabPage(1)
    setTabPageSize(50)
    setTabTotal(0)
    setDraftFilters(EMPTY_FILTERS)
    setFilters(EMPTY_FILTERS)
    setCreateOpen(false)
    setEditingComponent(null)
    setEditingInteraction(null)
    setTab(next)
  }

  function refreshTab(closeEditor = true) {
    setCreateOpen(false)
    if (closeEditor) {
      setEditingComponent(null)
      setEditingInteraction(null)
    }
    setTabPage(1)
    setReloadToken((value) => value + 1)
  }

  if (loading || error) {
    return (
      <PageWorkspace>
        {loading ? <LoadingState>Loading application definition…</LoadingState> : <ErrorState message={error?.message ?? "Application Definition could not be loaded."} />}
      </PageWorkspace>
    )
  }
  if (!definition) return null

  const applyFilters = () => {
    setTabPage(1)
    setFilters({
      search: draftFilters.search.trim(),
      first: draftFilters.first.trim(),
      second: draftFilters.second.trim(),
      third: draftFilters.third.trim(),
    })
  }

  return (
    <PageWorkspace>
      <div>
        <Button variant="ghost" size="sm" onClick={onBack}>
          <ArrowLeft className="size-4" aria-hidden="true" />Definitions
        </Button>
      </div>
      <PageHeader
        title={definition.displayName}
        description={`${definition.domain ?? "No domain"}${definition.ownerReference ? ` · Owner: ${definition.ownerReference}` : ""}`}
        actions={
          <Button variant="secondary" onClick={() => setDefinitionEditOpen((value) => !value)}>
            <Pencil className="size-[var(--napms-icon-size-control)]" aria-hidden="true" />Edit
          </Button>
        }
      />

      {definitionEditOpen ? (
        <DefinitionEditPanel
          definition={definition}
          onChanged={(updated) => { setDefinition(updated); setDefinitionEditOpen(false) }}
          onRetired={onBack}
          onCancel={() => setDefinitionEditOpen(false)}
        />
      ) : null}

      <PageTabs>
        {(Object.keys(TAB_LABELS) as Tab[]).map((item) => (
          <PageTab key={item} active={tab === item} onClick={() => selectTab(item)}>{TAB_LABELS[item]}</PageTab>
        ))}
      </PageTabs>

      {tab === "overview" ? (
        <DetailSection title="Application definition">
          <DetailRow label="Name">{definition.displayName}</DetailRow>
          <DetailRow label="Domain">{definition.domain ?? "—"}</DetailRow>
          <DetailRow label="Owner">{definition.ownerReference ?? "—"}</DetailRow>
          <DetailRow label="Description">{definition.description ?? "—"}</DetailRow>
        </DetailSection>
      ) : (
        <>
          <ApplicationDefinitionToolbar tab={tab} draft={draftFilters} onDraft={setDraftFilters} onApply={applyFilters} />

          {tab === "components" ? (
            <>
              <DetailSection
                title="Components"
                actions={<Button size="sm" onClick={() => { setEditingComponent(null); setCreateOpen((value) => !value) }}><Plus className="size-4" aria-hidden="true" />Add component</Button>}
              >
                {createOpen ? <CreateComponentPanel applicationId={applicationId} onCancel={() => setCreateOpen(false)} onCreated={() => refreshTab()} /> : null}
                {editingComponent ? <ComponentEditPanel component={editingComponent} onChanged={(updated) => { setComponents((items) => items.map((item) => item.componentId === updated.componentId ? updated : item)); setEditingComponent(null) }} onRetired={() => refreshTab()} onCancel={() => setEditingComponent(null)} /> : null}
                {tabLoading ? <LoadingState>Loading components…</LoadingState> : tabError ? <ErrorState message={tabError.message} /> : components.length === 0 ? <EmptyState title="No active components" /> : <ApplicationComponentsTable items={components} onEdit={(item) => { setCreateOpen(false); setEditingComponent(item) }} />}
              </DetailSection>
            </>
          ) : tab === "interactions" ? (
            <DetailSection
              title="Interactions"
              actions={<Button size="sm" onClick={() => { setEditingInteraction(null); setCreateOpen((value) => !value) }}><Plus className="size-4" aria-hidden="true" />Add interaction</Button>}
            >
              {createOpen ? <InteractionDefinitionCreatePanel applicationId={applicationId} onCancel={() => setCreateOpen(false)} onCreated={() => refreshTab()} /> : null}
              {editingInteraction ? <InteractionDefinitionEditPanel interaction={editingInteraction} sourceName={editingInteraction.sourceComponentName} destinationName={editingInteraction.destinationComponentName} onChanged={() => refreshTab(false)} onRetired={() => refreshTab()} onCancel={() => setEditingInteraction(null)} /> : null}
              {tabLoading ? <LoadingState>Loading interactions…</LoadingState> : tabError ? <ErrorState message={tabError.message} /> : interactions.length === 0 ? <EmptyState title="No active interactions" /> : <InteractionDefinitionsTable items={interactions} onEdit={(item) => { setCreateOpen(false); setEditingInteraction(item) }} />}
            </DetailSection>
          ) : (
            <DetailSection
              title="Deployments"
              actions={<Button size="sm" onClick={() => setCreateOpen((value) => !value)}><Plus className="size-4" aria-hidden="true" />Add deployment</Button>}
            >
              {createOpen ? <CreateDeploymentPanel applicationId={applicationId} onCancel={() => setCreateOpen(false)} onCreated={() => refreshTab()} /> : null}
              {tabLoading ? <LoadingState>Loading deployments…</LoadingState> : tabError ? <ErrorState message={tabError.message} /> : deployments.length === 0 ? <EmptyState title="No active deployments" /> : <ApplicationDeploymentsTable items={deployments} onOpen={onOpenDeployment} />}
            </DetailSection>
          )}

          {!tabLoading && !tabError ? (
            <CataloguePaginationControls
              page={tabPage}
              pageSize={tabPageSize}
              total={tabTotal}
              onPageChange={setTabPage}
              onPageSizeChange={(nextPageSize) => { setTabPageSize(nextPageSize); setTabPage(1) }}
            />
          ) : null}
        </>
      )}
    </PageWorkspace>
  )
}
