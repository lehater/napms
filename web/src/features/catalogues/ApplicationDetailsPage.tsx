import { useEffect, useState } from "react"
import { ArrowLeft, Boxes, Link2, Plus, RefreshCw } from "lucide-react"

import { ApiError } from "@/api"
import { shortId } from "@/components/catalogue/CatalogueIdentity"
import { Button } from "@/components/ui/Button"
import {
  createCatalogueComponent,
  createCatalogueDeployment,
  readCatalogueApplication,
  type ApplicationTreeDto,
} from "@/features/catalogues/catalogueApi"

const inputClass =
  "min-h-10 w-full rounded-md border border-[#CBD5E1] bg-white px-3 py-2 text-sm text-[#172033] outline-none focus:border-[#2563EB] focus:ring-2 focus:ring-[#DBEAFE]"

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
  const [deploymentNames, setDeploymentNames] = useState<Record<string, string>>({})
  const [creatingDeployment, setCreatingDeployment] = useState<string | null>(null)
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

  useEffect(() => {
    void load()
  }, [applicationId])

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
          <h1 className="text-2xl font-bold text-[#172033]">{detail.application.displayName}</h1>
          <div className="mt-1 font-mono text-xs text-[#64748B]">{detail.application.applicationId}</div>
        </div>
        <Button variant="secondary" loading={loading} onClick={() => void load()}>
          <RefreshCw className="size-4" aria-hidden="true" />
          Refresh
        </Button>
      </header>

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
        {mutationError ? (
          <p className="mt-3 text-sm text-red-700">{mutationError.message}</p>
        ) : null}
      </section>

      {detail.components.length === 0 ? (
        <section className="rounded-lg border border-dashed border-[#CBD5E1] bg-white p-8 text-center text-sm text-[#64748B]">
          This application has no components yet. Add the first component above.
        </section>
      ) : (
        <div className="grid gap-5">
          {detail.components.map((component) => (
            <section
              key={component.componentId}
              className="rounded-lg border border-[#E2E8F0] bg-white shadow-sm"
            >
              <div className="border-b border-[#E2E8F0] p-5">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <Boxes className="size-4 text-[#64748B]" aria-hidden="true" />
                      <h2 className="font-semibold text-[#172033]">{component.displayName}</h2>
                    </div>
                    <div className="mt-1 font-mono text-[11px] text-[#64748B]">
                      {component.componentId}
                    </div>
                  </div>
                  <span className="rounded-full border border-green-200 bg-green-50 px-2 py-0.5 text-xs font-semibold text-green-800">
                    {component.lifecycle}
                  </span>
                </div>

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
                    placeholder="Deployment name (optional), e.g. prod"
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
              </div>

              {component.deployments.length === 0 ? (
                <div className="p-5 text-sm text-[#64748B]">No deployments.</div>
              ) : (
                <div className="divide-y divide-[#E2E8F0]">
                  {component.deployments.map((deployment) => (
                    <div key={deployment.componentDeploymentId} className="p-5">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <div className="font-semibold text-[#172033]">
                            {deployment.displayName || `Deployment ${shortId(deployment.componentDeploymentId)}`}
                          </div>
                          <div className="mt-1 font-mono text-[11px] text-[#64748B]">
                            {deployment.componentDeploymentId}
                          </div>
                        </div>
                        <span className="text-xs font-medium text-[#64748B]">
                          v{deployment.version} · {deployment.lifecycle}
                        </span>
                      </div>

                      <div className="mt-4 grid gap-4 lg:grid-cols-2">
                        <div className="rounded-md bg-[#F8FAFC] p-4">
                          <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-[#64748B]">
                            <Link2 className="size-3.5" aria-hidden="true" />
                            Resource bindings
                          </div>
                          {deployment.effectiveResourceBindings.length === 0 ? (
                            <p className="text-sm text-[#64748B]">No effective resource bindings.</p>
                          ) : (
                            <div className="grid gap-2">
                              {deployment.effectiveResourceBindings.map((binding) => (
                                <div key={binding.bindingReference} className="text-sm text-[#172033]">
                                  <span className="font-medium">{binding.resourceReference}</span>
                                  <span className="ml-2 text-xs text-[#64748B]">
                                    since {new Date(binding.validFrom).toLocaleString()}
                                  </span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>

                        <div className="rounded-md bg-[#F8FAFC] p-4">
                          <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-[#64748B]">
                            Communication specifications
                          </div>
                          {deployment.dcsRevisions.length === 0 ? (
                            <p className="text-sm text-[#64748B]">No DCS revisions.</p>
                          ) : (
                            <div className="grid gap-2">
                              {deployment.dcsRevisions.map((revision) => (
                                <div key={revision.revisionId} className="text-sm">
                                  <div className="font-medium text-[#172033]">
                                    {revision.displayName || shortId(revision.revisionId)}
                                  </div>
                                  <div className="text-xs text-[#64748B]">
                                    {shortId(revision.sourceComponentDeploymentId)} → {shortId(revision.destinationComponentDeploymentId)}
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>
          ))}
        </div>
      )}
    </div>
  )
}
