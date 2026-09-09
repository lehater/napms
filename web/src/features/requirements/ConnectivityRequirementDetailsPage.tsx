import { useEffect, useState } from "react"
import { ArrowLeft, CircleAlert } from "lucide-react"

import {
  ApiError,
  getConnectivityRequirement,
  getConnectivityRequirementAlignment,
  retireConnectivityRequirement,
  setConnectivityRequirementApplicability,
  setConnectivityRequirementJustification,
  type ConnectivityRequirementDetailResponse,
  type RequirementApplicability,
  type RequirementPolicyAlignmentDetail,
  type RequirementPolicyAlignmentStatus,
} from "@/api"
import {
  CatalogueIdentity,
  displayName,
  trafficAlternativeText,
} from "@/components/catalogue/CatalogueIdentity"
import { Button } from "@/components/ui/Button"
import { Field, Select } from "@/components/ui/Field"
import {
  nowLocalDateTimeInput,
  toLocalDateTimeInput,
  toOffsetAwareIso,
} from "@/lib/datetime"

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

function alignmentExplanation(status: RequirementPolicyAlignmentStatus) {
  switch (status) {
    case "Covered":
      return "An exact matching Access Rule contributes effective desired policy at this time."
    case "Uncovered":
      return "No exact matching Access Rule contributes effective desired policy at this time. This does not mean Denied."
    case "NotCurrent":
      return "The Requirement is retired or outside its applicability at this time."
    case "Unknown":
      return "Authoritative policy coverage cannot be established safely at this time."
  }
}

function applicabilityText(value: RequirementApplicability) {
  return value.kind === "Ongoing"
    ? "Ongoing"
    : `${value.start} → ${value.end}`
}

