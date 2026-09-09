import { useEffect, useMemo, useState } from "react"
import { ChevronRight, CircleAlert, Plus, Search } from "lucide-react"

import {
  ApiError,
  declareConnectivityRequirement,
  listConnectivityRequirementAlignment,
  listConnectivityRequirementInteractions,
  listConnectivityRequirements,
  listConnectivityRequirementScopes,
  type ConnectivityRequirementDto,
  type ProposalInteraction,
  type RequirementApplicability,
  type RequirementPolicyAlignmentStatus,
} from "@/api"
import {
  displayName,
  shortId,
  trafficAlternativeText,
} from "@/components/catalogue/CatalogueIdentity"
import { Button } from "@/components/ui/Button"
import { Field, Select } from "@/components/ui/Field"
import {
  nowLocalDateTimeInput,
  toOffsetAwareIso,
} from "@/lib/datetime"

function applicabilityText(value: RequirementApplicability) {
  return value.kind === "Ongoing"
    ? "Ongoing"
    : `${value.start} → ${value.end}`
}

function alignmentClasses(status: RequirementPolicyAlignmentStatus) {
  switch (status) {
    case "Covered":
      return "border-green-200 bg-green-50 text-green-800"
    case "Uncovered":
      return "border-amber-200 bg-amber-50 text-amber-900"
    case "NotCurrent":
      return "border-slate-200 bg-slate-100 text-slate-700"
    case "Unknown":
      return "border-red-200 bg-red-50 text-red-800"
  }
}

function lifecycleClasses(state: "Active" | "Retired") {
  return state === "Active"
    ? "border-green-200 bg-green-50 text-green-800"
    : "border-slate-200 bg-slate-100 text-slate-700"
}

function optionLabel(name: string | null | undefined, id: string) {
  const readable = name?.trim()
  return readable ? `${readable} · ${shortId(id)}` : shortId(id)
}

function dcsLabel(item: ProposalInteraction) {
  const base = optionLabel(
    item.catalogue?.dcsDisplayName,
    item.dcsContractRevisionId,
  )
  const alternatives = item.catalogue?.trafficAlternatives ?? []
  return alternatives.length > 0
    ? `${base} — ${alternatives.map(trafficAlternativeText).join(" | ")}`
    : base
}

