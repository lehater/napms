import { useEffect, useMemo, useState } from "react"
import { ArrowRight, CheckCircle2, CircleAlert, ShieldCheck } from "lucide-react"

import {
  ApiError,
  listProposalInteractions,
  listProposalScopes,
  submitProposal,
  type ProposalInteraction,
  type ProposalResult,
} from "@/api"
import { Button } from "@/components/ui/Button"
import { Field, Select } from "@/components/ui/Field"

function shortId(value: string) {
  return value.length <= 18 ? value : `${value.slice(0, 8)}…${value.slice(-6)}`
}

function unique(values: string[]) {
  return [...new Set(values)]
}

export function ComposeConnectivityPage() {
  const [scopes, setScopes] = useState<string[]>([])
  const [ambiguousScopes, setAmbiguousScopes] = useState<string[]>([])
  const [scope, setScope] = useState("")
  const [interactions, setInteractions] = useState<ProposalInteraction[]>([])
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
    setInteractions([])
    setSource("")
    setDestination("")
    setDcs("")
    setResult(null)
    if (!scope) return

    let active = true
    setLoadingInteractions(true)
    setError(null)
    void listProposalInteractions(scope)
      .then((items) => {
        if (active) setInteractions(items)
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
  }, [scope])

  const sources = useMemo(
    () => unique(interactions.map((item) => item.sourceComponentDeploymentId)),
    [interactions],
  )
  const destinations = useMemo(
    () =>
      unique(
        interactions
          .filter((item) => item.sourceComponentDeploymentId === source)
          .map((item) => item.destinationComponentDeploymentId),
      ),
    [interactions, source],
  )
  const dcsOptions = useMemo(
    () =>
      unique(
        interactions
          .filter(
            (item) =>
              item.sourceComponentDeploymentId === source &&
              item.destinationComponentDeploymentId === destination,
          )
          .map((item) => item.dcsContractRevisionId),
      ),
    [interactions, source, destination],
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
          Select a valid application-backed interaction. NAPMS validates authority and
          consumes the connectivity decision before an Access Rule can exist.
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
                Only catalogue-backed directed interactions are selectable.
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
                onChange={(event) => setScope(event.target.value)}
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

            <div className="grid gap-5 lg:grid-cols-2">
              <Field
                label="Source Component Deployment"
                hint="Stable deployment identity from Application Communication Catalogue."
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
                  {sources.map((value) => (
                    <option key={value} value={value}>
                      {shortId(value)}
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
                  {destinations.map((value) => (
                    <option key={value} value={value}>
                      {shortId(value)}
                    </option>
                  ))}
                </Select>
              </Field>
            </div>

            <Field
              label="Directed Communication Specification revision"
              hint="Immutable decision-relevant DCS revision."
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
                {dcsOptions.map((value) => (
                  <option key={value} value={value}>
                    {shortId(value)}
                  </option>
                ))}
              </Select>
            </Field>

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
