import { useEffect, useState } from "react"
import { ArrowLeft, Network, Plus, RefreshCw, Users } from "lucide-react"

import { ApiError } from "@/api"
import { shortId } from "@/components/catalogue/CatalogueIdentity"
import { Button } from "@/components/ui/Button"
import {
  createCatalogueResourceRealization,
  readCatalogueResource,
  type ResourceDetailDto,
} from "@/features/catalogues/catalogueApi"

const inputClass =
  "min-h-10 w-full rounded-md border border-[#CBD5E1] bg-white px-3 py-2 text-sm text-[#172033] outline-none focus:border-[#2563EB] focus:ring-2 focus:ring-[#DBEAFE]"

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError
    ? caught
    : new ApiError(500, "InternalError", fallback)
}

export function ResourceDetailsPage({
  resourceReference,
  onBack,
}: {
  resourceReference: string
  onBack: () => void
}) {
  const [detail, setDetail] = useState<ResourceDetailDto | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)
  const [addresses, setAddresses] = useState("")
  const [creatingRealization, setCreatingRealization] = useState(false)
  const [mutationError, setMutationError] = useState<ApiError | null>(null)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      setDetail(await readCatalogueResource(resourceReference))
    } catch (caught) {
      setError(errorFrom(caught, "Resource details could not be loaded."))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [resourceReference])

  async function addRealization(event: React.FormEvent) {
    event.preventDefault()
    const values = addresses
      .split(/[\n,]+/)
      .map((value) => value.trim())
      .filter(Boolean)
    if (values.length === 0) return
    setCreatingRealization(true)
    setMutationError(null)
    try {
      await createCatalogueResourceRealization(
        resourceReference,
        values,
        new Date().toISOString(),
      )
      setAddresses("")
      await load()
    } catch (caught) {
      setMutationError(errorFrom(caught, "Resource realization could not be created."))
    } finally {
      setCreatingRealization(false)
    }
  }

  if (loading && detail === null) {
    return <div className="text-sm text-[#64748B]">Loading resource…</div>
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
            Resources
          </button>
          <h1 className="text-2xl font-bold text-[#172033]">
            {detail.resource.displayName || shortId(detail.resource.resourceReference)}
          </h1>
          <div className="mt-1 font-mono text-xs text-[#64748B]">
            {detail.resource.resourceReference}
          </div>
        </div>
        <Button variant="secondary" loading={loading} onClick={() => void load()}>
          <RefreshCw className="size-4" aria-hidden="true" />
          Refresh
        </Button>
      </header>

      <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
        <div className="mb-4 flex items-center gap-2">
          <Plus className="size-4 text-[#2563EB]" aria-hidden="true" />
          <h2 className="font-semibold text-[#172033]">Add technical addresses</h2>
        </div>
        <form className="grid gap-3" onSubmit={addRealization}>
          <textarea
            className={`${inputClass} min-h-24 resize-y`}
            value={addresses}
            onChange={(event) => setAddresses(event.target.value)}
            placeholder={"10.20.30.40\n10.20.30.41"}
            aria-label="Technical addresses"
          />
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-xs text-[#64748B]">
              One address per line or comma. A new authoritative realization starts now.
            </p>
            <Button type="submit" loading={creatingRealization} disabled={!addresses.trim()}>
              Add addresses
            </Button>
          </div>
        </form>
        {mutationError ? (
          <p className="mt-3 text-sm text-red-700">{mutationError.message}</p>
        ) : null}
      </section>

      <div className="grid gap-5 lg:grid-cols-2">
        <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <Network className="size-4 text-[#64748B]" aria-hidden="true" />
            <h2 className="font-semibold text-[#172033]">Current realization</h2>
          </div>
          {detail.effectiveRealizations.length === 0 ? (
            <p className="text-sm text-[#64748B]">No current technical addresses.</p>
          ) : (
            <div className="grid gap-4">
              {detail.effectiveRealizations.map((realization) => (
                <div key={realization.factReference} className="rounded-md bg-[#F8FAFC] p-4">
                  <div className="grid gap-2">
                    {realization.technicalAddresses.map((endpoint) => (
                      <div key={`${endpoint.endpointReference}:${endpoint.technicalAddress}`}>
                        <div className="font-mono text-sm font-semibold text-[#172033]">
                          {endpoint.technicalAddress}
                        </div>
                        <div className="font-mono text-[11px] text-[#64748B]">
                          {shortId(endpoint.endpointReference)}
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-3 text-xs text-[#64748B]">
                    Effective from {new Date(realization.validFrom).toLocaleString()} · v{realization.version}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
          <h2 className="font-semibold text-[#172033]">Responsibility scopes</h2>
          {detail.effectiveScopeAffiliations.length === 0 ? (
            <p className="mt-4 text-sm text-[#64748B]">No current scope affiliations.</p>
          ) : (
            <div className="mt-4 grid gap-2">
              {detail.effectiveScopeAffiliations.map((item) => (
                <div key={item.affiliationReference} className="rounded-md bg-[#F8FAFC] px-4 py-3">
                  <div className="font-medium text-[#172033]">{item.responsibilityScope}</div>
                  <div className="mt-1 text-xs text-[#64748B]">
                    since {new Date(item.validFrom).toLocaleString()} · v{item.version}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
        <div className="mb-4 flex items-center gap-2">
          <Users className="size-4 text-[#64748B]" aria-hidden="true" />
          <h2 className="font-semibold text-[#172033]">Responsibilities</h2>
        </div>
        {detail.effectiveResponsibilities.length === 0 ? (
          <p className="text-sm text-[#64748B]">No current responsibility assignments.</p>
        ) : (
          <div className="grid gap-3 md:grid-cols-2">
            {detail.effectiveResponsibilities.map((item) => (
              <div key={item.assignmentReference} className="rounded-md border border-[#E2E8F0] p-4">
                <div className="font-semibold text-[#172033]">{item.displayName}</div>
                <div className="mt-1 text-sm text-[#64748B]">
                  {item.role} · {item.partyKind}
                </div>
                <div className="mt-2 font-mono text-xs text-[#64748B]">{item.partyReference}</div>
                {item.contact ? (
                  <div className="mt-2 text-sm text-[#172033]">{item.contact}</div>
                ) : null}
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
