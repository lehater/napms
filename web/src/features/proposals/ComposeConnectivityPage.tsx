import { useEffect, useMemo, useState } from "react"
import {
  ArrowRight,
  CheckCircle2,
  CircleAlert,
  Search,
  ShieldCheck,
} from "lucide-react"

import {
  ApiError,
  listProposalInteractions,
  listProposalScopes,
  submitProposal,
  type ProposalInteraction,
  type ProposalResult,
} from "@/api"
import {
  displayName,
  shortId,
  trafficAlternativeText,
} from "@/components/catalogue/CatalogueIdentity"
import { Button } from "@/components/ui/Button"
import { Field, Select } from "@/components/ui/Field"

function optionLabel(name: string | null | undefined, id: string) {
  const readable = name?.trim()
  return readable ? `${readable} · ${shortId(id)}` : shortId(id)
}

function dcsOptionLabel(item: ProposalInteraction) {
  const base = optionLabel(
    item.catalogue?.dcsDisplayName,
    item.dcsContractRevisionId,
  )
  const traffic = item.catalogue?.trafficAlternatives ?? []
  if (traffic.length === 0) return base
  return `${base} — ${traffic.map(trafficAlternativeText).join(" | ")}`
}

export function ComposeConnectivityPage() {
  const [scopes, setScopes] = useState<string[]>([])
  const [ambiguousScopes, setAmbiguousScopes] = useState<string[]>([])
  const [scope, setScope] = useState("")
  const [interactions, setInteractions] = useState<ProposalInteraction[]>([])
  const [interactionPage, setInteractionPage] = useState(1)
  const [hasMoreInteractions, setHasMoreInteractions] = useState(false)
  const [searchInput, setSearchInput] = useState("")
  const [search, setSearch] = useState("")
  const [source, setSource] = useState("")
  const [destination, setDestination] = useState("")
  const [dcs, setDcs] = useState("")
  const [loadingScopes, setLoadingScopes] = useState(true)
  const [loadingInteractions, setLoadingInteractions] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)
  const [result, setResult] = useState<ProposalResult | null>(null)

  useEffect(() => {
    let active = true
    void listProposalScopes()
      .then((payload) => {
        if (!active) return
        const values = payload.scopes.map((item) => item.scope)
        setScopes(values)
        setAmbiguousScopes(payload.ambiguousScopes.map((item) => item.scope))
        if (values.length === 1) setScope(values[0])
      })
      .catch((caught) => {
        if (active) {
          setError(
            caught instanceof ApiError
              ? caught
              : new ApiError(500, "InternalError", "Scopes could not be loaded."),
          )
        }
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
    setResult(null)
    if (!scope) return

    let active = true
    setLoadingInteractions(true)
    setError(null)
    void listProposalInteractions(scope, interactionPage, search)
      .then((response) => {
        if (!active) return
        setInteractions(response.items)
        setHasMoreInteractions(response.hasMore)
      })
      .catch((caught) => {
        if (active) {
          setError(
            caught instanceof ApiError
              ? caught
              : new ApiError(
                  500,
                  "InternalError",
                  "Available interactions could not be loaded.",
                ),
          )
        }
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

  const dcsOptions = useMemo(() => {
    const values = new Map<string, ProposalInteraction>()
    for (const item of interactions) {
      if (
        item.sourceComponentDeploymentId === source &&
        item.destinationComponentDeploymentId === destination &&
        !values.has(item.dcsContractRevisionId)
      ) {
        values.set(item.dcsContractRevisionId, item)
      }
    }
    return [...values.values()]
  }, [interactions, source, destination])

  const selectedInteraction = useMemo(
    () =>
      interactions.find(
        (item) =>
          item.sourceComponentDeploymentId === source &&
          item.destinationComponentDeploymentId === destination &&
          item.dcsContractRevisionId === dcs,
      ) ?? null,
    [interactions, source, destination, dcs],
  )

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    if (!scope || !source || !destination || !dcs) return

    setSubmitting(true)
    setError(null)
    setResult(null)
    try {
      const response = await submitProposal({
        authorityScope: scope,
        sourceComponentDeploymentId: source,
        destinationComponentDeploymentId: destination,
        dcsContractRevisionId: dcs,
      })
      setResult(response)
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught
          : new ApiError(500, "InternalError", "The proposal could not be submitted."),
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-[1180px]">
      <header className="mb-6">
        <div className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#64748B]">
          Access Policy
        </div>
        <h1 className="text-[28px] font-bold tracking-tight text-[#172033]">
          Compose Connectivity
        </h1>
        <p className="mt-2 max-w-3xl text-sm text-[#64748B]">
          Select a valid application-backed interaction. Human-readable catalogue
          labels are presentation metadata; stable deployment and DCS IDs remain the
          proposal identity.
        </p>
      </header>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
        <form
          onSubmit={submit}
          className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6"
        >
          <div className="mb-5 flex items-center justify-between gap-4">
            <div>
              <h2 className="text-base font-semibold text-[#172033]">
                Proposal identity
              </h2>
              <p className="mt-1 text-sm text-[#64748B]">
                Only authorized catalogue-backed directed interactions are selectable.
              </p>
            </div>
            <div className="rounded-md bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700">
              local-dev
            </div>
          </div>

          <div className="grid gap-5">
            <Field label="Governance scope">
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

            <Field
              label="Search interactions"
              hint="Server-side search by deployment label, DCS label or stable UUID."
            >
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
                  placeholder="e.g. Orders, Checkout, HTTPS"
                  className="min-h-10 w-full rounded-md border border-[#CBD5E1] bg-white py-2 pl-9 pr-3 text-sm disabled:bg-[#F8FAFC]"
                />
              </div>
            </Field>

            <div className="grid gap-5 lg:grid-cols-2">
              <Field
                label="Source Component Deployment"
                hint="Readable label first; stable deployment ID remains visible."
              >
                <Select
                  value={source}
                  onChange={(event) => {
                    setSource(event.target.value)
                    setDestination("")
                    setDcs("")
                    setResult(null)
                  }}
                  disabled={!scope || loadingInteractions}
                  required
                >
                  <option value="">
                    {loadingInteractions ? "Loading interactions…" : "Select source"}
                  </option>
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
                    setResult(null)
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
            </div>

            <Field
              label="Directed Communication Specification revision"
              hint="DCS label plus decoded immutable traffic summary."
            >
              <Select
                value={dcs}
                onChange={(event) => {
                  setDcs(event.target.value)
                  setResult(null)
                }}
                disabled={!destination}
                required
              >
                <option value="">Select DCS revision</option>
                {dcsOptions.map((item) => (
                  <option
                    key={item.dcsContractRevisionId}
                    value={item.dcsContractRevisionId}
                  >
                    {dcsOptionLabel(item)}
                  </option>
                ))}
              </Select>
            </Field>

            {selectedInteraction ? (
              <div className="rounded-md border border-[#E2E8F0] bg-[#F8FAFC] p-4 text-sm">
                <div className="font-semibold text-[#172033]">
                  {displayName(
                    selectedInteraction.catalogue?.sourceDisplayName,
                    selectedInteraction.sourceComponentDeploymentId,
                  )}{" "}
                  →{" "}
                  {displayName(
                    selectedInteraction.catalogue?.destinationDisplayName,
                    selectedInteraction.destinationComponentDeploymentId,
                  )}
                </div>
                <div className="mt-1 text-[#475569]">
                  {displayName(
                    selectedInteraction.catalogue?.dcsDisplayName,
                    selectedInteraction.dcsContractRevisionId,
                  )}
                </div>
                {(selectedInteraction.catalogue?.trafficAlternatives.length ?? 0) > 0 ? (
                  <div className="mt-2 grid gap-1 text-xs text-[#64748B]">
                    {selectedInteraction.catalogue?.trafficAlternatives.map(
                      (alternative, index) => (
                        <div key={index}>{trafficAlternativeText(alternative)}</div>
                      ),
                    )}
                  </div>
                ) : null}
              </div>
            ) : null}

            {!loadingInteractions && scope && interactions.length === 0 ? (
              <div className="rounded-md border border-[#E2E8F0] bg-[#F8FAFC] p-4 text-sm text-[#64748B]">
                {search
                  ? "No authorized interactions match this search."
                  : "No authorized interactions are available in this scope."}
              </div>
            ) : null}

            <div className="flex items-center justify-between rounded-md border border-[#E2E8F0] bg-[#F8FAFC] px-3 py-2">
              <span className="text-xs text-[#64748B]">
                Interaction page {interactionPage}
                {search ? ` · search: ${search}` : ""}
              </span>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="secondary"
                  disabled={interactionPage === 1 || loadingInteractions}
                  onClick={() => setInteractionPage((value) => Math.max(1, value - 1))}
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

            {error ? (
              <div
                role="alert"
                className="rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800"
              >
                <div className="flex gap-3">
                  <CircleAlert className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
                  <div>
                    <div className="font-semibold">{error.code}</div>
                    <div className="mt-1">{error.message}</div>
                    {error.correlationId ? (
                      <div className="mt-2 text-xs text-red-700">
                        Correlation: {error.correlationId}
                      </div>
                    ) : null}
                  </div>
                </div>
              </div>
            ) : null}

            <div className="flex justify-end border-t border-[#E2E8F0] pt-5">
              <Button
                type="submit"
                loading={submitting}
                disabled={!scope || !source || !destination || !dcs}
              >
                Submit proposal
                <ArrowRight className="size-4" aria-hidden="true" />
              </Button>
            </div>
          </div>
        </form>

        <aside className="grid content-start gap-4">
          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5">
            <div className="flex items-center gap-2 text-sm font-semibold text-[#172033]">
              <ShieldCheck className="size-4 text-[#2563EB]" aria-hidden="true" />
              Decision boundary
            </div>
            <p className="mt-2 text-sm leading-6 text-[#64748B]">
              In local-dev, structurally valid and authorized proposals use the explicit
              <code className="mx-1 rounded bg-[#F1F5F9] px-1 py-0.5 text-xs">
                local-dev:allowed
              </code>
              decision adapter.
            </p>
          </section>

          {ambiguousScopes.length > 0 ? (
            <section className="rounded-lg border border-amber-200 bg-amber-50 p-5 text-sm text-amber-900">
              <div className="font-semibold">Authority ambiguity detected</div>
              <p className="mt-2">
                {ambiguousScopes.length} scope(s) are hidden from permitted choices and
                remain fail-closed.
              </p>
            </section>
          ) : null}

          {result ? (
            <section
              className={
                result.outcome === "NotAllowed"
                  ? "rounded-lg border border-red-200 bg-red-50 p-5"
                  : "rounded-lg border border-green-200 bg-green-50 p-5"
              }
              aria-live="polite"
            >
              {result.outcome === "NotAllowed" ? (
                <>
                  <div className="font-semibold text-red-800">NotAllowed</div>
                  <p className="mt-2 text-sm text-red-700">
                    The proposal produced no authoritative Access Rule.
                  </p>
                </>
              ) : (
                <>
                  <div className="flex items-center gap-2 font-semibold text-green-800">
                    <CheckCircle2 className="size-4" aria-hidden="true" />
                    {result.outcome}
                  </div>
                  <dl className="mt-4 grid gap-3 text-sm">
                    <div>
                      <dt className="text-xs uppercase tracking-wide text-green-700">
                        Interaction
                      </dt>
                      <dd className="mt-1 text-green-950">
                        {displayName(
                          result.rule.catalogue?.sourceDisplayName,
                          result.rule.semanticIdentity.sourceComponentDeploymentId,
                        )}{" "}
                        →{" "}
                        {displayName(
                          result.rule.catalogue?.destinationDisplayName,
                          result.rule.semanticIdentity.destinationComponentDeploymentId,
                        )}
                      </dd>
                      <dd className="mt-1 text-xs text-green-800">
                        {displayName(
                          result.rule.catalogue?.dcsDisplayName,
                          result.rule.semanticIdentity.dcsContractRevisionId,
                        )}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-xs uppercase tracking-wide text-green-700">
                        Rule ID
                      </dt>
                      <dd className="mt-1 break-all font-mono text-green-950">
                        {result.rule.ruleId}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-xs uppercase tracking-wide text-green-700">
                        State
                      </dt>
                      <dd className="mt-1 font-semibold text-green-950">
                        {result.rule.operationalState}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-xs uppercase tracking-wide text-green-700">
                        Decision
                      </dt>
                      <dd className="mt-1 break-all font-mono text-green-950">
                        {result.rule.decisionReference ?? "—"}
                      </dd>
                    </div>
                  </dl>
                </>
              )}
            </section>
          ) : null}
        </aside>
      </div>
    </div>
  )
}
