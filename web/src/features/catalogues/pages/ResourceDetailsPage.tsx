import { useEffect, useMemo, useState } from "react"
import { ArrowLeft, ChevronDown, Plus } from "lucide-react"

import { Button } from "@/components/ui/Button"
import { Input, Select } from "@/components/ui/Field"
import { ErrorState, LoadingState } from "@/design-system/components/PageState"
import { StatusIndicator } from "@/design-system/components/StatusIndicator"
import { Tag } from "@/design-system/components/Tag"
import { PageWorkspace } from "@/design-system/layout/PageWorkspace"
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
import { ApiError } from "@/lib/api"

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError
    ? caught
    : new ApiError(500, "InternalError", fallback)
}

function formatDate(value: string) {
  return new Date(value).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

function roleLabel(role: ResourceResponsibilityDto["role"]) {
  return {
    TechnicalOwner: "Technical owner",
    ServiceOwner: "Service owner",
    OperationsContact: "Operations contact",
    BusinessOwner: "Business owner",
  }[role]
}

type HistoryEvent = {
  key: string
  at: string
  title: string
  summary: string
  detail?: string
}

function historyEvents(history: ResourceHistoryDto | null): HistoryEvent[] {
  if (!history) return []
  const values: HistoryEvent[] = []

  for (const item of history.realizations) {
    const addresses = item.technicalAddresses.map((value) => value.technicalAddress).join(", ")
    values.push({
      key: `realization-start:${item.factReference}`,
      at: item.validFrom,
      title: "Technical realization started",
      summary: addresses || "Technical addresses recorded",
      detail: `Fact ${shortId(item.factReference)} · v${item.version}`,
    })
    if (item.validTo) {
      values.push({
        key: `realization-end:${item.factReference}`,
        at: item.validTo,
        title: "Technical realization ended",
        summary: addresses || "Technical addresses ended",
      })
    }
  }

  for (const item of history.scopeAffiliations) {
    values.push({
      key: `scope-start:${item.affiliationReference}`,
      at: item.validFrom,
      title: "Scope affiliation added",
      summary: item.responsibilityScope,
    })
    if (item.validTo) {
      values.push({
        key: `scope-end:${item.affiliationReference}`,
        at: item.validTo,
        title: "Scope affiliation ended",
        summary: item.responsibilityScope,
      })
    }
  }

  for (const item of history.responsibilities) {
    values.push({
      key: `responsibility-start:${item.assignmentReference}`,
      at: item.validFrom,
      title: "Responsibility assigned",
      summary: `${roleLabel(item.role)} · ${item.displayName}`,
      detail: item.contact || undefined,
    })
    if (item.validTo) {
      values.push({
        key: `responsibility-end:${item.assignmentReference}`,
        at: item.validTo,
        title: "Responsibility ended",
        summary: `${roleLabel(item.role)} · ${item.displayName}`,
      })
    }
  }

  return values.sort((a, b) => new Date(b.at).getTime() - new Date(a.at).getTime())
}

function DetailRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="grid grid-cols-[130px_minmax(0,1fr)] gap-3 py-1.5 text-sm">
      <div className="text-[var(--napms-color-text-secondary)]">{label}</div>
      <div className="min-w-0 text-[var(--napms-color-text-body)]">{children}</div>
    </div>
  )
}

function PanelTitle({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="border-b border-[var(--napms-color-border)] px-4 py-3 text-sm font-semibold text-[var(--napms-color-text-primary)]">
      {children}
    </h2>
  )
}

