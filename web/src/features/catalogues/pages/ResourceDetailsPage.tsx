import { useEffect, useState } from "react"
import { ArrowLeft, ChevronDown, Plus } from "lucide-react"

import { Button } from "@/design-system/components/Button"
import { Input, Select, Textarea } from "@/design-system/components/Field"
import { ErrorState, LoadingState } from "@/design-system/components/PageState"
import { StatusIndicator } from "@/design-system/components/StatusIndicator"
import { Tag } from "@/design-system/components/Tag"
import { PageWorkspace } from "@/design-system/layout/PageWorkspace"
import { DetailRow, DetailSection } from "@/design-system/patterns/detail/Detail"
import { Surface } from "@/design-system/primitives/Surface"
import {
  createCatalogueResourceRealization,
  createCatalogueResourceResponsibility,
  createCatalogueResourceScopeAffiliation,
  endCatalogueResourceResponsibility,
  endCatalogueResourceScopeAffiliation,
  readCatalogueResource,
  replaceCatalogueResourceRealization,
  type ResourceDetailDto,
  type ResourceResponsibilityDto,
  type ResourceScopeAffiliationDto,
} from "@/features/catalogues/api/catalogue"
import {
  readCatalogueResourceHistory,
  type ResourceHistoryDto,
} from "@/features/catalogues/api/resourceHistory"
import {
  renameCatalogueResource,
  retireCatalogueResource,
} from "@/features/catalogues/api/resourceWorkspace"
import { shortId } from "@/features/catalogues/components/CatalogueIdentity"
import {
  formatResourceDate,
  ResourceBasicInformation,
  ResourceHistorySection,
  ResourceTechnicalDetails,
} from "@/features/catalogues/components/ResourceDetailSections"
import { ApiError } from "@/lib/api"

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError
    ? caught
    : new ApiError(500, "InternalError", fallback)
}

