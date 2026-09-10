import { useEffect, useMemo, useState } from "react"
import { Archive, ArrowLeft, Boxes, Link2, Pencil, Plus, RefreshCw } from "lucide-react"

import { ApiError } from "@/api"
import { shortId } from "@/components/catalogue/CatalogueIdentity"
import { Button } from "@/components/ui/Button"
import { DcsAuthoringPanel } from "@/features/catalogues/DcsAuthoringPanel"
import {
  createCatalogueComponent,
  createCatalogueDeployment,
  createCatalogueDeploymentResourceBinding,
  endCatalogueDeploymentResourceBinding,
  listCatalogueResources,
  readCatalogueApplication,
  renameCatalogueApplication,
  renameCatalogueComponent,
  renameCatalogueDeployment,
  retireCatalogueApplication,
  retireCatalogueComponent,
  retireCatalogueDeployment,
  type ApplicationTreeDto,
  type DeploymentResourceBindingDto,
  type PortConstraintDto,
  type ResourceDto,
} from "@/features/catalogues/catalogueApi"

const inputClass =
  "min-h-10 w-full rounded-md border border-[#CBD5E1] bg-white px-3 py-2 text-sm text-[#172033] outline-none focus:border-[#2563EB] focus:ring-2 focus:ring-[#DBEAFE]"

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError
    ? caught
    : new ApiError(500, "InternalError", fallback)
}

function portConstraintLabel(value: PortConstraintDto) {
  if (value.kind === "Any") return "any port"
  if (value.kind === "NotApplicable") return "n/a"
  return (value.ranges ?? [])
    .map((range) =>
      range.first === range.last ? String(range.first) : `${range.first}-${range.last}`,
    )
    .join(", ")
}

function InlineRename({
  value,
  allowEmpty = false,
  loading,
  onSave,
}: {
  value: string | null
  allowEmpty?: boolean
  loading: boolean
  onSave: (value: string | null) => Promise<boolean>
}) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(value ?? "")

  useEffect(() => {
    if (!editing) setDraft(value ?? "")
  }, [editing, value])

  if (!editing) {
    return (
      <Button type="button" variant="ghost" onClick={() => setEditing(true)}>
        <Pencil className="size-4" aria-hidden="true" />
        Rename
      </Button>
    )
  }

  const normalized = draft.trim()
  const nextValue = allowEmpty && !normalized ? null : normalized
  const unchanged = nextValue === value

  return (
    <form
      className="flex min-w-64 flex-wrap items-center gap-2"
      onSubmit={(event) => {
        event.preventDefault()
        if ((!allowEmpty && !normalized) || unchanged) return
        void onSave(nextValue).then((saved) => {
          if (saved) setEditing(false)
        })
      }}
    >
      <input
        className={inputClass}
        value={draft}
        onChange={(event) => setDraft(event.target.value)}
        aria-label="New display name"
        maxLength={256}
        autoFocus
      />
      <Button
        type="submit"
        loading={loading}
        disabled={(!allowEmpty && !normalized) || unchanged}
      >
        Save
      </Button>
      <Button
        type="button"
        variant="ghost"
        disabled={loading}
        onClick={() => setEditing(false)}
      >
        Cancel
      </Button>
    </form>
  )
}