export function ConnectivityRequirementsPage({
  page,
  onPageChange,
  onOpenRequirement,
}: {
  page: number
  onPageChange: (page: number) => void
  onOpenRequirement: (requirementId: string) => void
}) {
  const [requirements, setRequirements] = useState<ConnectivityRequirementDto[]>([])
  const [hasMore, setHasMore] = useState(false)
  const [ambiguousReadScopes, setAmbiguousReadScopes] = useState<string[]>([])
  const [loadingList, setLoadingList] = useState(true)
  const [listError, setListError] = useState<ApiError | null>(null)

  const [alignmentAsOf, setAlignmentAsOf] = useState(
    nowLocalDateTimeInput(),
  )
  const [alignmentById, setAlignmentById] = useState<
    Record<string, RequirementPolicyAlignmentStatus>
  >({})
  const [loadingAlignment, setLoadingAlignment] = useState(true)
  const [alignmentError, setAlignmentError] = useState<ApiError | null>(null)

  const [scopes, setScopes] = useState<string[]>([])
  const [ambiguousDeclareScopes, setAmbiguousDeclareScopes] = useState<string[]>([])
  const [scope, setScope] = useState("")
  const [interactions, setInteractions] = useState<ProposalInteraction[]>([])
  const [interactionPage, setInteractionPage] = useState(1)
  const [hasMoreInteractions, setHasMoreInteractions] = useState(false)
  const [searchInput, setSearchInput] = useState("")
  const [search, setSearch] = useState("")
  const [source, setSource] = useState("")
  const [destination, setDestination] = useState("")
  const [dcs, setDcs] = useState("")
  const [dependent, setDependent] = useState("")
  const [applicabilityKind, setApplicabilityKind] =
    useState<"Ongoing" | "AbsoluteWindow">("Ongoing")
  const [windowStart, setWindowStart] = useState("")
  const [windowEnd, setWindowEnd] = useState("")
  const [justification, setJustification] = useState("")
  const [loadingScopes, setLoadingScopes] = useState(true)
  const [loadingInteractions, setLoadingInteractions] = useState(false)
  const [declaring, setDeclaring] = useState(false)
  const [declareError, setDeclareError] = useState<ApiError | null>(null)
  const [declareMessage, setDeclareMessage] = useState<string | null>(null)

  async function loadList() {
    setLoadingList(true)
    setListError(null)
    try {
      const result = await listConnectivityRequirements(page)
      setRequirements(result.items)
      setHasMore(result.hasMore)
      setAmbiguousReadScopes(
        result.ambiguousScopes.map((item) => item.scope),
      )
    } catch (caught) {
      setListError(
        caught instanceof ApiError
          ? caught
          : new ApiError(
              500,
              "InternalError",
              "Connectivity Requirements could not be loaded.",
            ),
      )
    } finally {
      setLoadingList(false)
    }
  }

  async function loadAlignment() {
    setLoadingAlignment(true)
    setAlignmentError(null)
    try {
      const asOf = toOffsetAwareIso(alignmentAsOf)
      const result = await listConnectivityRequirementAlignment(asOf, page)
      setAlignmentById(
        Object.fromEntries(
          result.items.map((item) => [item.requirementId, item.status]),
        ),
      )
    } catch (caught) {
      setAlignmentById({})
      setAlignmentError(
        caught instanceof ApiError
          ? caught
          : new ApiError(
              422,
              "InvalidAsOf",
              "Select a valid alignment date and time.",
            ),
      )
    } finally {
      setLoadingAlignment(false)
    }
  }

  useEffect(() => {
    void loadList()
  }, [page])

  useEffect(() => {
    void loadAlignment()
  }, [page, alignmentAsOf])

  useEffect(() => {
    let active = true
    setLoadingScopes(true)
    void listConnectivityRequirementScopes()
      .then((result) => {
        if (!active) return
        const values = result.scopes.map((item) => item.scope)
        setScopes(values)
        setAmbiguousDeclareScopes(
          result.ambiguousScopes.map((item) => item.scope),
        )
        if (values.length === 1) setScope(values[0])
      })
      .catch((caught) => {
        if (!active) return
        setDeclareError(
          caught instanceof ApiError
            ? caught
            : new ApiError(
                500,
                "InternalError",
                "Declaration scopes could not be loaded.",
              ),
        )
      })
      .finally(() => {
        if (active) setLoadingScopes(false)
      })
    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setInteractionPage(1)
      setSearch(searchInput.trim())
    }, 300)
    return () => window.clearTimeout(timer)
  }, [searchInput])

  useEffect(() => {
    setInteractions([])
    setHasMoreInteractions(false)
    setSource("")
    setDestination("")
    setDcs("")
    setDependent("")
    if (!scope) return

    let active = true
    setLoadingInteractions(true)
    setDeclareError(null)
    void listConnectivityRequirementInteractions(
      scope,
      interactionPage,
      search,
    )
      .then((result) => {
        if (!active) return
        setInteractions(result.items)
        setHasMoreInteractions(result.hasMore)
      })
      .catch((caught) => {
        if (!active) return
        setDeclareError(
          caught instanceof ApiError
            ? caught
            : new ApiError(
                500,
                "InternalError",
                "Required interactions could not be loaded.",
              ),
        )
      })
      .finally(() => {
        if (active) setLoadingInteractions(false)
      })

    return () => {
      active = false
    }
  }, [scope, interactionPage, search])

  const sourceOptions = useMemo(() => {
    const values = new Map<string, string | null | undefined>()
    for (const item of interactions) {
      if (!values.has(item.sourceComponentDeploymentId)) {
        values.set(
          item.sourceComponentDeploymentId,
          item.catalogue?.sourceDisplayName,
        )
      }
    }
    return [...values.entries()]
  }, [interactions])

  const destinationOptions = useMemo(() => {
    const values = new Map<string, string | null | undefined>()
    for (const item of interactions) {
      if (item.sourceComponentDeploymentId !== source) continue
      if (!values.has(item.destinationComponentDeploymentId)) {
        values.set(
          item.destinationComponentDeploymentId,
          item.catalogue?.destinationDisplayName,
        )
      }
    }
    return [...values.entries()]
  }, [interactions, source])

  const dcsOptions = useMemo(
    () =>
      interactions.filter(
        (item) =>
          item.sourceComponentDeploymentId === source &&
          item.destinationComponentDeploymentId === destination,
      ),
    [interactions, source, destination],
  )

  const selectedInteraction =
    dcsOptions.find((item) => item.dcsContractRevisionId === dcs) ?? null

  function resetDeclaration() {
    setSource("")
    setDestination("")
    setDcs("")
    setDependent("")
    setApplicabilityKind("Ongoing")
    setWindowStart("")
    setWindowEnd("")
    setJustification("")
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    if (!scope || !source || !destination || !dcs || !dependent) return

    let applicability: RequirementApplicability
    try {
      applicability =
        applicabilityKind === "Ongoing"
          ? { kind: "Ongoing" }
          : {
              kind: "AbsoluteWindow",
              start: toOffsetAwareIso(windowStart),
              end: toOffsetAwareIso(windowEnd),
            }
    } catch {
      setDeclareError(
        new ApiError(
          422,
          "InvalidRequirementApplicability",
          "Select a valid applicability start and end.",
        ),
      )
      return
    }

    setDeclaring(true)
    setDeclareError(null)
    setDeclareMessage(null)
    try {
      const result = await declareConnectivityRequirement({
        authorityScope: scope,
        dependentComponentDeploymentId: dependent,
        sourceComponentDeploymentId: source,
        destinationComponentDeploymentId: destination,
        dcsContractRevisionId: dcs,
        applicability,
        justification,
      })
      setDeclareMessage(
        result.outcome === "Declared"
          ? "Connectivity Requirement declared."
          : "The same Active connectivity need already exists; existing Requirement resolved.",
      )
      resetDeclaration()
      await Promise.all([loadList(), loadAlignment()])
    } catch (caught) {
      setDeclareError(
        caught instanceof ApiError
          ? caught
          : new ApiError(
              500,
              "InternalError",
              "Connectivity Requirement could not be declared.",
            ),
      )
    } finally {
      setDeclaring(false)
    }
  }

  return (
    <div className="mx-auto max-w-[1380px]">
      <header className="mb-6">
        <div className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#64748B]">
          Connectivity Needs
        </div>
        <h1 className="text-[28px] font-bold tracking-tight text-[#172033]">
          My Connectivity Needs
        </h1>
        <p className="mt-2 max-w-4xl text-sm text-[#64748B]">
          Declare semantic connectivity that is required. A Requirement records need only:
          it does not mean the connection is Allowed, authorized by Access Policy, or configured.
        </p>
      </header>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_430px]">
        <section className="overflow-hidden rounded-lg border border-[#E2E8F0] bg-white">
          <div className="flex flex-wrap items-end justify-between gap-4 border-b border-[#E2E8F0] px-5 py-4">
            <div>
              <h2 className="text-base font-semibold text-[#172033]">
                Visible Connectivity Requirements
              </h2>
              <p className="mt-1 text-xs text-[#64748B]">Page {page}</p>
            </div>
            <Field
              label="Policy coverage as of"
              hint="Same logical time is used for Requirement applicability and Rule effectiveness."
            >
              <input
                type="datetime-local"
                step="1"
                value={alignmentAsOf}
                onChange={(event) => setAlignmentAsOf(event.target.value)}
                className="min-h-10 rounded-md border border-[#CBD5E1] px-3 py-2 text-sm"
              />
            </Field>
          </div>

          {ambiguousReadScopes.length > 0 ? (
            <div className="m-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
              {ambiguousReadScopes.length} scope(s) have ambiguous read authority and
              remain fail-closed.
            </div>
          ) : null}

          {listError ? (
            <div className="m-4 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800">
              <div className="font-semibold">{listError.code}</div>
              <div className="mt-1">{listError.message}</div>
            </div>
          ) : null}

          {alignmentError ? (
            <div className="m-4 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800">
              <div className="font-semibold">{alignmentError.code}</div>
              <div className="mt-1">{alignmentError.message}</div>
            </div>
          ) : null}

          {loadingList ? (
            <div className="p-8 text-sm text-[#64748B]">Loading Requirements…</div>
          ) : requirements.length === 0 ? (
            <div className="p-10 text-center">
              <div className="text-sm font-semibold text-[#334155]">
                No visible Connectivity Requirements
              </div>
              <div className="mt-2 text-sm text-[#64748B]">
                Declare the first semantic connectivity need from the form.
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[980px] text-left text-sm">
                <thead className="bg-[#F8FAFC] text-xs uppercase tracking-wide text-[#64748B]">
                  <tr>
                    <th className="px-4 py-3 font-semibold">Interaction</th>
                    <th className="px-4 py-3 font-semibold">Dependent</th>
                    <th className="px-4 py-3 font-semibold">Scope</th>
                    <th className="px-4 py-3 font-semibold">Applicability</th>
                    <th className="px-4 py-3 font-semibold">Policy coverage</th>
                    <th className="px-4 py-3 font-semibold">Lifecycle</th>
                    <th className="w-12 px-4 py-3" aria-label="Open" />
                  </tr>
                </thead>
                <tbody>
                  {requirements.map((item) => {
                    const interaction = item.requiredInteraction
                    const dependentName =
                      item.dependentComponentDeploymentId ===
                      interaction.sourceComponentDeploymentId
                        ? displayName(
                            item.catalogue?.sourceDisplayName,
                            interaction.sourceComponentDeploymentId,
                          )
                        : displayName(
                            item.catalogue?.destinationDisplayName,
                            interaction.destinationComponentDeploymentId,
                          )
                    return (
                      <tr
                        key={item.requirementId}
                        className="border-t border-[#E2E8F0] align-top hover:bg-[#F8FAFC]"
                      >
                        <td className="px-4 py-3">
                          <div className="font-medium text-[#172033]">
                            {displayName(
                              item.catalogue?.sourceDisplayName,
                              interaction.sourceComponentDeploymentId,
                            )}{" "}
                            →{" "}
                            {displayName(
                              item.catalogue?.destinationDisplayName,
                              interaction.destinationComponentDeploymentId,
                            )}
                          </div>
                          <div className="mt-1 text-xs text-[#64748B]">
                            {displayName(
                              item.catalogue?.dcsDisplayName,
                              interaction.dcsContractRevisionId,
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3">{dependentName}</td>
                        <td className="px-4 py-3">{item.governanceScope}</td>
                        <td className="px-4 py-3 text-xs text-[#475569]">
                          {applicabilityText(item.applicability)}
                        </td>
                        <td className="px-4 py-3">
                          {alignmentById[item.requirementId] ? (
                            <span
                              className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${alignmentClasses(alignmentById[item.requirementId])}`}
                              title={
                                alignmentById[item.requirementId] === "Uncovered"
                                  ? "No exact matching Access Rule contributes effective desired policy at the selected time. This does not mean Denied."
                                  : undefined
                              }
                            >
                              {alignmentById[item.requirementId]}
                            </span>
                          ) : loadingAlignment ? (
                            <span className="text-xs text-[#64748B]">Loading…</span>
                          ) : (
                            <span className="text-xs text-[#64748B]">—</span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${lifecycleClasses(item.lifecycleState)}`}
                          >
                            {item.lifecycleState}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <button
                            type="button"
                            aria-label={`Open Requirement ${item.requirementId}`}
                            className="grid size-8 place-items-center rounded-md text-[#64748B] hover:bg-[#E2E8F0]"
                            onClick={() => onOpenRequirement(item.requirementId)}
                          >
                            <ChevronRight className="size-4" aria-hidden="true" />
                          </button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}

          <div className="flex justify-end gap-2 border-t border-[#E2E8F0] px-5 py-4">
            <Button
              variant="secondary"
              disabled={page === 1 || loadingList}
              onClick={() => onPageChange(Math.max(1, page - 1))}
            >
              Previous
            </Button>
            <Button
              variant="secondary"
              disabled={!hasMore || loadingList}
              onClick={() => onPageChange(page + 1)}
            >
              Next
            </Button>
          </div>
        </section>

        <form
          onSubmit={submit}
          className="self-start rounded-lg border border-[#E2E8F0] bg-white p-5"
        >
          <div className="mb-5 flex items-center gap-2">
            <Plus className="size-4 text-[#2563EB]" aria-hidden="true" />
            <h2 className="text-base font-semibold text-[#172033]">
              Declare Connectivity Requirement
            </h2>
          </div>

          <div className="grid gap-4">
            <Field label="Requirement Governance Scope">
              <Select
                value={scope}
                onChange={(event) => {
                  setScope(event.target.value)
                  setInteractionPage(1)
                }}
                disabled={loadingScopes}
                required
              >
                <option value="">
                  {loadingScopes ? "Loading scopes…" : "Select scope"}
                </option>
                {scopes.map((value) => (
                  <option key={value} value={value}>
                    {value}
                  </option>
                ))}
              </Select>
            </Field>

            <Field label="Search required interaction">
              <div className="relative">
                <Search
                  className="pointer-events-none absolute left-3 top-3 size-4 text-[#94A3B8]"
                  aria-hidden="true"
                />
                <input
                  type="search"
                  value={searchInput}
                  maxLength={256}
                  onChange={(event) => setSearchInput(event.target.value)}
                  disabled={!scope}
                  placeholder="Orders, Checkout, HTTPS…"
                  className="min-h-10 w-full rounded-md border border-[#CBD5E1] py-2 pl-9 pr-3 text-sm disabled:bg-[#F8FAFC]"
                />
              </div>
            </Field>

            <Field label="Source Component Deployment">
              <Select
                value={source}
                onChange={(event) => {
                  setSource(event.target.value)
                  setDestination("")
                  setDcs("")
                  setDependent("")
                }}
                disabled={!scope || loadingInteractions}
                required
              >
                <option value="">Select source</option>
                {sourceOptions.map(([id, name]) => (
                  <option key={id} value={id}>
                    {optionLabel(name, id)}
                  </option>
                ))}
              </Select>
            </Field>

            <Field label="Destination Component Deployment">
              <Select
                value={destination}
                onChange={(event) => {
                  setDestination(event.target.value)
                  setDcs("")
                  setDependent("")
                }}
                disabled={!source}
                required
              >
                <option value="">Select destination</option>
                {destinationOptions.map(([id, name]) => (
                  <option key={id} value={id}>
                    {optionLabel(name, id)}
                  </option>
                ))}
              </Select>
            </Field>

            <Field label="Directed Communication Specification">
              <Select
                value={dcs}
                onChange={(event) => {
                  setDcs(event.target.value)
                  setDependent("")
                }}
                disabled={!destination}
                required
              >
                <option value="">Select DCS</option>
                {dcsOptions.map((item) => (
                  <option
                    key={item.dcsContractRevisionId}
                    value={item.dcsContractRevisionId}
                  >
                    {dcsLabel(item)}
                  </option>
                ))}
              </Select>
            </Field>

            <Field
              label="Dependent Component Deployment"
              hint="Whose operational/business concern requires this interaction?"
            >
              <Select
                value={dependent}
                onChange={(event) => setDependent(event.target.value)}
                disabled={!selectedInteraction}
                required
              >
                <option value="">Select dependent participant</option>
                {selectedInteraction ? (
                  <>
                    <option value={selectedInteraction.sourceComponentDeploymentId}>
                      {optionLabel(
                        selectedInteraction.catalogue?.sourceDisplayName,
                        selectedInteraction.sourceComponentDeploymentId,
                      )}
                    </option>
                    {selectedInteraction.destinationComponentDeploymentId !==
                    selectedInteraction.sourceComponentDeploymentId ? (
                      <option
                        value={
                          selectedInteraction.destinationComponentDeploymentId
                        }
                      >
                        {optionLabel(
                          selectedInteraction.catalogue?.destinationDisplayName,
                          selectedInteraction.destinationComponentDeploymentId,
                        )}
                      </option>
                    ) : null}
                  </>
                ) : null}
              </Select>
            </Field>

            <Field label="Applicability">
              <Select
                value={applicabilityKind}
                onChange={(event) =>
                  setApplicabilityKind(
                    event.target.value as "Ongoing" | "AbsoluteWindow",
                  )
                }
              >
                <option value="Ongoing">Ongoing</option>
                <option value="AbsoluteWindow">Absolute time window</option>
              </Select>
            </Field>

            {applicabilityKind === "AbsoluteWindow" ? (
              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1 2xl:grid-cols-2">
                <Field label="Start">
                  <input
                    type="datetime-local"
                    step="1"
                    value={windowStart}
                    onChange={(event) => setWindowStart(event.target.value)}
                    className="min-h-10 rounded-md border border-[#CBD5E1] px-3 py-2 text-sm"
                    required
                  />
                </Field>
                <Field label="End">
                  <input
                    type="datetime-local"
                    step="1"
                    value={windowEnd}
                    onChange={(event) => setWindowEnd(event.target.value)}
                    className="min-h-10 rounded-md border border-[#CBD5E1] px-3 py-2 text-sm"
                    required
                  />
                </Field>
              </div>
            ) : null}

            <Field
              label="Business justification"
              hint="Why is this semantic connectivity required?"
            >
              <textarea
                value={justification}
                onChange={(event) => setJustification(event.target.value)}
                maxLength={4096}
                rows={4}
                required
                className="w-full rounded-md border border-[#CBD5E1] px-3 py-2 text-sm"
              />
            </Field>

            <div className="flex items-center justify-between rounded-md border border-[#E2E8F0] bg-[#F8FAFC] px-3 py-2">
              <span className="text-xs text-[#64748B]">
                Interaction page {interactionPage}
              </span>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="secondary"
                  disabled={interactionPage === 1 || loadingInteractions}
                  onClick={() =>
                    setInteractionPage((value) => Math.max(1, value - 1))
                  }
                >
                  Previous
                </Button>
                <Button
                  type="button"
                  variant="secondary"
                  disabled={!hasMoreInteractions || loadingInteractions}
                  onClick={() => setInteractionPage((value) => value + 1)}
                >
                  Next
                </Button>
              </div>
            </div>

            {ambiguousDeclareScopes.length > 0 ? (
              <div className="rounded-md border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900">
                {ambiguousDeclareScopes.length} declaration scope(s) remain
                fail-closed because authority is ambiguous.
              </div>
            ) : null}

            {declareError ? (
              <div
                role="alert"
                className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800"
              >
                <div className="flex gap-2">
                  <CircleAlert className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
                  <div>
                    <div className="font-semibold">{declareError.code}</div>
                    <div className="mt-1">{declareError.message}</div>
                  </div>
                </div>
              </div>
            ) : null}

            {declareMessage ? (
              <div
                role="status"
                className="rounded-md border border-green-200 bg-green-50 p-3 text-sm text-green-800"
              >
                {declareMessage}
              </div>
            ) : null}

            <Button
              type="submit"
              loading={declaring}
              disabled={
                !scope ||
                !source ||
                !destination ||
                !dcs ||
                !dependent ||
                !justification.trim() ||
                (applicabilityKind === "AbsoluteWindow" &&
                  (!windowStart || !windowEnd))
              }
            >
              Declare Requirement
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
