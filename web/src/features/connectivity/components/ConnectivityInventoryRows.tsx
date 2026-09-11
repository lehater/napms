import { Fragment, useState } from "react"
import { ArrowLeft, ArrowRight } from "lucide-react"

import { DataTableCell, DataTableRow } from "@/design-system/components/DataTable"
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
  const [expandedRelationship, setExpandedRelationship] = useState<string | null>(null)

  return (
    <>
      <DataTableRow className="bg-[var(--napms-color-surface-subtle)] hover:bg-[var(--napms-color-surface-subtle)]">
        <DataTableCell colSpan={8} className="py-3">
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
            <div className="font-semibold text-[var(--napms-color-text-primary)]">{resource.resourceReference}</div>
            <div className="font-mono text-xs text-[var(--napms-color-text-secondary)]">{endpointSummary}</div>
            {resource.realizationState !== "Resolved" ? (
              <StatusBadge tone={resource.realizationState === "Unknown" ? "unknown" : "neutral"}>
                {resource.realizationState === "Unknown" ? "Realization unknown" : "No current realization"}
              </StatusBadge>
            ) : null}
          </div>
        </DataTableCell>
      </DataTableRow>

      {!item.componentsKnown ? (
        <DataTableRow>
          <DataTableCell colSpan={8} className="px-8 py-4 text-sm text-[var(--napms-color-text-secondary)]">Component binding information is unavailable.</DataTableCell>
        </DataTableRow>
      ) : item.components.length === 0 ? (
        <DataTableRow>
          <DataTableCell colSpan={8} className="px-8 py-4 text-sm text-[var(--napms-color-text-secondary)]">No Component Deployment is currently bound to this Resource.</DataTableCell>
        </DataTableRow>
      ) : (
        item.components.flatMap((component) => {
          const componentCell = (
            <div>
              <div className="font-medium text-[var(--napms-color-text-primary)]">{component.displayName?.trim() || component.componentDeploymentId}</div>
              {component.displayName?.trim() ? <div className="mt-0.5 font-mono text-[11px] text-[var(--napms-color-text-muted)]">{component.componentDeploymentId}</div> : null}
            </div>
          )

          if (!component.relationshipsKnown) {
            return [
              <DataTableRow key={`${resource.resourceReference}:${component.componentDeploymentId}:unknown`}>
                <DataTableCell className="pl-8">{componentCell}</DataTableCell>
                <DataTableCell colSpan={7} className="text-[var(--napms-color-text-secondary)]">Connectivity relationship data is unavailable.</DataTableCell>
              </DataTableRow>,
            ]
          }

          if (component.relationships.length === 0) {
            return [
              <DataTableRow key={`${resource.resourceReference}:${component.componentDeploymentId}:empty`}>
                <DataTableCell className="pl-8">{componentCell}</DataTableCell>
                <DataTableCell colSpan={7} className="text-[var(--napms-color-text-secondary)]">No catalogued communication interaction is known for this Component.</DataTableCell>
              </DataTableRow>,
            ]
          }

          return component.relationships.map((relationship, index) => {
            const relationshipKey = `${resource.resourceReference}:${component.componentDeploymentId}:${relationship.semanticIdentity.sourceComponentDeploymentId}:${relationship.semanticIdentity.destinationComponentDeploymentId}:${relationship.semanticIdentity.dcsContractRevisionId}:${relationship.direction}`
            const detailsOpen = expandedRelationship === relationshipKey

            return (
              <Fragment key={relationshipKey}>
                <DataTableRow>
                  <DataTableCell className="pl-8">{index === 0 ? componentCell : null}</DataTableCell>
                  <DataTableCell>
                    <span className="inline-flex items-center gap-1.5 font-medium text-[var(--napms-color-text-body)]">
                      {relationship.direction === "Outgoing" ? <><ArrowRight className="size-4" aria-hidden="true" />Out</> : <><ArrowLeft className="size-4" aria-hidden="true" />In</>}
                    </span>
                  </DataTableCell>
                  <DataTableCell>
                    <div className="font-medium text-[var(--napms-color-text-primary)]">{relationship.dcsDisplayName?.trim() || "Communication"}</div>
                    <div className="mt-1 font-mono text-xs text-[var(--napms-color-text-secondary)]">{relationship.accessSummary || "Technical details unavailable"}</div>
                  </DataTableCell>
                  <DataTableCell>
                    <ConnectivityRemoteSide resourcesKnown={relationship.remoteResourcesKnown} resources={relationship.remoteResources} componentName={relationship.remoteComponent.displayName} componentId={relationship.remoteComponent.componentDeploymentId} />
                  </DataTableCell>
                  <DataTableCell><ConnectivityNeedStatus value={relationship.need} /></DataTableCell>
                  <DataTableCell><ConnectivityDecisionStatus value={relationship.decision} /></DataTableCell>
                  <DataTableCell><ConnectivityPolicyStatus value={relationship.policy} /></DataTableCell>
                  <DataTableCell>
                    <div className="flex flex-col items-start gap-2">
                      <button type="button" aria-expanded={detailsOpen} className="text-xs font-semibold text-[var(--napms-color-text-body)] hover:text-[var(--napms-color-text-primary)]" onClick={() => setExpandedRelationship(detailsOpen ? null : relationshipKey)}>
                        {detailsOpen ? "Hide details" : "Details"}
                      </button>
                      {relationship.policy.ruleExists === "No" && relationship.need.current !== "Unknown" && relationship.need.historicalOnly !== true && relationship.decision.state !== "NotAllowed" ? (
                        <button
                          type="button"
                          className="text-xs font-semibold text-[var(--napms-color-primary)] hover:text-[var(--napms-color-primary-hover)]"
                          onClick={() => onRequestAccess({
                            scope,
                            localResourceReference: resource.resourceReference,
                            dependentComponentDeploymentId: component.componentDeploymentId,
                            sourceComponentDeploymentId: relationship.semanticIdentity.sourceComponentDeploymentId,
                            destinationComponentDeploymentId: relationship.semanticIdentity.destinationComponentDeploymentId,
                            dcsContractRevisionId: relationship.semanticIdentity.dcsContractRevisionId,
                            needCurrent: relationship.need.current === "Required" ? "Required" : "None",
                          })}
                        >Request access</button>
                      ) : null}
                    </div>
                  </DataTableCell>
                </DataTableRow>
                {detailsOpen ? (
                  <DataTableRow className="bg-[var(--napms-color-surface-subtle)] hover:bg-[var(--napms-color-surface-subtle)]">
                    <DataTableCell colSpan={8} className="px-8 py-4">
                      <div className="grid gap-4 text-xs md:grid-cols-2 xl:grid-cols-4">
                        <div><div className="font-semibold uppercase tracking-wide text-[var(--napms-color-text-secondary)]">Source deployment</div><div className="mt-1 break-all font-mono text-[var(--napms-color-text-body)]">{relationship.semanticIdentity.sourceComponentDeploymentId}</div></div>
                        <div><div className="font-semibold uppercase tracking-wide text-[var(--napms-color-text-secondary)]">Destination deployment</div><div className="mt-1 break-all font-mono text-[var(--napms-color-text-body)]">{relationship.semanticIdentity.destinationComponentDeploymentId}</div></div>
                        <div><div className="font-semibold uppercase tracking-wide text-[var(--napms-color-text-secondary)]">DCS revision</div><div className="mt-1 break-all font-mono text-[var(--napms-color-text-body)]">{relationship.semanticIdentity.dcsContractRevisionId}</div></div>
                        <div><div className="font-semibold uppercase tracking-wide text-[var(--napms-color-text-secondary)]">Remote resources</div><div className="mt-1 text-[var(--napms-color-text-body)]">{!relationship.remoteResourcesKnown ? "Unavailable" : relationship.remoteResources.length === 0 ? "Unresolved" : relationship.remoteResources.map((remote) => `${remote.resourceReference} · ${connectivityEndpointText(remote)}`).join(" | ")}</div></div>
                      </div>
                    </DataTableCell>
                  </DataTableRow>
                ) : null}
              </Fragment>
            )
          })
        })
      )}
    </>
  )
}
