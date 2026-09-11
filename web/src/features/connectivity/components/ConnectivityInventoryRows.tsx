import { Fragment, useState } from "react"
import { ArrowLeft, ArrowRight } from "lucide-react"

import { StatusBadge } from "@/design-system/components/StatusBadge"
import type { ScopedConnectivityInventoryPage } from "@/features/connectivity/api"
import {
  ConnectivityRemoteSide,
  connectivityEndpointText,
} from "@/features/connectivity/components/ConnectivityEndpoint"
import {
  ConnectivityDecisionStatus,
  ConnectivityNeedStatus,
  ConnectivityPolicyStatus,
} from "@/features/connectivity/components/ConnectivityStatus"
import type { RequestConnectivityContext } from "@/features/connectivity/model"

export function ConnectivityInventoryRows({
  item,
  scope,
  onRequestAccess,
}: {
  item: ScopedConnectivityInventoryPage["items"][number]
  scope: string
  onRequestAccess: (context: RequestConnectivityContext) => void
}) {
  const resource = item.resource
  const endpointSummary = connectivityEndpointText(resource)
  const [expandedRelationship, setExpandedRelationship] = useState<string | null>(
    null,
  )

  return (
    <>
      <tr className="border-t border-[#CBD5E1] bg-[#F8FAFC]">
        <td colSpan={8} className="px-4 py-3">
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
            <div className="font-semibold text-[#172033]">
              {resource.resourceReference}
            </div>
            <div className="font-mono text-xs text-[#64748B]">
              {endpointSummary}
            </div>
            {resource.realizationState !== "Resolved" ? (
              <StatusBadge
                tone={resource.realizationState === "Unknown" ? "unknown" : "neutral"}
              >
                {resource.realizationState === "Unknown"
                  ? "Realization unknown"
                  : "No current realization"}
              </StatusBadge>
            ) : null}
          </div>
        </td>
      </tr>

      {!item.componentsKnown ? (
        <tr className="border-t border-[#E2E8F0]">
          <td colSpan={8} className="px-8 py-4 text-sm text-[#64748B]">
            Component binding information is unavailable.
          </td>
        </tr>
      ) : item.components.length === 0 ? (
        <tr className="border-t border-[#E2E8F0]">
          <td colSpan={8} className="px-8 py-4 text-sm text-[#64748B]">
            No Component Deployment is currently bound to this Resource.
          </td>
        </tr>
      ) : (
        item.components.flatMap((component) => {
          const componentCell = (
            <div>
              <div className="font-medium text-[#172033]">
                {component.displayName?.trim() || component.componentDeploymentId}
              </div>
              {component.displayName?.trim() ? (
                <div className="mt-0.5 font-mono text-[11px] text-[#94A3B8]">
                  {component.componentDeploymentId}
                </div>
              ) : null}
            </div>
          )

          if (!component.relationshipsKnown) {
            return [
              <tr
                key={`${resource.resourceReference}:${component.componentDeploymentId}:unknown`}
                className="border-t border-[#E2E8F0] align-top"
              >
                <td className="px-4 py-3 pl-8">{componentCell}</td>
                <td colSpan={7} className="px-4 py-3 text-[#64748B]">
                  Connectivity relationship data is unavailable.
                </td>
              </tr>,
            ]
          }

          if (component.relationships.length === 0) {
            return [
              <tr
                key={`${resource.resourceReference}:${component.componentDeploymentId}:empty`}
                className="border-t border-[#E2E8F0] align-top"
              >
                <td className="px-4 py-3 pl-8">{componentCell}</td>
                <td colSpan={7} className="px-4 py-3 text-[#64748B]">
                  No catalogued communication interaction is known for this Component.
                </td>
              </tr>,
            ]
          }

          return component.relationships.map((relationship, index) => {
            const relationshipKey =
              `${resource.resourceReference}:${component.componentDeploymentId}:${relationship.semanticIdentity.sourceComponentDeploymentId}:${relationship.semanticIdentity.destinationComponentDeploymentId}:${relationship.semanticIdentity.dcsContractRevisionId}:${relationship.direction}`
            const detailsOpen = expandedRelationship === relationshipKey

            return (
              <Fragment key={relationshipKey}>
                <tr className="border-t border-[#E2E8F0] align-top hover:bg-[#FCFDFE]">
                  <td className="px-4 py-3 pl-8">
                    {index === 0 ? componentCell : null}
                  </td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center gap-1.5 font-medium text-[#334155]">
                      {relationship.direction === "Outgoing" ? (
                        <>
                          <ArrowRight className="size-4" aria-hidden="true" />
                          Out
                        </>
                      ) : (
                        <>
                          <ArrowLeft className="size-4" aria-hidden="true" />
                          In
                        </>
                      )}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="font-medium text-[#172033]">
                      {relationship.dcsDisplayName?.trim() || "Communication"}
                    </div>
                    <div className="mt-1 font-mono text-xs text-[#64748B]">
                      {relationship.accessSummary || "Technical details unavailable"}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <ConnectivityRemoteSide
                      resourcesKnown={relationship.remoteResourcesKnown}
                      resources={relationship.remoteResources}
                      componentName={relationship.remoteComponent.displayName}
                      componentId={relationship.remoteComponent.componentDeploymentId}
                    />
                  </td>
                  <td className="px-4 py-3">
                    <ConnectivityNeedStatus value={relationship.need} />
                  </td>
                  <td className="px-4 py-3">
                    <ConnectivityDecisionStatus value={relationship.decision} />
                  </td>
                  <td className="px-4 py-3">
                    <ConnectivityPolicyStatus value={relationship.policy} />
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-col items-start gap-2">
                      <button
                        type="button"
                        aria-expanded={detailsOpen}
                        className="text-xs font-semibold text-[#475569] hover:text-[#172033]"
                        onClick={() =>
                          setExpandedRelationship(detailsOpen ? null : relationshipKey)
                        }
                      >
                        {detailsOpen ? "Hide details" : "Details"}
                      </button>
                      {relationship.policy.ruleExists === "No" &&
                      relationship.need.current !== "Unknown" &&
                      relationship.need.historicalOnly !== true &&
                      relationship.decision.state !== "NotAllowed" ? (
                        <button
                          type="button"
                          className="text-xs font-semibold text-[#2563EB] hover:text-[#1D4ED8]"
                          onClick={() =>
                            onRequestAccess({
                              scope,
                              localResourceReference: resource.resourceReference,
                              dependentComponentDeploymentId: component.componentDeploymentId,
                              sourceComponentDeploymentId:
                                relationship.semanticIdentity.sourceComponentDeploymentId,
                              destinationComponentDeploymentId:
                                relationship.semanticIdentity.destinationComponentDeploymentId,
                              dcsContractRevisionId:
                                relationship.semanticIdentity.dcsContractRevisionId,
                              needCurrent:
                                relationship.need.current === "Required" ? "Required" : "None",
                            })
                          }
                        >
                          Request access
                        </button>
                      ) : null}
                    </div>
                  </td>
                </tr>
                {detailsOpen ? (
                  <tr className="border-t border-[#E2E8F0] bg-[#F8FAFC]">
                    <td colSpan={8} className="px-8 py-4">
                      <div className="grid gap-4 text-xs md:grid-cols-2 xl:grid-cols-4">
                        <div>
                          <div className="font-semibold uppercase tracking-wide text-[#64748B]">
                            Source deployment
                          </div>
                          <div className="mt-1 break-all font-mono text-[#334155]">
                            {relationship.semanticIdentity.sourceComponentDeploymentId}
                          </div>
                        </div>
                        <div>
                          <div className="font-semibold uppercase tracking-wide text-[#64748B]">
                            Destination deployment
                          </div>
                          <div className="mt-1 break-all font-mono text-[#334155]">
                            {relationship.semanticIdentity.destinationComponentDeploymentId}
                          </div>
                        </div>
                        <div>
                          <div className="font-semibold uppercase tracking-wide text-[#64748B]">
                            DCS revision
                          </div>
                          <div className="mt-1 break-all font-mono text-[#334155]">
                            {relationship.semanticIdentity.dcsContractRevisionId}
                          </div>
                        </div>
                        <div>
                          <div className="font-semibold uppercase tracking-wide text-[#64748B]">
                            Remote resources
                          </div>
                          <div className="mt-1 text-[#334155]">
                            {!relationship.remoteResourcesKnown
                              ? "Unavailable"
                              : relationship.remoteResources.length === 0
                                ? "Unresolved"
                                : relationship.remoteResources
                                    .map(
                                      (remote) =>
                                        `${remote.resourceReference} · ${connectivityEndpointText(remote)}`,
                                    )
                                    .join(" | ")}
                          </div>
                        </div>
                      </div>
                    </td>
                  </tr>
                ) : null}
              </Fragment>
            )
          })
        })
      )}
    </>
  )
}
