import { useState } from "react"
import { Archive, Boxes, Link2 } from "lucide-react"

import { Button } from "@/design-system/components/Button"
import { Input, Select } from "@/design-system/components/Field"
import { InlineTextEdit } from "@/design-system/patterns/detail/InlineTextEdit"
import type {
  ApplicationTreeDto,
  DeploymentResourceBindingDto,
  PortConstraintDto,
  ResourceDto,
} from "@/features/catalogues/api/catalogue"
import { shortId } from "@/features/catalogues/components/CatalogueIdentity"

function portConstraintLabel(value: PortConstraintDto) {
  if (value.kind === "Any") return "any port"
  if (value.kind === "NotApplicable") return "n/a"
  return (value.ranges ?? [])
    .map((range) => range.first === range.last ? String(range.first) : `${range.first}-${range.last}`)
    .join(", ")
}

export function ApplicationComponentSection({
  component,
  resources,
  deploymentLabels,
  mutationKey,
  creatingDeployment,
  bindingDeployment,
  endingBindingReference,
  onRenameComponent,
  onRetireComponent,
  onAddDeployment,
  onRenameDeployment,
  onRetireDeployment,
  onBindResource,
  onEndBinding,
}: {
  component: ApplicationTreeDto["components"][number]
  resources: ResourceDto[]
  deploymentLabels: Map<string, string>
  mutationKey: string | null
  creatingDeployment: string | null
  bindingDeployment: string | null
  endingBindingReference: string | null
  onRenameComponent: (value: string | null) => Promise<boolean>
  onRetireComponent: () => void
  onAddDeployment: (name: string | null) => Promise<void>
  onRenameDeployment: (
    deployment: ApplicationTreeDto["components"][number]["deployments"][number],
    value: string | null,
  ) => Promise<boolean>
  onRetireDeployment: (
    deployment: ApplicationTreeDto["components"][number]["deployments"][number],
  ) => void
  onBindResource: (deploymentId: string, resourceReference: string) => Promise<void>
  onEndBinding: (binding: DeploymentResourceBindingDto) => Promise<void>
}) {
  const [deploymentName, setDeploymentName] = useState("")
  const [resourceSelections, setResourceSelections] = useState<Record<string, string>>({})
  const componentActive = component.lifecycle === "Active"

  async function addDeployment() {
    await onAddDeployment(deploymentName.trim() || null)
    setDeploymentName("")
  }

  async function bindResource(deploymentId: string) {
    const resourceReference = resourceSelections[deploymentId]
    if (!resourceReference) return
    await onBindResource(deploymentId, resourceReference)
    setResourceSelections((current) => ({ ...current, [deploymentId]: "" }))
  }

  return (
    <section className="rounded-lg border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)] shadow-sm">
      <div className="border-b border-[var(--napms-color-border)] p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <Boxes className="size-4 text-[var(--napms-color-text-secondary)]" aria-hidden="true" />
              <h2 className="font-semibold text-[var(--napms-color-text-primary)]">{component.displayName}</h2>
            </div>
            <div className="mt-1 font-mono text-[var(--napms-font-size-caption)] text-[var(--napms-color-text-secondary)]">
              {component.componentId} · v{component.version}
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-medium text-[var(--napms-color-text-secondary)]">{component.lifecycle}</span>
            {componentActive ? (
              <>
                <InlineTextEdit
                  value={component.displayName}
                  loading={mutationKey === `component:${component.componentId}:rename`}
                  onSave={onRenameComponent}
                />
                <Button
                  type="button"
                  variant="ghost"
                  loading={mutationKey === `component:${component.componentId}:retire`}
                  onClick={onRetireComponent}
                >
                  <Archive className="size-4" aria-hidden="true" />
                  Retire
                </Button>
              </>
            ) : null}
          </div>
        </div>

        {componentActive ? (
          <div className="mt-4 flex flex-col gap-2 sm:flex-row">
            <Input
              value={deploymentName}
              onChange={(event) => setDeploymentName(event.target.value)}
              placeholder="Deployment name (optional), e.g. production"
              maxLength={256}
            />
            <Button
              type="button"
              variant="secondary"
              loading={creatingDeployment === component.componentId}
              onClick={() => void addDeployment()}
            >
              Add deployment
            </Button>
          </div>
        ) : null}
      </div>

      {component.deployments.length === 0 ? (
        <div className="p-5 text-sm text-[var(--napms-color-text-secondary)]">No active deployments.</div>
      ) : (
        <div className="divide-y divide-[var(--napms-color-border)]">
          {component.deployments.map((deployment) => {
            const deploymentActive = deployment.lifecycle === "Active"
            return (
              <div key={deployment.componentDeploymentId} className="p-5">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <div className="font-semibold text-[var(--napms-color-text-primary)]">
                      {deployment.displayName || `Deployment ${shortId(deployment.componentDeploymentId)}`}
                    </div>
                    <div className="mt-1 font-mono text-[var(--napms-font-size-caption)] text-[var(--napms-color-text-secondary)]">
                      {deployment.componentDeploymentId} · v{deployment.version}
                    </div>
                  </div>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs font-medium text-[var(--napms-color-text-secondary)]">{deployment.lifecycle}</span>
                    {deploymentActive ? (
                      <>
                        <InlineTextEdit
                          value={deployment.displayName}
                          allowEmpty
                          loading={mutationKey === `deployment:${deployment.componentDeploymentId}:rename`}
                          onSave={(value) => onRenameDeployment(deployment, value)}
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          loading={mutationKey === `deployment:${deployment.componentDeploymentId}:retire`}
                          onClick={() => onRetireDeployment(deployment)}
                        >
                          <Archive className="size-4" aria-hidden="true" />
                          Retire
                        </Button>
                      </>
                    ) : null}
                  </div>
                </div>

                <div className="mt-4 grid gap-4 lg:grid-cols-2">
                  <div className="rounded-md bg-[var(--napms-color-surface-subtle)] p-4">
                    <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-[var(--napms-color-text-secondary)]">
                      <Link2 className="size-3.5" aria-hidden="true" />
                      Resource bindings
                    </div>
                    {deployment.effectiveResourceBindings.length === 0 ? (
                      <p className="text-sm text-[var(--napms-color-text-secondary)]">No effective resource bindings.</p>
                    ) : (
                      <div className="grid gap-2">
                        {deployment.effectiveResourceBindings.map((binding) => (
                          <div key={binding.bindingReference} className="flex items-center justify-between gap-3 text-sm text-[var(--napms-color-text-primary)]">
                            <div>
                              <span className="font-medium">{binding.resourceReference}</span>
                              <span className="ml-2 text-xs text-[var(--napms-color-text-secondary)]">
                                since {new Date(binding.validFrom).toLocaleString()} · v{binding.version}
                              </span>
                            </div>
                            {deploymentActive ? (
                              <Button
                                type="button"
                                variant="secondary"
                                loading={endingBindingReference === binding.bindingReference}
                                disabled={endingBindingReference !== null}
                                onClick={() => void onEndBinding(binding)}
                              >
                                End
                              </Button>
                            ) : null}
                          </div>
                        ))}
                      </div>
                    )}
                    {deploymentActive ? (
                      <div className="mt-3 flex flex-col gap-2 sm:flex-row">
                        <Select
                          value={resourceSelections[deployment.componentDeploymentId] ?? ""}
                          onChange={(event) => setResourceSelections((current) => ({ ...current, [deployment.componentDeploymentId]: event.target.value }))}
                          aria-label="Resource to bind"
                        >
                          <option value="">Select Resource…</option>
                          {resources.map((resource) => (
                            <option key={resource.resourceReference} value={resource.resourceReference}>
                              {resource.displayName || shortId(resource.resourceReference)}
                            </option>
                          ))}
                        </Select>
                        <Button
                          type="button"
                          variant="secondary"
                          loading={bindingDeployment === deployment.componentDeploymentId}
                          disabled={!resourceSelections[deployment.componentDeploymentId]}
                          onClick={() => void bindResource(deployment.componentDeploymentId)}
                        >
                          Bind
                        </Button>
                      </div>
                    ) : null}
                  </div>

                  <div className="rounded-md bg-[var(--napms-color-surface-subtle)] p-4">
                    <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-[var(--napms-color-text-secondary)]">
                      Communication specifications
                    </div>
                    {deployment.dcsRevisions.length === 0 ? (
                      <p className="text-sm text-[var(--napms-color-text-secondary)]">No communication revisions.</p>
                    ) : (
                      <div className="grid gap-3">
                        {deployment.dcsRevisions.map((revision) => {
                          const source = deploymentLabels.get(revision.sourceComponentDeploymentId) ?? `Deployment ${shortId(revision.sourceComponentDeploymentId)}`
                          const destination = deploymentLabels.get(revision.destinationComponentDeploymentId) ?? `Deployment ${shortId(revision.destinationComponentDeploymentId)}`
                          const direction = revision.sourceComponentDeploymentId === deployment.componentDeploymentId ? "Outgoing" : "Incoming"
                          return (
                            <div key={revision.revisionId} className="rounded border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)] p-3 text-sm">
                              <div className="flex flex-wrap items-center justify-between gap-2">
                                <div className="font-medium text-[var(--napms-color-text-primary)]">{revision.displayName || `Communication ${shortId(revision.revisionId)}`}</div>
                                <span className="text-xs font-medium text-[var(--napms-color-text-secondary)]">{direction}</span>
                              </div>
                              <div className="mt-1 text-xs text-[var(--napms-color-text-body)]">{source} → {destination}</div>
                              {revision.trafficAlternatives.length === 0 ? (
                                <div className="mt-2 text-xs text-[var(--napms-color-warning)]">Traffic semantics are unavailable for this revision.</div>
                              ) : (
                                <div className="mt-2 grid gap-1">
                                  {revision.trafficAlternatives.map((traffic, index) => (
                                    <div key={`${revision.revisionId}:${index}`} className="text-xs text-[var(--napms-color-text-body)]">
                                      {traffic.protocol.toUpperCase()} · source {portConstraintLabel(traffic.sourcePorts)} → destination {portConstraintLabel(traffic.destinationPorts)}{traffic.serviceReference ? ` · service ${traffic.serviceReference}` : ""}
                                    </div>
                                  ))}
                                </div>
                              )}
                              <div className="mt-2 font-mono text-[var(--napms-font-size-micro)] text-[var(--napms-color-text-muted)]">revision {revision.revisionId}</div>
                            </div>
                          )
                        })}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </section>
  )
}