export function ApplicationDetailsPage({
  applicationId,
  onBack,
}: {
  applicationId: string
  onBack: () => void
}) {
  const [detail, setDetail] = useState<ApplicationTreeDto | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)
  const [componentName, setComponentName] = useState("")
  const [creatingComponent, setCreatingComponent] = useState(false)
  const [deploymentNames, setDeploymentNames] = useState<Record<string, string>>({})
  const [creatingDeployment, setCreatingDeployment] = useState<string | null>(null)
  const [resources, setResources] = useState<ResourceDto[]>([])
  const [resourceSelections, setResourceSelections] = useState<Record<string, string>>({})
  const [bindingDeployment, setBindingDeployment] = useState<string | null>(null)
  const [endingBindingReference, setEndingBindingReference] = useState<string | null>(null)
  const [mutationKey, setMutationKey] = useState<string | null>(null)
  const [mutationError, setMutationError] = useState<ApiError | null>(null)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      setDetail(await readCatalogueApplication(applicationId))
    } catch (caught) {
      setError(errorFrom(caught, "Application details could not be loaded."))
    } finally {
      setLoading(false)
    }
  }

  async function loadResources() {
    try {
      const result = await listCatalogueResources(1)
      setResources(result.items.filter((item) => item.lifecycle === "Active"))
    } catch (caught) {
      setMutationError(errorFrom(caught, "Resource discovery could not be loaded."))
    }
  }

  useEffect(() => {
    void load()
  }, [applicationId])

  useEffect(() => {
    void loadResources()
  }, [])

  const deploymentLabels = useMemo(() => {
    const labels = new Map<string, string>()
    if (!detail) return labels
    for (const component of detail.components) {
      for (const deployment of component.deployments) {
        labels.set(
          deployment.componentDeploymentId,
          `${component.displayName} / ${deployment.displayName || `Deployment ${shortId(deployment.componentDeploymentId)}`}`,
        )
      }
    }
    return labels
  }, [detail])

  async function runMutation(
    key: string,
    fallback: string,
    action: () => Promise<unknown>,
  ) {
    setMutationKey(key)
    setMutationError(null)
    try {
      await action()
      await load()
      return true
    } catch (caught) {
      setMutationError(errorFrom(caught, fallback))
      return false
    } finally {
      setMutationKey(null)
    }
  }

  async function addComponent(event: React.FormEvent) {
    event.preventDefault()
    const name = componentName.trim()
    if (!name) return
    setCreatingComponent(true)
    setMutationError(null)
    try {
      await createCatalogueComponent(applicationId, name)
      setComponentName("")
      await load()
    } catch (caught) {
      setMutationError(errorFrom(caught, "Component could not be created."))
    } finally {
      setCreatingComponent(false)
    }
  }

  async function addDeployment(componentId: string) {
    const name = deploymentNames[componentId]?.trim() || null
    setCreatingDeployment(componentId)
    setMutationError(null)
    try {
      await createCatalogueDeployment(componentId, name)
      setDeploymentNames((current) => ({ ...current, [componentId]: "" }))
      await load()
    } catch (caught) {
      setMutationError(errorFrom(caught, "Deployment could not be created."))
    } finally {
      setCreatingDeployment(null)
    }
  }

  async function bindResource(deploymentId: string) {
    const resourceReference = resourceSelections[deploymentId]
    if (!resourceReference) return
    setBindingDeployment(deploymentId)
    setMutationError(null)
    try {
      await createCatalogueDeploymentResourceBinding(
        deploymentId,
        resourceReference,
        new Date().toISOString(),
      )
      setResourceSelections((current) => ({ ...current, [deploymentId]: "" }))
      await load()
    } catch (caught) {
      setMutationError(errorFrom(caught, "Resource binding could not be created."))
    } finally {
      setBindingDeployment(null)
    }
  }

  async function endBinding(binding: DeploymentResourceBindingDto) {
    if (!window.confirm(`End binding to ${binding.resourceReference} now?`)) return
    setEndingBindingReference(binding.bindingReference)
    setMutationError(null)
    try {
      await endCatalogueDeploymentResourceBinding(
        binding,
        new Date().toISOString(),
      )
      await load()
    } catch (caught) {
      setMutationError(errorFrom(caught, "Resource binding could not be ended."))
    } finally {
      setEndingBindingReference(null)
    }
  }

  if (loading && detail === null) {
    return <div className="text-sm text-[#64748B]">Loading application…</div>
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

  const applicationActive = detail.application.lifecycle === "Active"

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
            Applications
          </button>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-bold text-[#172033]">
              {detail.application.displayName}
            </h1>
            <span className="rounded-full border border-[#CBD5E1] px-2 py-0.5 text-xs font-semibold text-[#475569]">
              {detail.application.lifecycle}
            </span>
          </div>
          <div className="mt-1 font-mono text-xs text-[#64748B]">
            {detail.application.applicationId} · v{detail.application.version}
          </div>
        </div>
        <div className="flex flex-wrap items-center justify-end gap-2">
          {applicationActive ? (
            <>
              <InlineRename
                value={detail.application.displayName}
                loading={mutationKey === `application:${detail.application.applicationId}:rename`}
                onSave={(value) =>
                  runMutation(
                    `application:${detail.application.applicationId}:rename`,
                    "Application could not be renamed.",
                    () => renameCatalogueApplication(detail.application, value ?? ""),
                  )
                }
              />
              <Button
                type="button"
                variant="secondary"
                loading={mutationKey === `application:${detail.application.applicationId}:retire`}
                onClick={() => {
                  if (!window.confirm(
                    "Retire this application? Active components must be retired first. Historical references will be preserved.",
                  )) return
                  void runMutation(
                    `application:${detail.application.applicationId}:retire`,
                    "Application could not be retired.",
                    () => retireCatalogueApplication(detail.application),
                  )
                }}
              >
                <Archive className="size-4" aria-hidden="true" />
                Retire
              </Button>
            </>
          ) : null}
          <Button variant="secondary" loading={loading} onClick={() => void load()}>
            <RefreshCw className="size-4" aria-hidden="true" />
            Refresh
          </Button>
        </div>
      </header>

      {mutationError ? (
        <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800" role="alert">
          {mutationError.message}
        </div>
      ) : null}

      {applicationActive ? (
        <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <Plus className="size-4 text-[#2563EB]" aria-hidden="true" />
            <h2 className="font-semibold text-[#172033]">Add component</h2>
          </div>
          <form className="flex flex-col gap-3 sm:flex-row" onSubmit={addComponent}>
            <input
              className={inputClass}
              value={componentName}
              onChange={(event) => setComponentName(event.target.value)}
              placeholder="Component name, e.g. Orders API"
              maxLength={256}
            />
            <Button type="submit" loading={creatingComponent} disabled={!componentName.trim()}>
              Create component
            </Button>
          </form>
        </section>
      ) : null}

      {applicationActive ? (
        <DcsAuthoringPanel
          currentApplicationId={applicationId}
          onCreated={load}
        />
      ) : null}

      {detail.components.length === 0 ? (
        <section className="rounded-lg border border-dashed border-[#CBD5E1] bg-white p-8 text-center text-sm text-[#64748B]">
          This application has no active components.
        </section>
      ) : (
        <div className="grid gap-5">
          {detail.components.map((component) => {
            const componentActive = component.lifecycle === "Active"
            return (
              <section
                key={component.componentId}
                className="rounded-lg border border-[#E2E8F0] bg-white shadow-sm"
              >
                <div className="border-b border-[#E2E8F0] p-5">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <Boxes className="size-4 text-[#64748B]" aria-hidden="true" />
                        <h2 className="font-semibold text-[#172033]">{component.displayName}</h2>
                      </div>
                      <div className="mt-1 font-mono text-[11px] text-[#64748B]">
                        {component.componentId} · v{component.version}
                      </div>
                    </div>
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="rounded-full border border-[#CBD5E1] px-2 py-0.5 text-xs font-semibold text-[#475569]">
                        {component.lifecycle}
                      </span>
                      {componentActive ? (
                        <>
                          <InlineRename
                            value={component.displayName}
                            loading={mutationKey === `component:${component.componentId}:rename`}
                            onSave={(value) =>
                              runMutation(
                                `component:${component.componentId}:rename`,
                                "Component could not be renamed.",
                                () => renameCatalogueComponent(component, value ?? ""),
                              )
                            }
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            loading={mutationKey === `component:${component.componentId}:retire`}
                            onClick={() => {
                              if (!window.confirm(
                                `Retire ${component.displayName}? Active deployments must be retired first. Historical references will be preserved.`,
                              )) return
                              void runMutation(
                                `component:${component.componentId}:retire`,
                                "Component could not be retired.",
                                () => retireCatalogueComponent(component),
                              )
                            }}
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
                      <input
                        className={inputClass}
                        value={deploymentNames[component.componentId] ?? ""}
                        onChange={(event) =>
                          setDeploymentNames((current) => ({
                            ...current,
                            [component.componentId]: event.target.value,
                          }))
                        }
                        placeholder="Deployment name (optional), e.g. production"
                        maxLength={256}
                      />
                      <Button
                        type="button"
                        variant="secondary"
                        loading={creatingDeployment === component.componentId}
                        onClick={() => void addDeployment(component.componentId)}
                      >
                        Add deployment
                      </Button>
                    </div>
                  ) : null}
                </div>

                {component.deployments.length === 0 ? (
                  <div className="p-5 text-sm text-[#64748B]">No active deployments.</div>
                ) : (
                  <div className="divide-y divide-[#E2E8F0]">
                    {component.deployments.map((deployment) => {
                      const deploymentActive = deployment.lifecycle === "Active"
                      return (
                        <div key={deployment.componentDeploymentId} className="p-5">
                          <div className="flex flex-wrap items-start justify-between gap-3">
                            <div>
                              <div className="font-semibold text-[#172033]">
                                {deployment.displayName ||
                                  `Deployment ${shortId(deployment.componentDeploymentId)}`}
                              </div>
                              <div className="mt-1 font-mono text-[11px] text-[#64748B]">
                                {deployment.componentDeploymentId} · v{deployment.version}
                              </div>
                            </div>
                            <div className="flex flex-wrap items-center gap-2">
                              <span className="text-xs font-medium text-[#64748B]">
                                {deployment.lifecycle}
                              </span>
                              {deploymentActive ? (
                                <>
                                  <InlineRename
                                    value={deployment.displayName}
                                    allowEmpty
                                    loading={mutationKey === `deployment:${deployment.componentDeploymentId}:rename`}
                                    onSave={(value) =>
                                      runMutation(
                                        `deployment:${deployment.componentDeploymentId}:rename`,
                                        "Deployment could not be renamed.",
                                        () => renameCatalogueDeployment(deployment, value),
                                      )
                                    }
                                  />
                                  <Button
                                    type="button"
                                    variant="ghost"
                                    loading={mutationKey === `deployment:${deployment.componentDeploymentId}:retire`}
                                    onClick={() => {
                                      if (!window.confirm(
                                        "Retire this deployment? Existing bindings, communication revisions and policy history will be preserved.",
                                      )) return
                                      void runMutation(
                                        `deployment:${deployment.componentDeploymentId}:retire`,
                                        "Deployment could not be retired.",
                                        () => retireCatalogueDeployment(deployment),
                                      )
                                    }}
                                  >
                                    <Archive className="size-4" aria-hidden="true" />
                                    Retire
                                  </Button>
                                </>
                              ) : null}
                            </div>
                          </div>

                          <div className="mt-4 grid gap-4 lg:grid-cols-2">
                            <div className="rounded-md bg-[#F8FAFC] p-4">
                              <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-[#64748B]">
                                <Link2 className="size-3.5" aria-hidden="true" />
                                Resource bindings
                              </div>
                              {deployment.effectiveResourceBindings.length === 0 ? (
                                <p className="text-sm text-[#64748B]">
                                  No effective resource bindings.
                                </p>
                              ) : (
                                <div className="grid gap-2">
                                  {deployment.effectiveResourceBindings.map((binding) => (
                                    <div
                                      key={binding.bindingReference}
                                      className="flex items-center justify-between gap-3 text-sm text-[#172033]"
                                    >
                                      <div>
                                        <span className="font-medium">
                                          {binding.resourceReference}
                                        </span>
                                        <span className="ml-2 text-xs text-[#64748B]">
                                          since {new Date(binding.validFrom).toLocaleString()} · v{binding.version}
                                        </span>
                                      </div>
                                      {deploymentActive ? (
                                        <Button
                                          type="button"
                                          variant="secondary"
                                          loading={endingBindingReference === binding.bindingReference}
                                          disabled={endingBindingReference !== null}
                                          onClick={() => void endBinding(binding)}
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
                                  <select
                                    className={inputClass}
                                    value={resourceSelections[deployment.componentDeploymentId] ?? ""}
                                    onChange={(event) =>
                                      setResourceSelections((current) => ({
                                        ...current,
                                        [deployment.componentDeploymentId]: event.target.value,
                                      }))
                                    }
                                    aria-label="Resource to bind"
                                  >
                                    <option value="">Select Resource…</option>
                                    {resources.map((resource) => (
                                      <option
                                        key={resource.resourceReference}
                                        value={resource.resourceReference}
                                      >
                                        {resource.displayName || shortId(resource.resourceReference)}
                                      </option>
                                    ))}
                                  </select>
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

                            <div className="rounded-md bg-[#F8FAFC] p-4">
                              <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-[#64748B]">
                                Communication specifications
                              </div>
                              {deployment.dcsRevisions.length === 0 ? (
                                <p className="text-sm text-[#64748B]">No communication revisions.</p>
                              ) : (
                                <div className="grid gap-3">
                                  {deployment.dcsRevisions.map((revision) => {
                                    const source = deploymentLabels.get(revision.sourceComponentDeploymentId)
                                      ?? `Deployment ${shortId(revision.sourceComponentDeploymentId)}`
                                    const destination = deploymentLabels.get(revision.destinationComponentDeploymentId)
                                      ?? `Deployment ${shortId(revision.destinationComponentDeploymentId)}`
                                    const direction = revision.sourceComponentDeploymentId === deployment.componentDeploymentId
                                      ? "Outgoing"
                                      : "Incoming"
                                    return (
                                      <div key={revision.revisionId} className="rounded border border-[#E2E8F0] bg-white p-3 text-sm">
                                        <div className="flex flex-wrap items-center justify-between gap-2">
                                          <div className="font-medium text-[#172033]">
                                            {revision.displayName || `Communication ${shortId(revision.revisionId)}`}
                                          </div>
                                          <span className="text-xs font-medium text-[#64748B]">{direction}</span>
                                        </div>
                                        <div className="mt-1 text-xs text-[#475569]">
                                          {source} → {destination}
                                        </div>
                                        {revision.trafficAlternatives.length === 0 ? (
                                          <div className="mt-2 text-xs text-amber-700">
                                            Traffic semantics are unavailable for this revision.
                                          </div>
                                        ) : (
                                          <div className="mt-2 grid gap-1">
                                            {revision.trafficAlternatives.map((traffic, index) => (
                                              <div key={`${revision.revisionId}:${index}`} className="text-xs text-[#334155]">
                                                {traffic.protocol.toUpperCase()} · source {portConstraintLabel(traffic.sourcePorts)} → destination {portConstraintLabel(traffic.destinationPorts)}
                                                {traffic.serviceReference ? ` · service ${traffic.serviceReference}` : ""}
                                              </div>
                                            ))}
                                          </div>
                                        )}
                                        <div className="mt-2 font-mono text-[10px] text-[#94A3B8]">
                                          revision {revision.revisionId}
                                        </div>
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
          })}
        </div>
      )}
    </div>
  )
}