export function ConnectivityRequirementDetailsPage({
  requirementId,
  onBack,
}: {
  requirementId: string
  onBack: () => void
}) {
  const [detail, setDetail] =
    useState<ConnectivityRequirementDetailResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [mutating, setMutating] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  const [alignmentAsOf, setAlignmentAsOf] = useState(
    nowLocalDateTimeInput(),
  )
  const [alignment, setAlignment] =
    useState<RequirementPolicyAlignmentDetail | null>(null)
  const [loadingAlignment, setLoadingAlignment] = useState(true)
  const [alignmentError, setAlignmentError] = useState<ApiError | null>(null)

  const [applicabilityKind, setApplicabilityKind] =
    useState<"Ongoing" | "AbsoluteWindow">("Ongoing")
  const [windowStart, setWindowStart] = useState("")
  const [windowEnd, setWindowEnd] = useState("")
  const [justification, setJustification] = useState("")

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const response = await getConnectivityRequirement(requirementId)
      setDetail(response)
      setJustification(response.requirement.justification)
      if (response.requirement.applicability.kind === "Ongoing") {
        setApplicabilityKind("Ongoing")
        setWindowStart("")
        setWindowEnd("")
      } else {
        setApplicabilityKind("AbsoluteWindow")
        setWindowStart(
          toLocalDateTimeInput(response.requirement.applicability.start),
        )
        setWindowEnd(
          toLocalDateTimeInput(response.requirement.applicability.end),
        )
      }
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught
          : new ApiError(
              500,
              "InternalError",
              "Connectivity Requirement could not be loaded.",
            ),
      )
    } finally {
      setLoading(false)
    }
  }

  async function loadAlignment() {
    setLoadingAlignment(true)
    setAlignmentError(null)
    try {
      const asOf = toOffsetAwareIso(alignmentAsOf)
      setAlignment(
        await getConnectivityRequirementAlignment(requirementId, asOf),
      )
    } catch (caught) {
      setAlignment(null)
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
    void load()
  }, [requirementId])

  useEffect(() => {
    void loadAlignment()
  }, [requirementId, alignmentAsOf])

  async function saveApplicability() {
    if (
      !detail ||
      detail.requirement.lifecycleState === "Retired" ||
      detail.capabilities.setApplicability !== "Permitted"
    ) {
      return
    }

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
      setError(
        new ApiError(
          422,
          "InvalidRequirementApplicability",
          "Select a valid applicability start and end.",
        ),
      )
      return
    }

    setMutating(true)
    setError(null)
    setMessage(null)
    try {
      const result = await setConnectivityRequirementApplicability(
        requirementId,
        applicability,
      )
      setMessage(
        result.outcome === "Updated"
          ? "Requirement applicability updated."
          : "Requirement already has this applicability.",
      )
      await Promise.all([load(), loadAlignment()])
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught
          : new ApiError(
              500,
              "InternalError",
              "Applicability could not be changed.",
            ),
      )
    } finally {
      setMutating(false)
    }
  }

  async function saveJustification() {
    if (
      !detail ||
      detail.requirement.lifecycleState === "Retired" ||
      detail.capabilities.setJustification !== "Permitted"
    ) {
      return
    }

    setMutating(true)
    setError(null)
    setMessage(null)
    try {
      const result = await setConnectivityRequirementJustification(
        requirementId,
        justification,
      )
      setMessage(
        result.outcome === "Updated"
          ? "Requirement justification updated."
          : "Requirement already has this justification.",
      )
      await Promise.all([load(), loadAlignment()])
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught
          : new ApiError(
              500,
              "InternalError",
              "Justification could not be changed.",
            ),
      )
    } finally {
      setMutating(false)
    }
  }

  async function retire() {
    if (
      !detail ||
      detail.requirement.lifecycleState === "Retired" ||
      detail.capabilities.retire !== "Permitted"
    ) {
      return
    }

    setMutating(true)
    setError(null)
    setMessage(null)
    try {
      const result = await retireConnectivityRequirement(requirementId)
      setMessage(
        result.outcome === "Retired"
          ? "Connectivity Requirement retired."
          : "Connectivity Requirement is already retired.",
      )
      await Promise.all([load(), loadAlignment()])
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught
          : new ApiError(
              500,
              "InternalError",
              "Connectivity Requirement could not be retired.",
            ),
      )
    } finally {
      setMutating(false)
    }
  }

  const requirement = detail?.requirement
  const interaction = requirement?.requiredInteraction

  return (
    <div className="mx-auto max-w-[1180px]">
      <div className="mb-4">
        <Button variant="ghost" onClick={onBack}>
          <ArrowLeft className="size-4" aria-hidden="true" />
          My Connectivity Needs
        </Button>
      </div>

      <header className="mb-6">
        <div className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#5F6B7D]">
          Connectivity Needs / Requirement Details
        </div>
        <h1 className="break-all text-[28px] font-bold tracking-tight text-[#172033]">
          {requirementId}
        </h1>
        {requirement && interaction ? (
          <p className="mt-2 text-sm text-[#5F6B7D]">
            {displayName(
              requirement.catalogue?.sourceDisplayName,
              interaction.sourceComponentDeploymentId,
            )}{" "}
            →{" "}
            {displayName(
              requirement.catalogue?.destinationDisplayName,
              interaction.destinationComponentDeploymentId,
            )}{" "}
            ·{" "}
            {displayName(
              requirement.catalogue?.dcsDisplayName,
              interaction.dcsContractRevisionId,
            )}
          </p>
        ) : null}
      </header>

      {error ? (
        <div
          role="alert"
          className="mb-4 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800"
        >
          <div className="flex gap-3">
            <CircleAlert className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
            <div>
              <div className="font-semibold">{error.code}</div>
              <div className="mt-1">{error.message}</div>
              {error.correlationId ? (
                <div className="mt-2 text-xs">
                  Correlation: {error.correlationId}
                </div>
              ) : null}
            </div>
          </div>
        </div>
      ) : null}

      {message ? (
        <div
          role="status"
          className="mb-4 rounded-md border border-green-200 bg-green-50 p-4 text-sm text-green-800"
        >
          {message}
        </div>
      ) : null}

      {loading && !detail ? (
        <div className="rounded-lg border border-[#E2E8F0] bg-white p-8 text-sm text-[#5F6B7D]">
          Loading Connectivity Requirement…
        </div>
      ) : requirement && detail && interaction ? (
        <div className="grid gap-6">
          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div>
                <h2 className="text-base font-semibold text-[#172033]">
                  Policy coverage
                </h2>
                <p className="mt-1 max-w-3xl text-sm text-[#5F6B7D]">
                  Derived from this Requirement and effective Access Policy at one explicit logical time. It does not report configured/observed access.
                </p>
              </div>
              <Field label="Alignment as of">
                <input
                  type="datetime-local"
                  step="1"
                  value={alignmentAsOf}
                  onChange={(event) => setAlignmentAsOf(event.target.value)}
                  className="min-h-10 rounded-md border border-[#CBD5E1] px-3 py-2 text-sm"
                />
              </Field>
            </div>

            {alignmentError ? (
              <div className="mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800">
                <div className="font-semibold">{alignmentError.code}</div>
                <div className="mt-1">{alignmentError.message}</div>
              </div>
            ) : loadingAlignment ? (
              <div className="mt-4 text-sm text-[#5F6B7D]">
                Loading policy coverage…
              </div>
            ) : alignment ? (
              <div className="mt-4">
                <span
                  className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${alignmentClasses(alignment.status)}`}
                >
                  {alignment.status}
                </span>
                <p className="mt-3 text-sm text-[#475569]">
                  {alignmentExplanation(alignment.status)}
                </p>
                <div className="mt-2 text-xs text-[#5F6B7D]">
                  asOf {alignment.asOf}
                </div>
              </div>
            ) : null}
          </section>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h2 className="text-base font-semibold text-[#172033]">
                  Requirement lifecycle
                </h2>
                <div className="mt-3 flex items-center gap-3">
                  <span
                    className={
                      requirement.lifecycleState === "Active"
                        ? "inline-flex rounded-full border border-green-200 bg-green-50 px-2.5 py-1 text-xs font-semibold text-green-800"
                        : "inline-flex rounded-full border border-slate-200 bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700"
                    }
                  >
                    {requirement.lifecycleState}
                  </span>
                  <span className="text-xs text-[#5F6B7D]">
                    aggregate version {requirement.version}
                  </span>
                </div>
                <p className="mt-3 max-w-3xl text-sm text-[#5F6B7D]">
                  This lifecycle records whether the need remains current. It is not an
                  approval or connectivity-decision status.
                </p>
              </div>
              {requirement.lifecycleState === "Active" &&
              detail.capabilities.retire === "Permitted" ? (
                <Button
                  variant="secondary"
                  loading={mutating}
                  onClick={() => void retire()}
                >
                  Retire Requirement
                </Button>
              ) : null}
            </div>
          </section>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <h2 className="text-base font-semibold text-[#172033]">
              Required semantic interaction
            </h2>
            <dl className="mt-4 grid gap-5 lg:grid-cols-2">
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#5F6B7D]">
                  Source Component Deployment
                </dt>
                <dd className="mt-1">
                  <CatalogueIdentity
                    name={requirement.catalogue?.sourceDisplayName}
                    id={interaction.sourceComponentDeploymentId}
                  />
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#5F6B7D]">
                  Destination Component Deployment
                </dt>
                <dd className="mt-1">
                  <CatalogueIdentity
                    name={requirement.catalogue?.destinationDisplayName}
                    id={interaction.destinationComponentDeploymentId}
                  />
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#5F6B7D]">
                  DCS revision
                </dt>
                <dd className="mt-1">
                  <CatalogueIdentity
                    name={requirement.catalogue?.dcsDisplayName}
                    id={interaction.dcsContractRevisionId}
                  />
                  {(requirement.catalogue?.trafficAlternatives.length ?? 0) > 0 ? (
                    <div className="mt-2 grid gap-1 text-xs text-[#5F6B7D]">
                      {requirement.catalogue?.trafficAlternatives.map(
                        (alternative, index) => (
                          <div key={index}>
                            {trafficAlternativeText(alternative)}
                          </div>
                        ),
                      )}
                    </div>
                  ) : null}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#5F6B7D]">
                  Dependent Component Deployment
                </dt>
                <dd className="mt-1">
                  {requirement.dependentComponentDeploymentId ===
                  interaction.sourceComponentDeploymentId ? (
                    <CatalogueIdentity
                      name={requirement.catalogue?.sourceDisplayName}
                      id={requirement.dependentComponentDeploymentId}
                    />
                  ) : (
                    <CatalogueIdentity
                      name={requirement.catalogue?.destinationDisplayName}
                      id={requirement.dependentComponentDeploymentId}
                    />
                  )}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#5F6B7D]">
                  Requirement Governance Scope
                </dt>
                <dd className="mt-1 text-sm">{requirement.governanceScope}</dd>
              </div>
            </dl>
          </section>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h2 className="text-base font-semibold text-[#172033]">
                  Applicability
                </h2>
                <p className="mt-1 text-sm text-[#5F6B7D]">
                  Current: {applicabilityText(requirement.applicability)}
                </p>
                <div className="mt-1 text-xs text-[#5F6B7D]">
                  mutation: {detail.capabilities.setApplicability}
                </div>
              </div>
            </div>

            <div className="mt-5 grid gap-4">
              <Field label="Applicability kind">
                <Select
                  value={applicabilityKind}
                  disabled={
                    requirement.lifecycleState === "Retired" ||
                    detail.capabilities.setApplicability !== "Permitted"
                  }
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
                <div className="grid gap-4 md:grid-cols-2">
                  <Field label="Start">
                    <input
                      type="datetime-local"
                      step="1"
                      value={windowStart}
                      onChange={(event) => setWindowStart(event.target.value)}
                      disabled={
                        requirement.lifecycleState === "Retired" ||
                        detail.capabilities.setApplicability !== "Permitted"
                      }
                      className="min-h-10 rounded-md border border-[#CBD5E1] px-3 py-2 text-sm disabled:bg-[#F8FAFC]"
                    />
                  </Field>
                  <Field label="End">
                    <input
                      type="datetime-local"
                      step="1"
                      value={windowEnd}
                      onChange={(event) => setWindowEnd(event.target.value)}
                      disabled={
                        requirement.lifecycleState === "Retired" ||
                        detail.capabilities.setApplicability !== "Permitted"
                      }
                      className="min-h-10 rounded-md border border-[#CBD5E1] px-3 py-2 text-sm disabled:bg-[#F8FAFC]"
                    />
                  </Field>
                </div>
              ) : null}

              {requirement.lifecycleState === "Active" &&
              detail.capabilities.setApplicability === "Permitted" ? (
                <div className="flex justify-end">
                  <Button
                    loading={mutating}
                    disabled={
                      applicabilityKind === "AbsoluteWindow" &&
                      (!windowStart || !windowEnd)
                    }
                    onClick={() => void saveApplicability()}
                  >
                    Save applicability
                  </Button>
                </div>
              ) : null}
            </div>
          </section>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <h2 className="text-base font-semibold text-[#172033]">
              Business justification
            </h2>
            <p className="mt-1 text-xs text-[#5F6B7D]">
              mutation: {detail.capabilities.setJustification}
            </p>
            <textarea
              value={justification}
              onChange={(event) => setJustification(event.target.value)}
              rows={4}
              maxLength={4096}
              disabled={
                requirement.lifecycleState === "Retired" ||
                detail.capabilities.setJustification !== "Permitted"
              }
              className="mt-4 w-full rounded-md border border-[#CBD5E1] px-3 py-2 text-sm disabled:bg-[#F8FAFC]"
            />
            {requirement.lifecycleState === "Active" &&
            detail.capabilities.setJustification === "Permitted" ? (
              <div className="mt-4 flex justify-end">
                <Button
                  loading={mutating}
                  disabled={!justification.trim()}
                  onClick={() => void saveJustification()}
                >
                  Save justification
                </Button>
              </div>
            ) : null}
          </section>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <h2 className="text-base font-semibold text-[#172033]">
              Declaration provenance
            </h2>
            <dl className="mt-4 grid gap-4 text-sm lg:grid-cols-2">
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#5F6B7D]">
                  Actor
                </dt>
                <dd className="mt-1">
                  {requirement.declarationProvenance.actorId}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#5F6B7D]">
                  Effective time
                </dt>
                <dd className="mt-1">
                  {requirement.declarationProvenance.effectiveTime}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#5F6B7D]">
                  Authority reference
                </dt>
                <dd className="mt-1 break-all font-mono text-xs">
                  {requirement.declarationProvenance.authorityReference}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-[#5F6B7D]">
                  Catalogue reference
                </dt>
                <dd className="mt-1 break-all font-mono text-xs">
                  {requirement.declarationProvenance.catalogueReference ?? "—"}
                </dd>
              </div>
            </dl>
          </section>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <h2 className="text-base font-semibold text-[#172033]">
              Applicability history
            </h2>
            {requirement.applicabilityHistory.length === 0 ? (
              <p className="mt-3 text-sm text-[#5F6B7D]">
                No applicability changes have been recorded.
              </p>
            ) : (
              <div className="mt-4 grid gap-3">
                {requirement.applicabilityHistory.map((change, index) => (
                  <div
                    key={`${change.effectiveTime}-app-${index}`}
                    className="rounded-md border border-[#E2E8F0] p-3 text-sm"
                  >
                    <div>
                      {applicabilityText(change.previousApplicability)} →{" "}
                      {applicabilityText(change.newApplicability)}
                    </div>
                    <div className="mt-1 text-xs text-[#5F6B7D]">
                      {change.actorId} · {change.effectiveTime} ·{" "}
                      {change.authorityReference}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <h2 className="text-base font-semibold text-[#172033]">
              Justification history
            </h2>
            {requirement.justificationHistory.length === 0 ? (
              <p className="mt-3 text-sm text-[#5F6B7D]">
                No justification changes have been recorded.
              </p>
            ) : (
              <div className="mt-4 grid gap-3">
                {requirement.justificationHistory.map((change, index) => (
                  <div
                    key={`${change.effectiveTime}-reason-${index}`}
                    className="rounded-md border border-[#E2E8F0] p-3 text-sm"
                  >
                    <div>
                      <span className="text-[#5F6B7D]">
                        {change.previousJustification}
                      </span>{" "}
                      → {change.newJustification}
                    </div>
                    <div className="mt-1 text-xs text-[#5F6B7D]">
                      {change.actorId} · {change.effectiveTime} ·{" "}
                      {change.authorityReference}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
            <h2 className="text-base font-semibold text-[#172033]">
              Lifecycle history
            </h2>
            {requirement.lifecycleHistory.length === 0 ? (
              <p className="mt-3 text-sm text-[#5F6B7D]">
                Requirement has not been retired.
              </p>
            ) : (
              <div className="mt-4 grid gap-3">
                {requirement.lifecycleHistory.map((change, index) => (
                  <div
                    key={`${change.effectiveTime}-life-${index}`}
                    className="rounded-md border border-[#E2E8F0] p-3 text-sm"
                  >
                    <div>
                      {change.fromState} → {change.toState}
                    </div>
                    <div className="mt-1 text-xs text-[#5F6B7D]">
                      {change.actorId} · {change.effectiveTime} ·{" "}
                      {change.authorityReference}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      ) : null}
    </div>
  )
}
