import { useEffect, useMemo, useState } from "react"
import { ArrowLeft, CircleAlert, ShieldCheck } from "lucide-react"

import { Button } from "@/design-system/components/Button"
import {
  displayName,
  trafficAlternativeText,
} from "@/features/catalogues/components/CatalogueIdentity"
import type { ProposalInteraction } from "@/features/catalogues/model/interaction"
import {
  RequestConnectivityContextSummary,
} from "@/features/connectivity/components/RequestConnectivityContext"
import {
  RequestConnectivityForm,
  type RequestConnectivityDraft,
} from "@/features/connectivity/components/RequestConnectivityForm"
import type { RequestConnectivityContext } from "@/features/connectivity/model"
import { listProposalInteractions, submitProposal } from "@/features/proposals/api"
import type { ProposalResult } from "@/features/proposals/model/result"
import {
  declareConnectivityRequirement,
  type RequirementApplicability,
} from "@/features/requirements/api"
import { ApiError } from "@/lib/api"
import { toOffsetAwareIso } from "@/lib/datetime"

function exactMatch(
  item: ProposalInteraction,
  context: RequestConnectivityContext,
): boolean {
  return (
    item.sourceComponentDeploymentId === context.sourceComponentDeploymentId &&
    item.destinationComponentDeploymentId === context.destinationComponentDeploymentId &&
    item.dcsContractRevisionId === context.dcsContractRevisionId
  )
}

function proposalOutcomeText(result: ProposalResult): string {
  if (result.outcome === "NotAllowed") {
    return "The connectivity was not allowed. No Access Rule was created."
  }
  if (result.outcome === "Materialized") {
    return "Access was allowed and the Access Rule was created."
  }
  return "Access was allowed and the existing Access Rule was resolved."
}