const textAreaClass =
  "min-h-24 w-full resize-y rounded-[var(--napms-control-radius)] border border-[var(--napms-color-border-strong)] bg-[var(--napms-color-surface)] px-3 py-2 font-mono text-sm text-[var(--napms-color-text-primary)] outline-none transition focus:border-[var(--napms-color-primary)] focus:ring-2 focus:ring-[var(--napms-color-primary-subtle)]"

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

  const events = useMemo(() => historyEvents(history), [history])

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
            <Surface>
              <PanelTitle>Basic information</PanelTitle>
              <div className="p-4">
                <DetailRow label="Name">{currentName}</DetailRow>
                <DetailRow label="Reference"><span className="font-mono text-xs">{detail.resource.resourceReference}</span></DetailRow>
                <DetailRow label="Lifecycle"><StatusIndicator tone={resourceActive ? "positive" : "critical"}>{detail.resource.lifecycle}</StatusIndicator></DetailRow>
                <DetailRow label="Current as of">{formatDate(detail.asOf)}</DetailRow>
              </div>
            </Surface>

            <Surface>
              <PanelTitle>Technical realization</PanelTitle>
              <div className="p-4">
                {currentRealization ? (
                  <>
                    <DetailRow label="Addresses">
                      <div className="grid gap-1 font-mono text-xs">
                        {currentRealization.technicalAddresses.map((item) => (
                          <span key={item.endpointReference}>{item.technicalAddress}</span>
                        ))}
                      </div>
                    </DetailRow>
                    <DetailRow label="Effective since">{formatDate(currentRealization.validFrom)}</DetailRow>
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
                      <textarea
                        className={textAreaClass}
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
              </div>
            </Surface>
          </div>

          <div className="grid content-start gap-4">
            <Surface>
              <PanelTitle>Responsibility scopes</PanelTitle>
              <div className="p-4">
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
              </div>
            </Surface>

            <Surface>
              <PanelTitle>Responsibilities</PanelTitle>
              <div className="p-4">
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
              </div>
            </Surface>
          </div>
        </div>
      ) : null}

      {tab === "history" ? (
        <Surface>
          <PanelTitle>Resource history</PanelTitle>
          <div className="grid gap-3 p-4">
            {events.length ? (
              events.map((event) => (
                <div key={event.key} className="grid gap-1 border-l-2 border-[var(--napms-color-primary-border)] pl-4 sm:grid-cols-[170px_minmax(0,1fr)]">
                  <div className="text-xs text-[var(--napms-color-text-secondary)]">{formatDate(event.at)}</div>
                  <div>
                    <div className="text-sm font-semibold text-[var(--napms-color-text-primary)]">{event.title}</div>
                    <div className="text-sm text-[var(--napms-color-text-body)]">{event.summary}</div>
                    {event.detail ? <div className="text-xs text-[var(--napms-color-text-secondary)]">{event.detail}</div> : null}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-[var(--napms-color-text-secondary)]">No historical facts recorded.</p>
            )}
          </div>
        </Surface>
      ) : null}

      {tab === "technical" ? (
        <Surface>
          <PanelTitle>Technical details</PanelTitle>
          <div className="grid gap-1 p-4 md:grid-cols-2 md:gap-x-8">
            <DetailRow label="Resource reference"><span className="font-mono text-xs">{detail.resource.resourceReference}</span></DetailRow>
            <DetailRow label="Version">{detail.resource.version}</DetailRow>
            <DetailRow label="Provenance"><span className="font-mono text-xs">{detail.resource.provenanceReference}</span></DetailRow>
            <DetailRow label="Retirement provenance">{detail.resource.retirementProvenanceReference ? <span className="font-mono text-xs">{detail.resource.retirementProvenanceReference}</span> : "—"}</DetailRow>
          </div>
          <div className="border-t border-[var(--napms-color-border)] p-4">
            <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-[var(--napms-color-text-secondary)]">Current fact references</h3>
            <div className="grid gap-2 text-xs text-[var(--napms-color-text-body)] md:grid-cols-2">
              {detail.effectiveRealizations.map((item) => <div key={item.factReference}>Realization · <span className="font-mono">{item.factReference}</span> · v{item.version}</div>)}
              {detail.effectiveScopeAffiliations.map((item) => <div key={item.affiliationReference}>Scope · <span className="font-mono">{item.affiliationReference}</span> · v{item.version}</div>)}
              {detail.effectiveResponsibilities.map((item) => <div key={item.assignmentReference}>Responsibility · <span className="font-mono">{item.assignmentReference}</span> · v{item.version}</div>)}
            </div>
          </div>
        </Surface>
      ) : null}
    </PageWorkspace>
  )
}
