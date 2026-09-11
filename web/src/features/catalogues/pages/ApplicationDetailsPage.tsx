import { useEffect, useMemo, useState } from "react"
import { Archive, ArrowLeft, Plus, RefreshCw } from "lucide-react"

import { Button } from "@/design-system/components/Button"
import { Input } from "@/design-system/components/Field"
import { InlineTextEdit } from "@/design-system/patterns/detail/InlineTextEdit"
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
  type ResourceDto,
} from "@/features/catalogues/api/catalogue"
import { ApplicationComponentSection } from "@/features/catalogues/components/ApplicationComponentSection"
import { DcsAuthoringPanel } from "@/features/catalogues/components/DcsAuthoringPanel"
import { shortId } from "@/features/catalogues/components/CatalogueIdentity"
import { ApiError } from "@/lib/api"

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError
    ? caught
    : new ApiError(500, "InternalError", fallback)
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
  const [creatingDeployment, setCreatingDeployment] = useState<string | null>(null)
  const [resources, setResources] = useState<ResourceDto[]>([])
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

  async function addDeployment(componentId: string, name: string | null) {
    setCreatingDeployment(componentId)
    setMutationError(null)
    try {
      await createCatalogueDeployment(componentId, name)
      await load()
    } catch (caught) {
      setMutationError(errorFrom(caught, "Deployment could not be created."))
    } finally {
      setCreatingDeployment(null)
    }
  }

  async function bindResource(deploymentId: string, resourceReference: string) {
    setBindingDeployment(deploymentId)
    setMutationError(null)
    try {
      await createCatalogueDeploymentResourceBinding(
        deploymentId,
        resourceReference,
        new Date().toISOString(),
      )
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
      await endCatalogueDeploymentResourceBinding(binding, new Date().toISOString())
      await load()
    } catch (caught) {
      setMutationError(errorFrom(caught, "Resource binding could not be ended."))
    } finally {
      setEndingBindingReference(null)
    }
  }

  if (loading && detail === null) {
    return <div className="text-sm text-[var(--napms-color-text-secondary)]">Loading application…</div>
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
    <div className="grid gap-6">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <button
            type="button"
            className="mb-3 inline-flex items-center gap-2 text-sm font-semibold text-[var(--napms-color-primary)] hover:underline"
            onClick={onBack}
          >
            <ArrowLeft className="size-4" aria-hidden="true" />
            Applications
          </button>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-bold text-[var(--napms-color-text-primary)]">
              {detail.application.displayName}
            </h1>
            <span className="text-xs font-semibold text-[var(--napms-color-text-secondary)]">
              {detail.application.lifecycle}
            </span>
          </div>
          <div className="mt-1 font-mono text-xs text-[var(--napms-color-text-secondary)]">
            {detail.application.applicationId} · v{detail.application.version}
          </div>
        </div>
        <div className="flex flex-wrap items-center justify-end gap-2">
          {applicationActive ? (
            <>
              <InlineTextEdit
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
                  if (!window.confirm("Retire this application? Active components must be retired first. Historical references will be preserved.")) return
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
        <section className="rounded-lg border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)] p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <Plus className="size-4 text-[var(--napms-color-primary)]" aria-hidden="true" />
            <h2 className="font-semibold text-[var(--napms-color-text-primary)]">Add component</h2>
          </div>
          <form className="flex flex-col gap-3 sm:flex-row" onSubmit={addComponent}>
            <Input
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
        <DcsAuthoringPanel currentApplicationId={applicationId} onCreated={load} />
      ) : null}

      {detail.components.length === 0 ? (
        <section className="rounded-lg border border-dashed border-[var(--napms-color-border-strong)] bg-[var(--napms-color-surface)] p-8 text-center text-sm text-[var(--napms-color-text-secondary)]">
          This application has no active components.
        </section>
      ) : (
        <div className="grid gap-5">
          {detail.components.map((component) => (
            <ApplicationComponentSection
              key={component.componentId}
              component={component}
              resources={resources}
              deploymentLabels={deploymentLabels}
              mutationKey={mutationKey}
              creatingDeployment={creatingDeployment}
              bindingDeployment={bindingDeployment}
              endingBindingReference={endingBindingReference}
              onRenameComponent={(value) =>
                runMutation(
                  `component:${component.componentId}:rename`,
                  "Component could not be renamed.",
                  () => renameCatalogueComponent(component, value ?? ""),
                )
              }
              onRetireComponent={() => {
                if (!window.confirm(`Retire ${component.displayName}? Active deployments must be retired first. Historical references will be preserved.`)) return
                void runMutation(
                  `component:${component.componentId}:retire`,
                  "Component could not be retired.",
                  () => retireCatalogueComponent(component),
                )
              }}
              onAddDeployment={(name) => addDeployment(component.componentId, name)}
              onRenameDeployment={(deployment, value) =>
                runMutation(
                  `deployment:${deployment.componentDeploymentId}:rename`,
                  "Deployment could not be renamed.",
                  () => renameCatalogueDeployment(deployment, value),
                )
              }
              onRetireDeployment={(deployment) => {
                if (!window.confirm("Retire this deployment? Existing bindings, communication revisions and policy history will be preserved.")) return
                void runMutation(
                  `deployment:${deployment.componentDeploymentId}:retire`,
                  "Deployment could not be retired.",
                  () => retireCatalogueDeployment(deployment),
                )
              }}
              onBindResource={bindResource}
              onEndBinding={endBinding}
            />
          ))}
        </div>
      )}
    </div>
  )
}
