import { useEffect, useState } from "react"
import { ArrowLeft, Pencil, Plus } from "lucide-react"

import { Button } from "@/design-system/components/Button"
import { Input } from "@/design-system/components/Field"
import { EmptyState, ErrorState, LoadingState } from "@/design-system/components/PageState"
import { SearchInput } from "@/design-system/components/SearchInput"
import { PageHeader } from "@/design-system/layout/PageHeader"
import { PageWorkspace } from "@/design-system/layout/PageWorkspace"
import {
  CatalogueFilterBar,
  CatalogueFilterField,
  CataloguePaginationControls,
  CatalogueToolbar,
} from "@/design-system/patterns/catalogue/CataloguePage"
import { DetailRow, DetailSection } from "@/design-system/patterns/detail/Detail"
import {
  retireDeploymentInteraction,
  TargetCatalogueApiError,
  type DependencyGroupDto,
} from "@/features/catalogues/api/targetCommands"
import { readDeploymentInteractionLifecycle } from "@/features/catalogues/api/targetDeploymentInteractionLifecycle"
import {
  listAvailableInteractions,
  listDeploymentConnectivity,
  readApplicationDeployment,
  type ApplicationDeploymentDto,
  type DeploymentConnectivityDto,
  type DeploymentInteractionSide,
} from "@/features/catalogues/api/targetCatalogue"
import { AddDeploymentInteractionPanel } from "@/features/catalogues/components/AddDeploymentInteractionPanel"
import { DependencyBlockPanel } from "@/features/catalogues/components/DependencyBlockPanel"
import { DeploymentConnectivityTable } from "@/features/catalogues/components/DeploymentConnectivityTable"
import { DeploymentEditPanel } from "@/features/catalogues/components/TargetCatalogueEditPanels"
import { ApiError } from "@/lib/api"

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError ? caught : new ApiError(500, "InternalError", fallback)
}

