import { useEffect, useMemo, useState } from "react"
import { ArrowLeft, Plus } from "lucide-react"

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
import { DetailSection } from "@/design-system/patterns/detail/Detail"
import { endDeploymentResourceBinding } from "@/features/catalogues/api/targetCommands"
import {
  listDeploymentInteractionResources,
  type DeploymentInteractionSide,
  type ResourceSetMemberDto,
} from "@/features/catalogues/api/targetCatalogue"
import { DeploymentResourceSetTable } from "@/features/catalogues/components/DeploymentResourceSetTable"
import { ResourceMembershipPanel } from "@/features/catalogues/components/ResourceMembershipPanel"
import { ApiError } from "@/lib/api"

function errorFrom(caught: unknown) {
  return caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Resource set could not be loaded.")
}

export function DeploymentResourceSetPage({
  deploymentInteractionId,
  side,
  onBack,
}: {
  deploymentInteractionId: string
  side: DeploymentInteractionSide
  onBack: () => void
}) {
  const [items, setItems] = useState<ResourceSetMemberDto[]>([])
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(50)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)
  const [mutationError, setMutationError] = useState<ApiError | null>(null)
  const [draftSearch, setDraftSearch] = useState("")
  const [draftScope, setDraftScope] = useState("")
  const [search, setSearch] = useState("")
  const [scope, setScope] = useState("")
  const [addOpen, setAddOpen] = useState(false)
  const [endingReference, setEndingReference] = useState<string | null>(null)
  const [ending, setEnding] = useState(false)
  const [reloadToken, setReloadToken] = useState(0)

  const visibleResourceReferences = useMemo(
    () => new Set(items.map((item) => item.resourceReference)),
    [items],
  )

  useEffect(() => {
    let active = true
    setLoading(true)
    setError(null)
    void listDeploymentInteractionResources({ deploymentInteractionId, side, page, pageSize, search, scopeReference: scope })
      .then((result) => {
        if (!active) return
        setItems(result.items)
        setTotal(result.total)
      })
      .catch((caught) => { if (active) setError(errorFrom(caught)) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [deploymentInteractionId, side, page, pageSize, search, scope, reloadToken])

  function refreshMembership() {
    setMutationError(null)
    setEndingReference(null)
    setPage(1)
    setReloadToken((value) => value + 1)
  }

  async function endMembership(item: ResourceSetMemberDto) {
    setEnding(true)
    setMutationError(null)
    try {
      await endDeploymentResourceBinding({
        deploymentInteractionId,
        side,
        bindingReference: item.bindingReference,
        validTo: new Date().toISOString(),
        expectedVersion: item.bindingVersion,
      })
      refreshMembership()
    } catch (caught) {
      setMutationError(errorFrom(caught))
    } finally {
      setEnding(false)
    }
  }

  return (
    <PageWorkspace>
      <div>
        <Button variant="ghost" size="sm" onClick={onBack}>
          <ArrowLeft className="size-4" aria-hidden="true" />Deployment
        </Button>
      </div>
      <PageHeader
        title={`${side} resources`}
        description={`${total} effective resources`}
        actions={<Button onClick={() => setAddOpen((value) => !value)}><Plus className="size-4" aria-hidden="true" />Add resource</Button>}
      />

      <DetailSection>
        {addOpen ? (
          <ResourceMembershipPanel
            deploymentInteractionId={deploymentInteractionId}
            side={side}
            activeResourceReferences={visibleResourceReferences}
            onChanged={refreshMembership}
            onCancel={() => setAddOpen(false)}
          />
        ) : null}

        <form
          onSubmit={(event) => {
            event.preventDefault()
            setPage(1)
            setSearch(draftSearch.trim())
            setScope(draftScope.trim())
          }}
        >
          <CatalogueToolbar>
            <SearchInput value={draftSearch} onChange={(event) => setDraftSearch(event.target.value)} placeholder="Search resources" aria-label="Search resources" />
            <CatalogueFilterBar>
              <CatalogueFilterField label="Scope" className="xl:w-[220px]">
                <Input value={draftScope} onChange={(event) => setDraftScope(event.target.value)} aria-label="Scope" />
              </CatalogueFilterField>
              <Button type="submit" variant="secondary" size="sm" className="xl:ml-auto">Apply</Button>
            </CatalogueFilterBar>
          </CatalogueToolbar>
        </form>

        {mutationError ? <div className="my-3 rounded-[var(--napms-control-radius)] border border-[var(--napms-color-danger-dot)] bg-[var(--napms-color-danger-bg)] px-4 py-3 text-sm text-[var(--napms-color-danger)]">{mutationError.message}</div> : null}

        {loading ? (
          <LoadingState>Loading resources…</LoadingState>
        ) : error ? (
          <ErrorState message={error.message} />
        ) : items.length === 0 ? (
          <EmptyState title="No resources match the current view" />
        ) : (
          <DeploymentResourceSetTable
            items={items}
            endingReference={endingReference}
            ending={ending}
            onRequestEnd={setEndingReference}
            onCancelEnd={() => setEndingReference(null)}
            onConfirmEnd={(item) => void endMembership(item)}
          />
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
      </DetailSection>
    </PageWorkspace>
  )
}