export function RequestConnectivityPage({
  context,
  onBack,
}: {
  context: RequestConnectivityContext
  onBack: () => void
}) {
  const [interaction, setInteraction] = useState<ProposalInteraction | null>(null)
  const [loadingContext, setLoadingContext] = useState(true)
  const [contextError, setContextError] = useState<ApiError | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState<ApiError | null>(null)
  const [needRecorded, setNeedRecorded] = useState(
    context.needCurrent === "Required",
  )
  const [result, setResult] = useState<ProposalResult | null>(null)

  useEffect(() => {
    let active = true
    setLoadingContext(true)
    setContextError(null)

    void listProposalInteractions(
      context.scope,
      1,
      context.dcsContractRevisionId,
    )
      .then((page) => {
        if (!active) return
        const selected = page.items.find((item) => exactMatch(item, context))
        if (!selected) {
          setInteraction(null)
          setContextError(
            new ApiError(
              404,
              "InteractionUnavailable",
              "This exact application interaction is not available for an access proposal in the selected scope.",
            ),
          )
          return
        }
        setInteraction(selected)
      })
      .catch((caught) => {
        if (!active) return
        setInteraction(null)
        setContextError(
          caught instanceof ApiError
            ? caught
            : new ApiError(
                500,
                "InternalError",
                "The connectivity context could not be loaded.",
              ),
        )
      })
      .finally(() => {
        if (active) setLoadingContext(false)
      })

    return () => {
      active = false
    }
  }, [context])

  const localIsSource =
    context.dependentComponentDeploymentId === context.sourceComponentDeploymentId

  const localLabel = useMemo(() => {
    if (!interaction) return context.dependentComponentDeploymentId
    return localIsSource
      ? displayName(
          interaction.catalogue?.sourceDisplayName,
          context.sourceComponentDeploymentId,
        )
      : displayName(
          interaction.catalogue?.destinationDisplayName,
          context.destinationComponentDeploymentId,
        )
  }, [context, interaction, localIsSource])

  const remoteLabel = useMemo(() => {
    if (!interaction) {
      return localIsSource
        ? context.destinationComponentDeploymentId
        : context.sourceComponentDeploymentId
    }
    return localIsSource
      ? displayName(
          interaction.catalogue?.destinationDisplayName,
          context.destinationComponentDeploymentId,
        )
      : displayName(
          interaction.catalogue?.sourceDisplayName,
          context.sourceComponentDeploymentId,
        )
  }, [context, interaction, localIsSource])

  const accessLabel = interaction
    ? displayName(
        interaction.catalogue?.dcsDisplayName,
        context.dcsContractRevisionId,
      )
    : context.dcsContractRevisionId

  const trafficText = (interaction?.catalogue?.trafficAlternatives ?? [])
    .map(trafficAlternativeText)
    .join(" | ")

  async function submit(draft: RequestConnectivityDraft) {
    if (!interaction || result) return

    setSubmitting(true)
    setSubmitError(null)

    try {
      if (context.needCurrent === "None") {
        let applicability: RequirementApplicability
        if (draft.applicabilityKind === "Ongoing") {
          applicability = { kind: "Ongoing" }
        } else {
          if (!draft.windowStart || !draft.windowEnd) {
            throw new ApiError(
              422,
              "InvalidRequirementApplicability",
              "Start and end are required for an absolute time window.",
            )
          }
          applicability = {
            kind: "AbsoluteWindow",
            start: toOffsetAwareIso(draft.windowStart),
            end: toOffsetAwareIso(draft.windowEnd),
          }
        }

        await declareConnectivityRequirement({
          authorityScope: context.scope,
          dependentComponentDeploymentId: context.dependentComponentDeploymentId,
          sourceComponentDeploymentId: context.sourceComponentDeploymentId,
          destinationComponentDeploymentId: context.destinationComponentDeploymentId,
          dcsContractRevisionId: context.dcsContractRevisionId,
          applicability,
          justification: draft.justification,
        })
        setNeedRecorded(true)
      }

      const proposal = await submitProposal({
        authorityScope: context.scope,
        sourceComponentDeploymentId: context.sourceComponentDeploymentId,
        destinationComponentDeploymentId: context.destinationComponentDeploymentId,
        dcsContractRevisionId: context.dcsContractRevisionId,
      })
      setResult(proposal)
    } catch (caught) {
      setSubmitError(
        caught instanceof ApiError
          ? caught
          : new ApiError(
              500,
              "InternalError",
              "The access operation could not be completed.",
            ),
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-[980px]">
      <button
        type="button"
        onClick={onBack}
        className="mb-4 inline-flex items-center gap-2 text-sm font-semibold text-[#475569] hover:text-[#172033]"
      >
        <ArrowLeft className="size-4" aria-hidden="true" />
        Back to Connectivity
      </button>

      <header className="mb-6">
        <div className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#64748B]">
          Connectivity
        </div>
        <h1 className="text-[28px] font-bold tracking-tight text-[#172033]">
          Request access
        </h1>
        <p className="mt-2 max-w-3xl text-sm text-[#64748B]">
          The resource and exact application interaction are already known.
          This action records the local need when required, then uses the
          existing access proposal and decision flow.
        </p>
      </header>

      {contextError || submitError ? (
        <div
          role="alert"
          className="mb-5 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800"
        >
          <div className="flex gap-3">
            <CircleAlert className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
            <div>
              <div className="font-semibold">
                {(contextError ?? submitError)?.code}
              </div>
              <div className="mt-1">
                {(contextError ?? submitError)?.message}
              </div>
              {needRecorded && context.needCurrent === "None" && submitError ? (
                <div className="mt-2 text-xs font-medium">
                  The Connectivity Requirement was recorded before the later
                  access step failed.
                </div>
              ) : null}
            </div>
          </div>
        </div>
      ) : null}

      <RequestConnectivityContextSummary
        scope={context.scope}
        resourceReference={context.localResourceReference}
        localLabel={localLabel}
        remoteLabel={remoteLabel}
        direction={localIsSource ? "Outgoing" : "Incoming"}
        accessLabel={accessLabel}
        trafficText={trafficText}
        needExists={context.needCurrent === "Required"}
        loading={loadingContext}
      />

      {result ? (
        <section
          className={
            result.outcome === "NotAllowed"
              ? "rounded-lg border border-red-200 bg-red-50 p-5"
              : "rounded-lg border border-green-200 bg-green-50 p-5"
          }
        >
          <div className="flex gap-3">
            <ShieldCheck className="mt-0.5 size-5 shrink-0" aria-hidden="true" />
            <div>
              <h2 className="font-semibold text-[#172033]">
                {result.outcome === "NotAllowed"
                  ? "Access not allowed"
                  : "Access authorized"}
              </h2>
              <p className="mt-1 text-sm text-[#475569]">
                {proposalOutcomeText(result)}
              </p>
              <Button
                type="button"
                variant="secondary"
                className="mt-4"
                onClick={onBack}
              >
                Back to Connectivity
              </Button>
            </div>
          </div>
        </section>
      ) : (
        <RequestConnectivityForm
          needExists={context.needCurrent === "Required"}
          loading={loadingContext}
          submitting={submitting}
          disabled={!interaction}
          onSubmit={(draft) => void submit(draft)}
        />
      )}
    </div>
  )
}