export function ApplicationDeploymentPage({
  deploymentId,
  onBack,
  onOpenResources,
}: {
  deploymentId: string
  onBack: () => void
  onOpenResources: (deploymentInteractionId: string, side: DeploymentInteractionSide) => void
}) {
  const [deployment, setDeployment] = useState<ApplicationDeploymentDto | null>(null)
  const [applicationName, setApplicationName] = useState<string | null>(null)
  const [selectedTotal, setSelectedTotal] = useState(0)
  const [definedTotal, setDefinedTotal] = useState(0)
  const [detailLoading, setDetailLoading] = useState(true)
  const [detailError, setDetailError] = useState<ApiError | null>(null)
  const [editOpen, setEditOpen] = useState(false)

  const [connectivity, setConnectivity] = useState<DeploymentConnectivityDto[]>([])
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(50)
  const [filteredTotal, setFilteredTotal] = useState(0)
  const [connectivityLoading, setConnectivityLoading] = useState(true)
  const [connectivityError, setConnectivityError] = useState<ApiError | null>(null)
  const [draftSearch, setDraftSearch] = useState("")
  const [draftProtocol, setDraftProtocol] = useState("")
  const [search, setSearch] = useState("")
  const [protocol, setProtocol] = useState("")
  const [addOpen, setAddOpen] = useState(false)
  const [reloadToken, setReloadToken] = useState(0)
  const [removingId, setRemovingId] = useState<string | null>(null)
  const [removeError, setRemoveError] = useState<string | null>(null)
  const [removeBlockers, setRemoveBlockers] = useState<DependencyGroupDto[] | null>(null)
  const [removeBlockerSubject, setRemoveBlockerSubject] = useState<string | null>(null)
  const [removing, setRemoving] = useState(false)

  useEffect(() => {
    let active = true
    setDetailLoading(true)
    setDetailError(null)
    void Promise.all([
      readApplicationDeployment(deploymentId),
      listDeploymentConnectivity({ applicationDeploymentId: deploymentId, page: 1, pageSize: 1 }),
      listAvailableInteractions({ applicationDeploymentId: deploymentId, page: 1, pageSize: 1 }),
    ])
      .then(([detail, selected, available]) => {
        if (!active) return
        setDeployment(detail.deployment)
        setApplicationName(detail.applicationName)
        setSelectedTotal(selected.total)
        setDefinedTotal(selected.total + available.total)
      })
      .catch((caught) => { if (active) setDetailError(errorFrom(caught, "Application Deployment could not be loaded.")) })
      .finally(() => { if (active) setDetailLoading(false) })
    return () => { active = false }
  }, [deploymentId, reloadToken])

  useEffect(() => {
    let active = true
    setConnectivityLoading(true)
    setConnectivityError(null)
    void listDeploymentConnectivity({ applicationDeploymentId: deploymentId, page, pageSize, search, protocol })
      .then((result) => {
        if (!active) return
        setConnectivity(result.items)
        setFilteredTotal(result.total)
      })
      .catch((caught) => { if (active) setConnectivityError(errorFrom(caught, "Connectivity could not be loaded.")) })
      .finally(() => { if (active) setConnectivityLoading(false) })
    return () => { active = false }
  }, [deploymentId, page, pageSize, search, protocol, reloadToken])

  function refreshDeployment() {
    setPage(1)
    setRemovingId(null)
    setRemoveError(null)
    setRemoveBlockers(null)
    setRemoveBlockerSubject(null)
    setReloadToken((value) => value + 1)
  }

  async function removeInteraction(deploymentInteractionId: string) {
    setRemoving(true)
    setRemoveError(null)
    setRemoveBlockers(null)
    setRemoveBlockerSubject(null)
    try {
      const current = await readDeploymentInteractionLifecycle(deploymentInteractionId)
      if (current.lifecycleState === "Retired") {
        refreshDeployment()
        return
      }
      await retireDeploymentInteraction(deploymentInteractionId, current.version)
      refreshDeployment()
    } catch (caught) {
      if (caught instanceof TargetCatalogueApiError && caught.code === "CatalogueDependencyBlocked") {
        setRemoveBlockers(caught.details?.dependencies ?? [])
        setRemoveBlockerSubject(deploymentInteractionId)
      } else {
        setRemoveError(caught instanceof Error ? caught.message : "Interaction could not be removed from the deployment.")
      }
    } finally {
      setRemoving(false)
      setRemovingId(null)
    }
  }

  if (detailLoading || detailError) {
    return (
      <PageWorkspace>
        {detailLoading ? <LoadingState>Loading deployment…</LoadingState> : <ErrorState message={detailError?.message ?? "Application Deployment could not be loaded."} />}
      </PageWorkspace>
    )
  }
  if (!deployment) return null

  return (
    <PageWorkspace>
      <div>
        <Button variant="ghost" size="sm" onClick={onBack}>
          <ArrowLeft className="size-4" aria-hidden="true" />Deployments
        </Button>
      </div>

      <PageHeader
        title={`${applicationName ?? "Application"} — ${deployment.companyReference} / ${deployment.environment}`}
        description="Application deployment and its selected connectivity."
        actions={
          <Button variant="secondary" onClick={() => setEditOpen((value) => !value)}>
            <Pencil className="size-[var(--napms-icon-size-control)]" aria-hidden="true" />Edit
          </Button>
        }
      />

      {editOpen ? (
        <DeploymentEditPanel
          deployment={deployment}
          onChanged={(updated) => { setDeployment(updated); setEditOpen(false); refreshDeployment() }}
          onRetired={onBack}
          onCancel={() => setEditOpen(false)}
        />
      ) : null}

      <DetailSection title="Deployment">
        <div className="grid gap-x-8 md:grid-cols-2 xl:grid-cols-4">
          <DetailRow label="Application" labelWidthClassName="grid-cols-1">{applicationName ?? "—"}</DetailRow>
          <DetailRow label="Company" labelWidthClassName="grid-cols-1">{deployment.companyReference}</DetailRow>
          <DetailRow label="Environment" labelWidthClassName="grid-cols-1">{deployment.environment}</DetailRow>
          <DetailRow label="Scope" labelWidthClassName="grid-cols-1">{deployment.scopeReference}</DetailRow>
        </div>
      </DetailSection>

      <DetailSection
        title={`Connectivity ${selectedTotal} / ${definedTotal}`}
        actions={<Button size="sm" onClick={() => setAddOpen((value) => !value)}><Plus className="size-4" aria-hidden="true" />Add interaction</Button>}
      >
        <p className="mb-3 text-xs text-[var(--napms-color-text-secondary)]">Selected Interaction Definitions in this deployment.</p>

        {addOpen ? <AddDeploymentInteractionPanel deploymentId={deploymentId} onCancel={() => setAddOpen(false)} onChanged={refreshDeployment} /> : null}

        <form
          onSubmit={(event) => {
            event.preventDefault()
            setPage(1)
            setSearch(draftSearch.trim())
            setProtocol(draftProtocol.trim())
          }}
        >
          <CatalogueToolbar>
            <SearchInput value={draftSearch} onChange={(event) => setDraftSearch(event.target.value)} placeholder="Search connectivity" aria-label="Search connectivity" />
            <CatalogueFilterBar>
              <CatalogueFilterField label="Protocol" className="xl:w-[190px]">
                <Input value={draftProtocol} onChange={(event) => setDraftProtocol(event.target.value)} aria-label="Protocol" />
              </CatalogueFilterField>
              <Button type="submit" variant="secondary" size="sm" className="xl:ml-auto">Apply</Button>
            </CatalogueFilterBar>
          </CatalogueToolbar>
        </form>

        {removeError ? <div className="my-3 rounded-[var(--napms-control-radius)] border border-[var(--napms-color-danger-dot)] bg-[var(--napms-color-danger-bg)] px-4 py-3 text-sm text-[var(--napms-color-danger)]">{removeError}</div> : null}
        {removeBlockers && removeBlockerSubject ? <DependencyBlockPanel groups={removeBlockers} subjectKind="deployment-interaction" subjectId={removeBlockerSubject} onClose={() => { setRemoveBlockers(null); setRemoveBlockerSubject(null) }} /> : null}

        {connectivityLoading ? (
          <LoadingState>Loading connectivity…</LoadingState>
        ) : connectivityError ? (
          <ErrorState message={connectivityError.message} />
        ) : connectivity.length === 0 ? (
          <EmptyState title="No interactions match the current view" />
        ) : (
          <DeploymentConnectivityTable
            items={connectivity}
            removingId={removingId}
            removing={removing}
            onOpenResources={onOpenResources}
            onRequestRemove={setRemovingId}
            onCancelRemove={() => setRemovingId(null)}
            onConfirmRemove={(interactionId) => void removeInteraction(interactionId)}
          />
        )}

        {!connectivityLoading && !connectivityError ? (
          <CataloguePaginationControls
            page={page}
            pageSize={pageSize}
            total={filteredTotal}
            onPageChange={setPage}
            onPageSizeChange={(nextPageSize) => { setPageSize(nextPageSize); setPage(1) }}
          />
        ) : null}
      </DetailSection>
    </PageWorkspace>
  )
}
