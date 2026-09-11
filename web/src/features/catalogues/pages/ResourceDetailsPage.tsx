import { useEffect, useMemo, useState } from "react"
import {
  Archive,
  ArrowLeft,
  ChevronDown,
  Clock3,
  Database,
  MoreHorizontal,
  Network,
  Pencil,
  Plus,
  RefreshCw,
  UserRound,
  Users,
  X,
} from "lucide-react"

import { ApiError } from "@/lib/api"
import { shortId } from "@/features/catalogues/components/CatalogueIdentity"
import { Button } from "@/components/ui/Button"
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

const inputClass =
  "min-h-10 w-full rounded-md border border-[#CBD5E1] bg-white px-3 py-2 text-sm text-[#172033] outline-none transition focus:border-[#2563EB] focus:ring-2 focus:ring-[#DBEAFE]"

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

function LifecycleBadge({ value }: { value: string }) {
  const active = value === "Active"
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${
        active
          ? "bg-emerald-50 text-emerald-700"
          : "bg-slate-100 text-slate-600"
      }`}
    >
      <span className={`size-1.5 rounded-full ${active ? "bg-emerald-500" : "bg-slate-400"}`} />
      {value}
    </span>
  )
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
        detail: item.endProvenanceReference
          ? `End provenance ${shortId(item.endProvenanceReference)}`
          : undefined,
      })
    }
  }

  for (const item of history.scopeAffiliations) {
    values.push({
      key: `scope-start:${item.affiliationReference}`,
      at: item.validFrom,
      title: "Scope affiliation added",
      summary: item.responsibilityScope,
      detail: `Affiliation ${shortId(item.affiliationReference)}`,
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
  const [realizationError, setRealizationError] = useState<ApiError | null>(null)

  const [addingScope, setAddingScope] = useState(false)
  const [responsibilityScope, setResponsibilityScope] = useState("")
  const [creatingAffiliation, setCreatingAffiliation] = useState(false)
  const [endingAffiliationReference, setEndingAffiliationReference] = useState<string | null>(null)
  const [affiliationError, setAffiliationError] = useState<ApiError | null>(null)

  const [addingResponsibility, setAddingResponsibility] = useState(false)
  const [partyReference, setPartyReference] = useState("")
  const [partyKind, setPartyKind] = useState<"Person" | "Team">("Team")
  const [responsibilityRole, setResponsibilityRole] = useState<
    "ServiceOwner" | "TechnicalOwner" | "OperationsContact" | "BusinessOwner"
  >("TechnicalOwner")
  const [responsibilityDisplayName, setResponsibilityDisplayName] = useState("")
  const [responsibilityContact, setResponsibilityContact] = useState("")
  const [creatingResponsibility, setCreatingResponsibility] = useState(false)
  const [endingResponsibilityReference, setEndingResponsibilityReference] = useState<string | null>(null)
  const [responsibilityError, setResponsibilityError] = useState<ApiError | null>(null)

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
    if (!editingName && detail) {
      setNameDraft(detail.resource.displayName ?? "")
    }
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
      setRealizationError(errorFrom(caught, "Resource realization could not be saved."))
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
      setAffiliationError(errorFrom(caught, "Scope affiliation could not be created."))
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
      setAffiliationError(errorFrom(caught, "Scope affiliation could not be ended."))
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
      setResponsibilityError(errorFrom(caught, "Resource responsibility could not be created."))
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
      setResponsibilityError(errorFrom(caught, "Resource responsibility could not be ended."))
    } finally {
      setEndingResponsibilityReference(null)
    }
  }

  if (loading && detail === null) {
    return <div className="p-8 text-sm text-[#64748B]">Loading resource…</div>
  }

  if (error && detail === null) {
    return (
      <div className="mx-auto max-w-4xl rounded-lg border border-red-200 bg-red-50 p-5">
        <p className="text-sm text-red-800">{error.message}</p>
        <div className="mt-4 flex gap-2">
          <Button variant="secondary" onClick={onBack}>Back</Button>
          <Button onClick={() => void load()}>Retry</Button>
        </div>
      </div>
    )
  }

  if (!detail) return null

  const resourceActive = detail.resource.lifecycle === "Active"
  const currentRealization = detail.effectiveRealizations[0]
  const currentName = detail.resource.displayName || shortId(detail.resource.resourceReference)

  return (
    <div className="mx-auto grid max-w-[1380px] gap-5">
      <header>
        <button
          type="button"
          className="mb-3 inline-flex items-center gap-2 text-sm font-semibold text-[#2563EB] hover:underline"
          onClick={onBack}
        >
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to resources
        </button>

        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl font-bold text-[#172033]">{currentName}</h1>
              <LifecycleBadge value={detail.resource.lifecycle} />
            </div>
            <div className="mt-1 text-xs text-[#64748B]">
              Resource reference: <span className="font-mono">{detail.resource.resourceReference}</span>
            </div>
          </div>

          <div className="relative">
            <Button
              variant="secondary"
              onClick={() => setActionsOpen((value) => !value)}
            >
              Actions
              <ChevronDown className="size-4" aria-hidden="true" />
            </Button>
            {actionsOpen ? (
              <div className="absolute right-0 z-20 mt-2 w-48 overflow-hidden rounded-lg border border-[#E2E8F0] bg-white py-1 shadow-xl">
                {resourceActive ? (
                  <button
                    type="button"
                    className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-[#172033] hover:bg-[#F8FAFC]"
                    onClick={() => {
                      setActionsOpen(false)
                      setEditingName(true)
                    }}
                  >
                    <Pencil className="size-4" /> Rename
                  </button>
                ) : null}
                <button
                  type="button"
                  className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-[#172033] hover:bg-[#F8FAFC]"
                  onClick={() => {
                    setActionsOpen(false)
                    void load()
                  }}
                >
                  <RefreshCw className="size-4" /> Refresh
                </button>
                {resourceActive ? (
                  <button
                    type="button"
                    className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-red-700 hover:bg-red-50"
                    onClick={() => void retireResource()}
                  >
                    <Archive className="size-4" /> Retire resource
                  </button>
                ) : null}
              </div>
            ) : null}
          </div>
        </div>
      </header>

      {editingName ? (
        <form className="flex flex-wrap gap-2 rounded-lg border border-[#BFDBFE] bg-[#EFF6FF] p-4" onSubmit={renameResource}>
          <input
            className={`${inputClass} max-w-lg`}
            value={nameDraft}
            onChange={(event) => setNameDraft(event.target.value)}
            maxLength={256}
            autoFocus
          />
          <Button type="submit" loading={savingLifecycle === "rename"}>Save</Button>
          <Button type="button" variant="secondary" onClick={() => setEditingName(false)}>Cancel</Button>
        </form>
      ) : null}

      {lifecycleError ? (
        <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800" role="alert">
          {lifecycleError}
        </div>
      ) : null}

      <nav className="flex gap-1 border-b border-[#E2E8F0]" aria-label="Resource details">
        {[
          ["overview", "Overview"],
          ["history", "History"],
          ["technical", "Technical details"],
        ].map(([value, label]) => (
          <button
            key={value}
            type="button"
            className={`border-b-2 px-4 py-3 text-sm font-semibold transition ${
              tab === value
                ? "border-[#2563EB] text-[#2563EB]"
                : "border-transparent text-[#64748B] hover:text-[#172033]"
            }`}
            onClick={() => setTab(value as typeof tab)}
          >
            {label}
          </button>
        ))}
      </nav>

      {tab === "overview" ? (
        <div className="grid gap-5 lg:grid-cols-2">
          <div className="grid content-start gap-5">
            <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
              <h2 className="font-semibold text-[#172033]">Basic information</h2>
              <dl className="mt-4 grid grid-cols-[10rem_1fr] gap-x-4 gap-y-3 text-sm">
                <dt className="text-[#64748B]">Name</dt>
                <dd className="font-medium text-[#172033]">{currentName}</dd>
                <dt className="text-[#64748B]">Reference</dt>
                <dd className="font-mono text-xs text-[#334155]">{detail.resource.resourceReference}</dd>
                <dt className="text-[#64748B]">Lifecycle</dt>
                <dd><LifecycleBadge value={detail.resource.lifecycle} /></dd>
                <dt className="text-[#64748B]">Version</dt>
                <dd className="text-[#334155]">v{detail.resource.version}</dd>
                <dt className="text-[#64748B]">State read at</dt>
                <dd className="text-[#334155]">{formatDate(detail.asOf)}</dd>
              </dl>
            </section>

            <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2">
                  <Network className="size-4 text-[#64748B]" aria-hidden="true" />
                  <h2 className="font-semibold text-[#172033]">Technical realization</h2>
                </div>
                {resourceActive ? (
                  <Button variant="secondary" onClick={() => setEditingAddresses((value) => !value)}>
                    {currentRealization ? "Replace addresses" : "Add addresses"}
                  </Button>
                ) : null}
              </div>

              {currentRealization ? (
                <div className="mt-4 grid gap-3">
                  <div className="grid gap-1.5">
                    {currentRealization.technicalAddresses.map((endpoint) => (
                      <div key={endpoint.endpointReference} className="font-mono text-sm font-semibold text-[#2563EB]">
                        {endpoint.technicalAddress}
                      </div>
                    ))}
                  </div>
                  <div className="text-xs text-[#64748B]">
                    Effective since {formatDate(currentRealization.validFrom)}
                  </div>
                </div>
              ) : (
                <p className="mt-4 text-sm text-[#64748B]">No current technical addresses.</p>
              )}

              {editingAddresses ? (
                <form className="mt-4 grid gap-3 rounded-md bg-[#F8FAFC] p-4" onSubmit={saveRealization}>
                  <textarea
                    className={`${inputClass} min-h-24 resize-y font-mono`}
                    value={addresses}
                    onChange={(event) => setAddresses(event.target.value)}
                    placeholder={"10.20.30.40\n10.20.30.41"}
                    autoFocus
                  />
                  <div className="flex justify-end gap-2">
                    <Button type="button" variant="secondary" onClick={() => setEditingAddresses(false)}>Cancel</Button>
                    <Button type="submit" loading={savingRealization} disabled={!addresses.trim()}>
                      {currentRealization ? "Replace" : "Add"}
                    </Button>
                  </div>
                </form>
              ) : null}
              {realizationError ? <p className="mt-3 text-sm text-red-700">{realizationError.message}</p> : null}
            </section>
          </div>

          <div className="grid content-start gap-5">
            <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="font-semibold text-[#172033]">Responsibility scopes</h2>
                  <p className="mt-1 text-xs text-[#64748B]">Current effective affiliations.</p>
                </div>
                {resourceActive ? (
                  <Button variant="secondary" onClick={() => setAddingScope((value) => !value)}>
                    <Plus className="size-4" /> Add scope
                  </Button>
                ) : null}
              </div>

              {addingScope ? (
                <form className="mt-4 flex flex-col gap-2 rounded-md bg-[#F8FAFC] p-4 sm:flex-row" onSubmit={addScopeAffiliation}>
                  <input
                    className={inputClass}
                    value={responsibilityScope}
                    onChange={(event) => setResponsibilityScope(event.target.value)}
                    placeholder="payments-team"
                    autoFocus
                  />
                  <Button type="submit" loading={creatingAffiliation} disabled={!responsibilityScope.trim()}>Add</Button>
                  <Button type="button" variant="ghost" onClick={() => setAddingScope(false)}><X className="size-4" /></Button>
                </form>
              ) : null}

              {detail.effectiveScopeAffiliations.length === 0 ? (
                <p className="mt-4 text-sm text-[#64748B]">No current scope affiliations.</p>
              ) : (
                <div className="mt-4 grid gap-2 sm:grid-cols-2">
                  {detail.effectiveScopeAffiliations.map((item) => (
                    <div key={item.affiliationReference} className="rounded-md border border-[#E2E8F0] p-3">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <div className="inline-flex rounded bg-[#EFF6FF] px-2 py-0.5 text-sm font-semibold text-[#1D4ED8]">
                            {item.responsibilityScope}
                          </div>
                          <div className="mt-2 text-xs text-[#64748B]">Since {formatDate(item.validFrom)}</div>
                        </div>
                        {resourceActive ? (
                          <button
                            type="button"
                            className="text-xs font-semibold text-[#64748B] hover:text-red-700"
                            disabled={endingAffiliationReference !== null}
                            onClick={() => void endScopeAffiliation(item)}
                          >
                            {endingAffiliationReference === item.affiliationReference ? "Ending…" : "End"}
                          </button>
                        ) : null}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {affiliationError ? <p className="mt-3 text-sm text-red-700">{affiliationError.message}</p> : null}
            </section>

            <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2">
                  <Users className="size-4 text-[#64748B]" aria-hidden="true" />
                  <h2 className="font-semibold text-[#172033]">Responsibilities</h2>
                </div>
                {resourceActive ? (
                  <Button variant="secondary" onClick={() => setAddingResponsibility((value) => !value)}>
                    <Plus className="size-4" /> Add responsibility
                  </Button>
                ) : null}
              </div>

              {addingResponsibility ? (
                <form className="mt-4 grid gap-3 rounded-md bg-[#F8FAFC] p-4" onSubmit={addResponsibility}>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <select className={inputClass} value={partyKind} onChange={(event) => setPartyKind(event.target.value as "Person" | "Team")}>
                      <option value="Team">Team</option>
                      <option value="Person">Person</option>
                    </select>
                    <select
                      className={inputClass}
                      value={responsibilityRole}
                      onChange={(event) => setResponsibilityRole(event.target.value as typeof responsibilityRole)}
                    >
                      <option value="TechnicalOwner">Technical owner</option>
                      <option value="ServiceOwner">Service owner</option>
                      <option value="OperationsContact">Operations contact</option>
                      <option value="BusinessOwner">Business owner</option>
                    </select>
                    <input className={inputClass} value={partyReference} onChange={(event) => setPartyReference(event.target.value)} placeholder="team:platform" />
                    <input className={inputClass} value={responsibilityDisplayName} onChange={(event) => setResponsibilityDisplayName(event.target.value)} placeholder="Platform Team" />
                  </div>
                  <input className={inputClass} value={responsibilityContact} onChange={(event) => setResponsibilityContact(event.target.value)} placeholder="Contact (optional)" />
                  <div className="flex justify-end gap-2">
                    <Button type="button" variant="secondary" onClick={() => setAddingResponsibility(false)}>Cancel</Button>
                    <Button type="submit" loading={creatingResponsibility} disabled={!partyReference.trim() || !responsibilityDisplayName.trim()}>Add</Button>
                  </div>
                </form>
              ) : null}

              {detail.effectiveResponsibilities.length === 0 ? (
                <p className="mt-4 text-sm text-[#64748B]">No current responsibility assignments.</p>
              ) : (
                <div className="mt-4 divide-y divide-[#E2E8F0]">
                  {detail.effectiveResponsibilities.map((item) => (
                    <div key={item.assignmentReference} className="flex items-start justify-between gap-3 py-3 first:pt-0 last:pb-0">
                      <div className="flex min-w-0 gap-3">
                        <div className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-full bg-[#F1F5F9] text-[#64748B]">
                          <UserRound className="size-4" />
                        </div>
                        <div className="min-w-0">
                          <div className="text-xs font-medium text-[#64748B]">{roleLabel(item.role)}</div>
                          <div className="font-semibold text-[#2563EB]">{item.displayName}</div>
                          {item.contact ? <div className="text-xs text-[#64748B]">{item.contact}</div> : null}
                        </div>
                      </div>
                      {resourceActive ? (
                        <button
                          type="button"
                          className="text-xs font-semibold text-[#64748B] hover:text-red-700"
                          disabled={endingResponsibilityReference !== null}
                          onClick={() => void endResponsibility(item)}
                        >
                          {endingResponsibilityReference === item.assignmentReference ? "Ending…" : "End"}
                        </button>
                      ) : null}
                    </div>
                  ))}
                </div>
              )}
              {responsibilityError ? <p className="mt-3 text-sm text-red-700">{responsibilityError.message}</p> : null}
            </section>
          </div>
        </div>
      ) : null}

      {tab === "history" ? (
        <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="font-semibold text-[#172033]">Resource history</h2>
              <p className="mt-1 text-xs text-[#64748B]">
                Temporal realization, scope-affiliation and responsibility changes.
              </p>
            </div>
            <div className="flex items-center gap-2 text-xs text-[#64748B]">
              <Clock3 className="size-4" /> State at: <span className="font-semibold text-[#172033]">Now</span>
            </div>
          </div>

          {events.length === 0 ? (
            <p className="mt-6 text-sm text-[#64748B]">No temporal history is recorded for this resource.</p>
          ) : (
            <div className="mt-6 ml-2 border-l-2 border-[#BFDBFE] pl-6">
              {events.map((event, index) => {
                const month = new Date(event.at).toLocaleDateString(undefined, { month: "long", year: "numeric" })
                const previousMonth = index > 0
                  ? new Date(events[index - 1].at).toLocaleDateString(undefined, { month: "long", year: "numeric" })
                  : null
                return (
                  <div key={event.key} className="relative pb-5 last:pb-0">
                    <span className="absolute -left-[31px] top-1.5 size-3 rounded-full border-2 border-white bg-[#2563EB] shadow" />
                    {month !== previousMonth ? (
                      <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-[#64748B]">{month}</div>
                    ) : null}
                    <div className="rounded-lg border border-[#E2E8F0] bg-white p-4">
                      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                        <div>
                          <div className="font-semibold text-[#172033]">{event.title}</div>
                          <div className="mt-1 text-sm text-[#334155]">{event.summary}</div>
                          {event.detail ? <div className="mt-1 text-xs text-[#64748B]">{event.detail}</div> : null}
                        </div>
                        <time className="whitespace-nowrap text-xs text-[#64748B]">{formatDate(event.at)}</time>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </section>
      ) : null}

      {tab === "technical" ? (
        <div className="grid gap-5 lg:grid-cols-2">
          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
            <div className="flex items-center gap-2">
              <Database className="size-4 text-[#64748B]" />
              <h2 className="font-semibold text-[#172033]">Resource identity</h2>
            </div>
            <dl className="mt-4 grid gap-4 text-sm">
              {[
                ["Resource reference", detail.resource.resourceReference],
                ["Version", String(detail.resource.version)],
                ["Creation provenance", detail.resource.provenanceReference],
                ["Retirement provenance", detail.resource.retirementProvenanceReference || "—"],
              ].map(([label, value]) => (
                <div key={label}>
                  <dt className="text-xs font-medium text-[#64748B]">{label}</dt>
                  <dd className="mt-1 break-all font-mono text-xs text-[#334155]">{value}</dd>
                </div>
              ))}
            </dl>
          </section>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
            <div className="flex items-center gap-2">
              <MoreHorizontal className="size-4 text-[#64748B]" />
              <h2 className="font-semibold text-[#172033]">Current fact references</h2>
            </div>
            <div className="mt-4 grid gap-4">
              {detail.effectiveRealizations.map((item) => (
                <div key={item.factReference}>
                  <div className="text-xs font-medium text-[#64748B]">Realization</div>
                  <div className="mt-1 break-all font-mono text-xs text-[#334155]">{item.factReference} · v{item.version}</div>
                </div>
              ))}
              {detail.effectiveScopeAffiliations.map((item) => (
                <div key={item.affiliationReference}>
                  <div className="text-xs font-medium text-[#64748B]">Scope affiliation · {item.responsibilityScope}</div>
                  <div className="mt-1 break-all font-mono text-xs text-[#334155]">{item.affiliationReference} · v{item.version}</div>
                </div>
              ))}
              {detail.effectiveResponsibilities.map((item) => (
                <div key={item.assignmentReference}>
                  <div className="text-xs font-medium text-[#64748B]">Responsibility · {roleLabel(item.role)}</div>
                  <div className="mt-1 break-all font-mono text-xs text-[#334155]">{item.assignmentReference} · v{item.version}</div>
                </div>
              ))}
              {detail.effectiveRealizations.length === 0 && detail.effectiveScopeAffiliations.length === 0 && detail.effectiveResponsibilities.length === 0 ? (
                <p className="text-sm text-[#64748B]">No current temporal facts.</p>
              ) : null}
            </div>
          </section>
        </div>
      ) : null}
    </div>
  )
}
