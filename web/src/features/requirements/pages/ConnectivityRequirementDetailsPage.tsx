import { useEffect, useState } from "react"
import { ArrowLeft } from "lucide-react"

import { Alert } from "@/design-system/components/Alert"
import { Button } from "@/design-system/components/Button"
import { Field, Input, Select, Textarea } from "@/design-system/components/Field"
import { PageWorkspace } from "@/design-system/layout/PageWorkspace"
import { DetailSection } from "@/design-system/patterns/detail/Detail"
import { displayName } from "@/features/catalogues/components/CatalogueIdentity"
import {
  getConnectivityRequirement,
  getConnectivityRequirementAlignment,
  retireConnectivityRequirement,
  setConnectivityRequirementApplicability,
  setConnectivityRequirementJustification,
  type ConnectivityRequirementDetailResponse,
  type RequirementApplicability,
  type RequirementPolicyAlignmentDetail,
  type RequirementPolicyAlignmentStatus,
} from "@/features/requirements/api"
import {
  RequirementHistorySections,
  RequirementInteractionSection,
  RequirementProvenanceSection,
  applicabilityDisplay,
} from "@/features/requirements/components/RequirementDetailSections"
import {
  RequirementAlignmentStatus,
  RequirementLifecycleStatus,
} from "@/features/requirements/components/RequirementStatus"
import { ApiError } from "@/lib/api"
import {
  nowLocalDateTimeInput,
  toLocalDateTimeInput,
  toOffsetAwareIso,
} from "@/lib/datetime"

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
    <PageWorkspace width="content">
      <div>
        <Button variant="ghost" onClick={onBack}>
          <ArrowLeft className="size-4" aria-hidden="true" />
          My Connectivity Needs
        </Button>
      </div>

      <header>
        <div className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-[var(--napms-color-text-secondary)]">
          Connectivity Needs / Requirement Details
        </div>
        <h1 className="break-all text-2xl font-bold tracking-tight text-[var(--napms-color-text-primary)]">
          {requirementId}
        </h1>
        {requirement && interaction ? (
          <p className="mt-2 text-sm text-[var(--napms-color-text-secondary)]">
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
        <Alert role="alert" tone="danger">
          <div className="font-semibold">{error.code}</div>
          <div className="mt-1">{error.message}</div>
          {error.correlationId ? (
            <div className="mt-2 text-xs">Correlation: {error.correlationId}</div>
          ) : null}
        </Alert>
      ) : null}

      {message ? <Alert role="status" tone="success">{message}</Alert> : null}

      {loading && !detail ? (
        <div className="rounded-[var(--napms-surface-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)] p-8 text-sm text-[var(--napms-color-text-secondary)] shadow-[var(--napms-surface-shadow)]">
          Loading Connectivity Requirement…
        </div>
      ) : requirement && detail && interaction ? (
        <div className="grid gap-6">
          <DetailSection
            title="Policy coverage"
            actions={
              <Field label="Alignment as of">
                <Input
                  type="datetime-local"
                  step="1"
                  value={alignmentAsOf}
                  onChange={(event) => setAlignmentAsOf(event.target.value)}
                />
              </Field>
            }
          >
            <p className="max-w-3xl text-sm text-[var(--napms-color-text-secondary)]">
              Derived from this Requirement and effective Access Policy at one explicit logical time. It does not report configured/observed access.
            </p>
            {alignmentError ? (
              <Alert role="alert" tone="danger" className="mt-4">
                <div className="font-semibold">{alignmentError.code}</div>
                <div className="mt-1">{alignmentError.message}</div>
              </Alert>
            ) : loadingAlignment ? (
              <div className="mt-4 text-sm text-[var(--napms-color-text-secondary)]">
                Loading policy coverage…
              </div>
            ) : alignment ? (
              <div className="mt-4">
                <RequirementAlignmentStatus status={alignment.status} />
                <p className="mt-3 text-sm text-[var(--napms-color-text-body)]">
                  {alignmentExplanation(alignment.status)}
                </p>
                <div className="mt-2 text-xs text-[var(--napms-color-text-secondary)]">
                  asOf {alignment.asOf}
                </div>
              </div>
            ) : null}
          </DetailSection>

          <DetailSection
            title="Requirement lifecycle"
            actions={
              requirement.lifecycleState === "Active" &&
              detail.capabilities.retire === "Permitted" ? (
                <Button
                  variant="secondary"
                  loading={mutating}
                  onClick={() => void retire()}
                >
                  Retire Requirement
                </Button>
              ) : null
            }
          >
            <div className="flex items-center gap-3">
              <RequirementLifecycleStatus state={requirement.lifecycleState} />
              <span className="text-xs text-[var(--napms-color-text-secondary)]">
                aggregate version {requirement.version}
              </span>
            </div>
            <p className="mt-3 max-w-3xl text-sm text-[var(--napms-color-text-secondary)]">
              This lifecycle records whether the need remains current. It is not an approval or connectivity-decision status.
            </p>
          </DetailSection>

          <RequirementInteractionSection requirement={requirement} />

          <DetailSection title="Applicability">
            <p className="text-sm text-[var(--napms-color-text-secondary)]">
              Current: {applicabilityDisplay(requirement.applicability)}
            </p>
            <div className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">
              mutation: {detail.capabilities.setApplicability}
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
                    <Input
                      type="datetime-local"
                      step="1"
                      value={windowStart}
                      onChange={(event) => setWindowStart(event.target.value)}
                      disabled={
                        requirement.lifecycleState === "Retired" ||
                        detail.capabilities.setApplicability !== "Permitted"
                      }
                    />
                  </Field>
                  <Field label="End">
                    <Input
                      type="datetime-local"
                      step="1"
                      value={windowEnd}
                      onChange={(event) => setWindowEnd(event.target.value)}
                      disabled={
                        requirement.lifecycleState === "Retired" ||
                        detail.capabilities.setApplicability !== "Permitted"
                      }
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
          </DetailSection>

          <DetailSection title="Business justification">
            <p className="text-xs text-[var(--napms-color-text-secondary)]">
              mutation: {detail.capabilities.setJustification}
            </p>
            <Textarea
              className="mt-4"
              value={justification}
              onChange={(event) => setJustification(event.target.value)}
              rows={4}
              maxLength={4096}
              disabled={
                requirement.lifecycleState === "Retired" ||
                detail.capabilities.setJustification !== "Permitted"
              }
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
          </DetailSection>

          <RequirementProvenanceSection requirement={requirement} />
          <RequirementHistorySections requirement={requirement} />
        </div>
      ) : null}
    </PageWorkspace>
  )
}