function roleLabel(role: ResourceResponsibilityDto["role"]) {
  return {
    TechnicalOwner: "Technical owner",
    ServiceOwner: "Service owner",
    OperationsContact: "Operations contact",
    BusinessOwner: "Business owner",
  }[role]
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
  const [actionsOpen, setActionsOpen] = useState(false)

  const [editingName, setEditingName] = useState(false)
  const [nameDraft, setNameDraft] = useState("")
  const [savingLifecycle, setSavingLifecycle] = useState<"rename" | "retire" | null>(null)
  const [lifecycleError, setLifecycleError] = useState<string | null>(null)

  const [editingAddresses, setEditingAddresses] = useState(false)
  const [addresses, setAddresses] = useState("")
  const [savingRealization, setSavingRealization] = useState(false)
  const [realizationError, setRealizationError] = useState<string | null>(null)

  const [addingScope, setAddingScope] = useState(false)
  const [responsibilityScope, setResponsibilityScope] = useState("")
  const [creatingAffiliation, setCreatingAffiliation] = useState(false)
  const [endingAffiliationReference, setEndingAffiliationReference] = useState<string | null>(null)
  const [affiliationError, setAffiliationError] = useState<string | null>(null)

  const [addingResponsibility, setAddingResponsibility] = useState(false)
  const [partyReference, setPartyReference] = useState("")
  const [partyKind, setPartyKind] = useState<"Person" | "Team">("Team")
  const [responsibilityRole, setResponsibilityRole] = useState<ResourceResponsibilityDto["role"]>("TechnicalOwner")
  const [responsibilityDisplayName, setResponsibilityDisplayName] = useState("")
  const [responsibilityContact, setResponsibilityContact] = useState("")
  const [creatingResponsibility, setCreatingResponsibility] = useState(false)
  const [endingResponsibilityReference, setEndingResponsibilityReference] = useState<string | null>(null)
  const [responsibilityError, setResponsibilityError] = useState<string | null>(null)

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

  useEffect(() => {
    void load()
  }, [resourceReference])

  useEffect(() => {
    if (!editingName && detail) setNameDraft(detail.resource.displayName ?? "")
  }, [detail, editingName])

  async function renameResource(event: React.FormEvent) {
    event.preventDefault()
    if (!detail) return
    const nextName = nameDraft.trim()
    if (!nextName || nextName === (detail.resource.displayName ?? "")) return
    setSavingLifecycle("rename")
    setLifecycleError(null)
    try {
      await renameCatalogueResource(detail.resource, nextName)
      setEditingName(false)
      await load()
    } catch (caught) {
      setLifecycleError(errorFrom(caught, "Resource could not be renamed.").message)
    } finally {
      setSavingLifecycle(null)
    }
  }

  async function retireResource() {
    if (!detail) return
    setActionsOpen(false)
    if (!window.confirm(
      "Retire this resource? Current scope affiliations and responsibilities must be ended first. Historical references will be preserved.",
    )) return
    setSavingLifecycle("retire")
    setLifecycleError(null)
    try {
      await retireCatalogueResource(detail.resource)
      await load()
    } catch (caught) {
      const failure = errorFrom(caught, "Resource could not be retired.")
      setLifecycleError(
        failure.code === "CatalogueRetirementBlocked"
          ? "End current scope affiliations and responsibilities before retiring this resource."
          : failure.message,
      )
    } finally {
      setSavingLifecycle(null)
    }
  }

  async function saveRealization(event: React.FormEvent) {
    event.preventDefault()
    const values = addresses
      .split(/[\n,]+/)
      .map((value) => value.trim())
      .filter(Boolean)
    if (values.length === 0) return
    setSavingRealization(true)
    setRealizationError(null)
    try {
      const current = detail?.effectiveRealizations[0]
      if (current) {
        await replaceCatalogueResourceRealization(current, values, new Date().toISOString())
      } else {
        await createCatalogueResourceRealization(resourceReference, values, new Date().toISOString())
      }
      setAddresses("")
      setEditingAddresses(false)
      await load()
    } catch (caught) {
      setRealizationError(errorFrom(caught, "Resource realization could not be saved.").message)
    } finally {
      setSavingRealization(false)
    }
  }

  async function addScopeAffiliation(event: React.FormEvent) {
    event.preventDefault()
    const reference = responsibilityScope.trim()
    if (!reference) return
    setCreatingAffiliation(true)
    setAffiliationError(null)
    try {
      await createCatalogueResourceScopeAffiliation(resourceReference, reference, new Date().toISOString())
      setResponsibilityScope("")
      setAddingScope(false)
      await load()
    } catch (caught) {
      setAffiliationError(errorFrom(caught, "Scope affiliation could not be created.").message)
    } finally {
      setCreatingAffiliation(false)
    }
  }

  async function endScopeAffiliation(item: ResourceScopeAffiliationDto) {
    if (!window.confirm(`End scope affiliation ${item.responsibilityScope} now?`)) return
    setEndingAffiliationReference(item.affiliationReference)
    setAffiliationError(null)
    try {
      await endCatalogueResourceScopeAffiliation(item, new Date().toISOString())
      await load()
    } catch (caught) {
      setAffiliationError(errorFrom(caught, "Scope affiliation could not be ended.").message)
    } finally {
      setEndingAffiliationReference(null)
    }
  }

  async function addResponsibility(event: React.FormEvent) {
    event.preventDefault()
    const reference = partyReference.trim()
    const displayName = responsibilityDisplayName.trim()
    if (!reference || !displayName) return
    setCreatingResponsibility(true)
    setResponsibilityError(null)
    try {
      await createCatalogueResourceResponsibility(resourceReference, {
        partyReference: reference,
        partyKind,
        role: responsibilityRole,
        displayName,
        contact: responsibilityContact.trim() || null,
        validFrom: new Date().toISOString(),
      })
      setPartyReference("")
      setResponsibilityDisplayName("")
      setResponsibilityContact("")
      setAddingResponsibility(false)
      await load()
    } catch (caught) {
      setResponsibilityError(errorFrom(caught, "Resource responsibility could not be created.").message)
    } finally {
      setCreatingResponsibility(false)
    }
  }

  async function endResponsibility(item: ResourceResponsibilityDto) {
    if (!window.confirm(`End ${roleLabel(item.role)} responsibility for ${item.displayName} now?`)) return
    setEndingResponsibilityReference(item.assignmentReference)
    setResponsibilityError(null)
    try {
      await endCatalogueResourceResponsibility(item, new Date().toISOString())
      await load()
    } catch (caught) {
      setResponsibilityError(errorFrom(caught, "Resource responsibility could not be ended.").message)
    } finally {
      setEndingResponsibilityReference(null)
    }
  }

  if (loading && detail === null) return <LoadingState>Loading resource…</LoadingState>
  if (error && detail === null) return <ErrorState message={error.message} onRetry={() => void load()} />
  if (!detail) return null

  const resourceActive = detail.resource.lifecycle === "Active"
  const currentRealization = detail.effectiveRealizations[0]
  const currentName = detail.resource.displayName || shortId(detail.resource.resourceReference)

  return (
    <PageWorkspace>
      <header>
        <button
          type="button"
          className="mb-2 inline-flex items-center gap-1.5 text-xs font-medium text-[var(--napms-color-primary)] hover:underline"
          onClick={onBack}
        >
          <ArrowLeft className="size-3.5" aria-hidden="true" />
          Back to resources
        </button>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="truncate text-xl font-semibold text-[var(--napms-color-text-primary)]">{currentName}</h1>
              <StatusIndicator tone={resourceActive ? "positive" : "critical"}>{detail.resource.lifecycle}</StatusIndicator>
            </div>
            <div className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">
              Resource reference: <span className="font-mono">{detail.resource.resourceReference}</span>
            </div>
          </div>
          <div className="relative">
            <Button variant="secondary" onClick={() => setActionsOpen((value) => !value)}>
              Actions <ChevronDown className="size-4" aria-hidden="true" />
            </Button>
            {actionsOpen ? (
              <div className="absolute right-0 z-20 mt-2 w-44 overflow-hidden rounded-[var(--napms-control-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)] py-1 shadow-lg">
                {resourceActive ? (
                  <button
                    type="button"
                    className="block w-full px-3 py-2 text-left text-sm hover:bg-[var(--napms-color-surface-subtle)]"
                    onClick={() => {
                      setActionsOpen(false)
                      setEditingName(true)
                    }}
                  >
                    Rename
                  </button>
                ) : null}
                {resourceActive ? (
                  <button
                    type="button"
                    className="block w-full px-3 py-2 text-left text-sm text-[var(--napms-color-danger)] hover:bg-[var(--napms-color-danger-bg)]"
                    onClick={() => void retireResource()}
                  >
                    Retire resource
                  </button>
                ) : null}
              </div>
            ) : null}
          </div>
        </div>
      </header>

      {editingName ? (
        <Surface className="p-4">
          <form className="flex flex-col gap-3 sm:flex-row sm:items-end" onSubmit={renameResource}>
            <label className="grid min-w-0 flex-1 gap-1 text-xs font-medium text-[var(--napms-color-text-body)]">
              Display name
              <Input value={nameDraft} onChange={(event) => setNameDraft(event.target.value)} />
            </label>
            <div className="flex gap-2">
              <Button type="button" variant="secondary" onClick={() => setEditingName(false)}>Cancel</Button>
              <Button type="submit" loading={savingLifecycle === "rename"}>Save</Button>
            </div>
          </form>
        </Surface>
      ) : null}

      {lifecycleError ? (
        <div role="alert" className="rounded-[var(--napms-control-radius)] border border-[var(--napms-color-danger)] bg-[var(--napms-color-danger-bg)] p-3 text-sm text-[var(--napms-color-danger)]">
          {lifecycleError}
        </div>
      ) : null}

      <div className="flex gap-6 border-b border-[var(--napms-color-border)] text-sm">
        {(["overview", "history", "technical"] as const).map((value) => (
          <button
            key={value}
            type="button"
            className={
              tab === value
                ? "border-b-2 border-[var(--napms-color-primary)] px-1 pb-2 font-semibold text-[var(--napms-color-primary)]"
                : "px-1 pb-2 text-[var(--napms-color-text-secondary)]"
            }
            onClick={() => setTab(value)}
          >
            {value === "overview" ? "Overview" : value === "history" ? "History" : "Technical details"}
          </button>
        ))}
      </div>

      {tab === "overview" ? (
        <div className="grid min-w-0 gap-4 xl:grid-cols-2">
          <div className="grid content-start gap-4">
            <ResourceBasicInformation detail={detail} />

            <DetailSection title="Technical realization">
              {currentRealization ? (
                <>
                  <DetailRow label="Addresses">
                    <div className="grid gap-1 font-mono text-xs">
                      {currentRealization.technicalAddresses.map((item) => (
                        <span key={item.endpointReference}>{item.technicalAddress}</span>
                      ))}
                    </div>
                  </DetailRow>
                  <DetailRow label="Effective since">
                    {formatResourceDate(currentRealization.validFrom)}
                  </DetailRow>
                </>
              ) : (
                <p className="text-sm text-[var(--napms-color-text-secondary)]">No current realization.</p>
              )}
              {resourceActive ? (
                <Button className="mt-3" variant="secondary" size="sm" onClick={() => setEditingAddresses(true)}>
                  {currentRealization ? "Replace addresses" : "Add addresses"}
                </Button>
              ) : null}
              {editingAddresses ? (
                <form className="mt-3 grid gap-2" onSubmit={saveRealization}>
                  <label className="grid gap-1 text-xs font-medium">
                    Addresses
                    <Textarea
                      className="font-mono"
                      value={addresses}
                      onChange={(event) => setAddresses(event.target.value)}
                      placeholder={"10.20.30.40\n10.20.30.41"}
                    />
                  </label>
                  {realizationError ? <p className="text-xs text-[var(--napms-color-danger)]">{realizationError}</p> : null}
                  <div className="flex gap-2">
                    <Button type="button" variant="secondary" size="sm" onClick={() => setEditingAddresses(false)}>Cancel</Button>
                    <Button type="submit" size="sm" loading={savingRealization}>
                      {currentRealization ? "Replace" : "Add"}
                    </Button>
                  </div>
                </form>
              ) : null}
            </DetailSection>
          </div>

          <div className="grid content-start gap-4">
            <DetailSection title="Responsibility scopes">
              <div className="flex flex-wrap gap-2">
                {detail.effectiveScopeAffiliations.length ? (
                  detail.effectiveScopeAffiliations.map((item) => (
                    <div key={item.affiliationReference} className="flex items-center gap-2">
                      <Tag>{item.responsibilityScope}</Tag>
                      {resourceActive ? (
                        <button
                          type="button"
                          className="text-xs text-[var(--napms-color-danger)] hover:underline"
                          disabled={endingAffiliationReference === item.affiliationReference}
                          onClick={() => void endScopeAffiliation(item)}
                        >
                          End
                        </button>
                      ) : null}
                    </div>
                  ))
                ) : (
                  <span className="text-sm text-[var(--napms-color-text-secondary)]">No current scope.</span>
                )}
              </div>
              {resourceActive ? (
                <Button className="mt-3" variant="secondary" size="sm" onClick={() => setAddingScope(true)}>
                  <Plus className="size-3.5" aria-hidden="true" />Add scope
                </Button>
              ) : null}
              {addingScope ? (
                <form className="mt-3 flex gap-2" onSubmit={addScopeAffiliation}>
                  <Input value={responsibilityScope} onChange={(event) => setResponsibilityScope(event.target.value)} placeholder="payments-team" />
                  <Button type="submit" size="sm" loading={creatingAffiliation}>Add</Button>
                </form>
              ) : null}
              {affiliationError ? <p className="mt-2 text-xs text-[var(--napms-color-danger)]">{affiliationError}</p> : null}
            </DetailSection>

            <DetailSection title="Responsibilities">
              <div className="grid gap-3">
                {detail.effectiveResponsibilities.length ? (
                  detail.effectiveResponsibilities.map((item) => (
                    <div key={item.assignmentReference} className="grid grid-cols-[130px_minmax(0,1fr)_auto] items-start gap-3 border-b border-[var(--napms-color-border)] pb-3 last:border-0 last:pb-0">
                      <div className="text-xs text-[var(--napms-color-text-secondary)]">{roleLabel(item.role)}</div>
                      <div>
                        <div className="text-sm font-semibold text-[var(--napms-color-primary)]">{item.displayName}</div>
                        {item.contact ? <div className="text-xs text-[var(--napms-color-text-secondary)]">{item.contact}</div> : null}
                      </div>
                      {resourceActive ? (
                        <button
                          type="button"
                          className="text-xs text-[var(--napms-color-danger)] hover:underline"
                          disabled={endingResponsibilityReference === item.assignmentReference}
                          onClick={() => void endResponsibility(item)}
                        >
                          End
                        </button>
                      ) : null}
                    </div>
                  ))
                ) : (
                  <span className="text-sm text-[var(--napms-color-text-secondary)]">No current responsibility.</span>
                )}
              </div>
              {resourceActive ? (
                <Button className="mt-3" variant="secondary" size="sm" onClick={() => setAddingResponsibility(true)}>
                  <Plus className="size-3.5" aria-hidden="true" />Add responsibility
                </Button>
              ) : null}
              {addingResponsibility ? (
                <form className="mt-3 grid gap-2" onSubmit={addResponsibility}>
                  <div className="grid gap-2 sm:grid-cols-2">
                    <Select value={partyKind} onChange={(event) => setPartyKind(event.target.value as "Person" | "Team")}>
                      <option value="Team">Team</option>
                      <option value="Person">Person</option>
                    </Select>
                    <Select value={responsibilityRole} onChange={(event) => setResponsibilityRole(event.target.value as ResourceResponsibilityDto["role"])}>
                      <option value="TechnicalOwner">Technical owner</option>
                      <option value="ServiceOwner">Service owner</option>
                      <option value="OperationsContact">Operations contact</option>
                      <option value="BusinessOwner">Business owner</option>
                    </Select>
                  </div>
                  <Input value={partyReference} onChange={(event) => setPartyReference(event.target.value)} placeholder="team:platform" />
                  <Input value={responsibilityDisplayName} onChange={(event) => setResponsibilityDisplayName(event.target.value)} placeholder="Platform Team" />
                  <Input value={responsibilityContact} onChange={(event) => setResponsibilityContact(event.target.value)} placeholder="Contact (optional)" />
                  <div className="flex gap-2">
                    <Button type="button" variant="secondary" size="sm" onClick={() => setAddingResponsibility(false)}>Cancel</Button>
                    <Button type="submit" size="sm" loading={creatingResponsibility}>Add</Button>
                  </div>
                </form>
              ) : null}
              {responsibilityError ? <p className="mt-2 text-xs text-[var(--napms-color-danger)]">{responsibilityError}</p> : null}
            </DetailSection>
          </div>
        </div>
      ) : null}

      {tab === "history" ? (
        <ResourceHistorySection history={history} />
      ) : null}

      {tab === "technical" ? (
        <ResourceTechnicalDetails detail={detail} />
      ) : null}
    </PageWorkspace>
  )
}
