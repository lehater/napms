import { useEffect, useState } from "react"
import { ArrowLeft, Network, Plus, RefreshCw, Users } from "lucide-react"

import { ApiError } from "@/api"
import { shortId } from "@/components/catalogue/CatalogueIdentity"
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
} from "@/features/catalogues/catalogueApi"

const inputClass =
  "min-h-10 w-full rounded-md border border-[#CBD5E1] bg-white px-3 py-2 text-sm text-[#172033] outline-none focus:border-[#2563EB] focus:ring-2 focus:ring-[#DBEAFE]"

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError
    ? caught
    : new ApiError(500, "InternalError", fallback)
}

export function ResourceDetailsPage({
  resourceReference,
  onBack,
}: {
  resourceReference: string
  onBack: () => void
}) {
  const [detail, setDetail] = useState<ResourceDetailDto | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)

  const [addresses, setAddresses] = useState("")
  const [savingRealization, setSavingRealization] = useState(false)
  const [realizationError, setRealizationError] = useState<ApiError | null>(null)

  const [responsibilityScope, setResponsibilityScope] = useState("")
  const [creatingAffiliation, setCreatingAffiliation] = useState(false)
  const [endingAffiliationReference, setEndingAffiliationReference] = useState<string | null>(null)
  const [affiliationError, setAffiliationError] = useState<ApiError | null>(null)

  const [partyReference, setPartyReference] = useState("")
  const [partyKind, setPartyKind] = useState<"Person" | "Team">("Team")
  const [responsibilityRole, setResponsibilityRole] = useState<
    "ServiceOwner" | "TechnicalOwner" | "OperationsContact" | "BusinessOwner"
  >("TechnicalOwner")
  const [responsibilityDisplayName, setResponsibilityDisplayName] = useState("")
  const [responsibilityContact, setResponsibilityContact] = useState("")
  const [creatingResponsibility, setCreatingResponsibility] = useState(false)
  const [endingResponsibilityReference, setEndingResponsibilityReference] = useState<
    string | null
  >(null)
  const [responsibilityError, setResponsibilityError] = useState<ApiError | null>(null)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      setDetail(await readCatalogueResource(resourceReference))
    } catch (caught) {
      setError(errorFrom(caught, "Resource details could not be loaded."))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [resourceReference])

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
        await replaceCatalogueResourceRealization(
          current,
          values,
          new Date().toISOString(),
        )
      } else {
        await createCatalogueResourceRealization(
          resourceReference,
          values,
          new Date().toISOString(),
        )
      }
      setAddresses("")
      await load()
    } catch (caught) {
      setRealizationError(
        errorFrom(caught, "Resource realization could not be saved."),
      )
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
      await createCatalogueResourceScopeAffiliation(
        resourceReference,
        reference,
        new Date().toISOString(),
      )
      setResponsibilityScope("")
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
      await load()
    } catch (caught) {
      setResponsibilityError(
        errorFrom(caught, "Resource responsibility could not be created."),
      )
    } finally {
      setCreatingResponsibility(false)
    }
  }

  async function endResponsibility(item: ResourceResponsibilityDto) {
    if (!window.confirm(`End ${item.role} responsibility for ${item.displayName} now?`)) {
      return
    }
    setEndingResponsibilityReference(item.assignmentReference)
    setResponsibilityError(null)
    try {
      await endCatalogueResourceResponsibility(item, new Date().toISOString())
      await load()
    } catch (caught) {
      setResponsibilityError(
        errorFrom(caught, "Resource responsibility could not be ended."),
      )
    } finally {
      setEndingResponsibilityReference(null)
    }
  }

  if (loading && detail === null) {
    return <div className="text-sm text-[#64748B]">Loading resource…</div>
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

  const hasCurrentRealization = detail.effectiveRealizations.length > 0

  return (
    <div className="mx-auto grid max-w-6xl gap-6">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <button
            type="button"
            className="mb-3 inline-flex items-center gap-2 text-sm font-semibold text-[#2563EB] hover:underline"
            onClick={onBack}
          >
            <ArrowLeft className="size-4" aria-hidden="true" />
            Resources
          </button>
          <h1 className="text-2xl font-bold text-[#172033]">
            {detail.resource.displayName || shortId(detail.resource.resourceReference)}
          </h1>
          <div className="mt-1 font-mono text-xs text-[#64748B]">
            {detail.resource.resourceReference}
          </div>
        </div>
        <Button variant="secondary" loading={loading} onClick={() => void load()}>
          <RefreshCw className="size-4" aria-hidden="true" />
          Refresh
        </Button>
      </header>

      <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
        <div className="mb-4 flex items-center gap-2">
          <Plus className="size-4 text-[#2563EB]" aria-hidden="true" />
          <h2 className="font-semibold text-[#172033]">
            {hasCurrentRealization ? "Replace technical addresses" : "Add technical addresses"}
          </h2>
        </div>
        <form className="grid gap-3" onSubmit={saveRealization}>
          <textarea
            className={`${inputClass} min-h-24 resize-y`}
            value={addresses}
            onChange={(event) => setAddresses(event.target.value)}
            placeholder={"10.20.30.40\n10.20.30.41"}
            aria-label="Technical addresses"
          />
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-xs text-[#64748B]">
              {hasCurrentRealization
                ? "Replacing ends the current realization now and creates a new historical version."
                : "One address per line or comma. A new authoritative realization starts now."}
            </p>
            <Button type="submit" loading={savingRealization} disabled={!addresses.trim()}>
              {hasCurrentRealization ? "Replace addresses" : "Add addresses"}
            </Button>
          </div>
        </form>
        {realizationError ? (
          <p className="mt-3 text-sm text-red-700">{realizationError.message}</p>
        ) : null}
      </section>

      <div className="grid gap-5 lg:grid-cols-2">
        <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <Network className="size-4 text-[#64748B]" aria-hidden="true" />
            <h2 className="font-semibold text-[#172033]">Current realization</h2>
          </div>
          {detail.effectiveRealizations.length === 0 ? (
            <p className="text-sm text-[#64748B]">No current technical addresses.</p>
          ) : (
            <div className="grid gap-4">
              {detail.effectiveRealizations.map((realization) => (
                <div key={realization.factReference} className="rounded-md bg-[#F8FAFC] p-4">
                  <div className="grid gap-2">
                    {realization.technicalAddresses.map((endpoint) => (
                      <div key={`${endpoint.endpointReference}:${endpoint.technicalAddress}`}>
                        <div className="font-mono text-sm font-semibold text-[#172033]">
                          {endpoint.technicalAddress}
                        </div>
                        <div className="font-mono text-[11px] text-[#64748B]">
                          {shortId(endpoint.endpointReference)}
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-3 text-xs text-[#64748B]">
                    Effective from {new Date(realization.validFrom).toLocaleString()} · v{realization.version}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
          <h2 className="font-semibold text-[#172033]">Responsibility scopes</h2>
          <form className="mt-4 grid gap-3" onSubmit={addScopeAffiliation}>
            <label className="grid gap-1 text-sm font-medium text-[#172033]">
              External scope reference
              <input
                className={inputClass}
                value={responsibilityScope}
                onChange={(event) => setResponsibilityScope(event.target.value)}
                placeholder="payments-team"
                autoComplete="off"
              />
            </label>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="max-w-xl text-xs text-[#64748B]">
                Correlation reference from the scope naming source used by your environment. NAPMS does not create that scope or derive curation authority from it.
              </p>
              <Button
                type="submit"
                loading={creatingAffiliation}
                disabled={!responsibilityScope.trim()}
              >
                Add affiliation
              </Button>
            </div>
          </form>
          {affiliationError ? (
            <p className="mt-3 text-sm text-red-700">{affiliationError.message}</p>
          ) : null}

          {detail.effectiveScopeAffiliations.length === 0 ? (
            <p className="mt-5 text-sm text-[#64748B]">No current scope affiliations.</p>
          ) : (
            <div className="mt-5 grid gap-2">
              {detail.effectiveScopeAffiliations.map((item) => (
                <div
                  key={item.affiliationReference}
                  className="flex items-center justify-between gap-3 rounded-md bg-[#F8FAFC] px-4 py-3"
                >
                  <div>
                    <div className="font-medium text-[#172033]">{item.responsibilityScope}</div>
                    <div className="mt-1 text-xs text-[#64748B]">
                      since {new Date(item.validFrom).toLocaleString()} · v{item.version}
                    </div>
                  </div>
                  <Button
                    variant="secondary"
                    loading={endingAffiliationReference === item.affiliationReference}
                    disabled={endingAffiliationReference !== null}
                    onClick={() => void endScopeAffiliation(item)}
                  >
                    End
                  </Button>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
        <div className="mb-4 flex items-center gap-2">
          <Users className="size-4 text-[#64748B]" aria-hidden="true" />
          <h2 className="font-semibold text-[#172033]">Responsibilities</h2>
        </div>

        <form className="grid gap-3 rounded-md bg-[#F8FAFC] p-4" onSubmit={addResponsibility}>
          <div className="grid gap-3 md:grid-cols-2">
            <label className="grid gap-1 text-sm font-medium text-[#172033]">
              Party kind
              <select
                className={inputClass}
                value={partyKind}
                onChange={(event) => setPartyKind(event.target.value as "Person" | "Team")}
              >
                <option value="Team">Team</option>
                <option value="Person">Person</option>
              </select>
            </label>
            <label className="grid gap-1 text-sm font-medium text-[#172033]">
              Role
              <select
                className={inputClass}
                value={responsibilityRole}
                onChange={(event) =>
                  setResponsibilityRole(
                    event.target.value as
                      | "ServiceOwner"
                      | "TechnicalOwner"
                      | "OperationsContact"
                      | "BusinessOwner",
                  )
                }
              >
                <option value="TechnicalOwner">Technical owner</option>
                <option value="ServiceOwner">Service owner</option>
                <option value="OperationsContact">Operations contact</option>
                <option value="BusinessOwner">Business owner</option>
              </select>
            </label>
            <label className="grid gap-1 text-sm font-medium text-[#172033]">
              External person/team reference
              <input
                className={inputClass}
                value={partyReference}
                onChange={(event) => setPartyReference(event.target.value)}
                placeholder="team:orders"
                autoComplete="off"
              />
            </label>
            <label className="grid gap-1 text-sm font-medium text-[#172033]">
              Display name
              <input
                className={inputClass}
                value={responsibilityDisplayName}
                onChange={(event) => setResponsibilityDisplayName(event.target.value)}
                placeholder="Orders Team"
                autoComplete="off"
              />
            </label>
          </div>
          <label className="grid gap-1 text-sm font-medium text-[#172033]">
            Contact (optional)
            <input
              className={inputClass}
              value={responsibilityContact}
              onChange={(event) => setResponsibilityContact(event.target.value)}
              placeholder="orders@example.test"
              autoComplete="off"
            />
          </label>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="max-w-2xl text-xs text-[#64748B]">
              The external reference correlates this contact with a Person or Team identity owned outside Resource Catalogue. The assignment does not grant NAPMS permissions.
            </p>
            <Button
              type="submit"
              loading={creatingResponsibility}
              disabled={!partyReference.trim() || !responsibilityDisplayName.trim()}
            >
              Add responsibility
            </Button>
          </div>
        </form>
        {responsibilityError ? (
          <p className="mt-3 text-sm text-red-700">{responsibilityError.message}</p>
        ) : null}

        {detail.effectiveResponsibilities.length === 0 ? (
          <p className="mt-5 text-sm text-[#64748B]">No current responsibility assignments.</p>
        ) : (
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            {detail.effectiveResponsibilities.map((item) => (
              <div key={item.assignmentReference} className="rounded-md border border-[#E2E8F0] p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="font-semibold text-[#172033]">{item.displayName}</div>
                    <div className="mt-1 text-sm text-[#64748B]">
                      {item.role} · {item.partyKind}
                    </div>
                  </div>
                  <Button
                    variant="secondary"
                    loading={endingResponsibilityReference === item.assignmentReference}
                    disabled={endingResponsibilityReference !== null}
                    onClick={() => void endResponsibility(item)}
                  >
                    End
                  </Button>
                </div>
                <div className="mt-2 font-mono text-xs text-[#64748B]">{item.partyReference}</div>
                {item.contact ? (
                  <div className="mt-2 text-sm text-[#172033]">{item.contact}</div>
                ) : null}
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
