import { useEffect, useMemo, useState } from "react"
import { ArrowRight, Plus } from "lucide-react"

import { ApiError } from "@/lib/api"
import { shortId } from "@/features/catalogues/components/CatalogueIdentity"
import { Button } from "@/components/ui/Button"
import {
  createCatalogueDcsRevision,
  listCatalogueApplicationParticipants,
  type ApplicationCatalogueParticipantDto,
} from "@/features/catalogues/catalogueApi"

const inputClass =
  "min-h-10 w-full rounded-md border border-[#CBD5E1] bg-white px-3 py-2 text-sm text-[#172033] outline-none focus:border-[#2563EB] focus:ring-2 focus:ring-[#DBEAFE]"

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError
    ? caught
    : new ApiError(500, "InternalError", fallback)
}

function participantLabel(item: ApplicationCatalogueParticipantDto) {
  const deployment =
    item.deploymentDisplayName?.trim() || shortId(item.componentDeploymentId)
  return `${item.applicationDisplayName} / ${item.componentDisplayName} / ${deployment}`
}

export function DcsAuthoringPanel({
  currentApplicationId,
  onCreated,
}: {
  currentApplicationId: string
  onCreated: () => Promise<void>
}) {
  const [searchInput, setSearchInput] = useState("")
  const [search, setSearch] = useState("")
  const [participants, setParticipants] = useState<
    ApplicationCatalogueParticipantDto[]
  >([])
  const [hasMore, setHasMore] = useState(false)
  const [loadingParticipants, setLoadingParticipants] = useState(true)
  const [sourceId, setSourceId] = useState("")
  const [destinationId, setDestinationId] = useState("")
  const [displayName, setDisplayName] = useState("")
  const [protocol, setProtocol] = useState<"tcp" | "udp">("tcp")
  const [destinationPort, setDestinationPort] = useState("443")
  const [serviceReference, setServiceReference] = useState("")
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  useEffect(() => {
    const timer = window.setTimeout(() => setSearch(searchInput.trim()), 250)
    return () => window.clearTimeout(timer)
  }, [searchInput])

  useEffect(() => {
    let active = true
    setLoadingParticipants(true)
    setError(null)
    void listCatalogueApplicationParticipants(1, search)
      .then((result) => {
        if (!active) return
        setParticipants(result.items)
        setHasMore(result.hasMore)
      })
      .catch((caught) => {
        if (!active) return
        setParticipants([])
        setHasMore(false)
        setError(
          errorFrom(caught, "Application participants could not be loaded."),
        )
      })
      .finally(() => {
        if (active) setLoadingParticipants(false)
      })
    return () => {
      active = false
    }
  }, [search])

  const orderedParticipants = useMemo(
    () =>
      [...participants].sort((left, right) => {
        const leftLocal = left.applicationId === currentApplicationId ? 0 : 1
        const rightLocal = right.applicationId === currentApplicationId ? 0 : 1
        return (
          leftLocal - rightLocal ||
          participantLabel(left).localeCompare(participantLabel(right))
        )
      }),
    [currentApplicationId, participants],
  )

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    const port = Number(destinationPort)
    if (
      !sourceId ||
      !destinationId ||
      !Number.isInteger(port) ||
      port < 0 ||
      port > 65535
    ) {
      setError(
        new ApiError(
          422,
          "ValidationError",
          "Select source and destination deployments and enter a port within 0..65535.",
        ),
      )
      return
    }

    setCreating(true)
    setError(null)
    setMessage(null)
    try {
      const revision = await createCatalogueDcsRevision({
        sourceComponentDeploymentId: sourceId,
        destinationComponentDeploymentId: destinationId,
        displayName: displayName.trim() || null,
        protocol,
        destinationPort: port,
        serviceReference: serviceReference.trim() || null,
      })
      setMessage(
        `Communication specification ${revision.displayName || shortId(revision.revisionId)} created.`,
      )
      setDisplayName("")
      setServiceReference("")
      await onCreated()
    } catch (caught) {
      setError(errorFrom(caught, "Communication specification could not be created."))
    } finally {
      setCreating(false)
    }
  }

  return (
    <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <Plus className="size-4 text-[#2563EB]" aria-hidden="true" />
        <div>
          <h2 className="font-semibold text-[#172033]">
            Add communication specification
          </h2>
          <p className="mt-1 text-xs text-[#64748B]">
            Choose Active deployments from the catalogue; stable IDs are resolved by the backend discovery projection.
          </p>
        </div>
      </div>

      <form className="grid gap-4" onSubmit={submit}>
        <label className="grid gap-2 text-sm font-medium text-[#334155]">
          <span>Find participant</span>
          <input
            className={inputClass}
            value={searchInput}
            onChange={(event) => setSearchInput(event.target.value)}
            placeholder="Application, component or deployment"
            maxLength={256}
          />
          {hasMore ? (
            <span className="text-xs font-normal text-[#64748B]">
              More matches exist. Refine the search to narrow the participant list.
            </span>
          ) : null}
        </label>

        <div className="grid gap-3 lg:grid-cols-[1fr_auto_1fr] lg:items-end">
          <label className="grid gap-2 text-sm font-medium text-[#334155]">
            <span>Source deployment</span>
            <select
              className={inputClass}
              value={sourceId}
              onChange={(event) => setSourceId(event.target.value)}
              disabled={loadingParticipants}
            >
              <option value="">
                {loadingParticipants ? "Loading participants…" : "Select source…"}
              </option>
              {orderedParticipants.map((item) => (
                <option
                  key={`source:${item.componentDeploymentId}`}
                  value={item.componentDeploymentId}
                >
                  {participantLabel(item)}
                </option>
              ))}
            </select>
          </label>

          <ArrowRight
            className="mx-auto mb-3 hidden size-5 text-[#94A3B8] lg:block"
            aria-hidden="true"
          />

          <label className="grid gap-2 text-sm font-medium text-[#334155]">
            <span>Destination deployment</span>
            <select
              className={inputClass}
              value={destinationId}
              onChange={(event) => setDestinationId(event.target.value)}
              disabled={loadingParticipants}
            >
              <option value="">
                {loadingParticipants
                  ? "Loading participants…"
                  : "Select destination…"}
              </option>
              {orderedParticipants.map((item) => (
                <option
                  key={`destination:${item.componentDeploymentId}`}
                  value={item.componentDeploymentId}
                >
                  {participantLabel(item)}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <label className="grid gap-2 text-sm font-medium text-[#334155]">
            <span>Label</span>
            <input
              className={inputClass}
              value={displayName}
              onChange={(event) => setDisplayName(event.target.value)}
              placeholder="HTTPS Orders API"
              maxLength={256}
            />
          </label>

          <label className="grid gap-2 text-sm font-medium text-[#334155]">
            <span>Protocol</span>
            <select
              className={inputClass}
              value={protocol}
              onChange={(event) =>
                setProtocol(event.target.value as "tcp" | "udp")
              }
            >
              <option value="tcp">TCP</option>
              <option value="udp">UDP</option>
            </select>
          </label>

          <label className="grid gap-2 text-sm font-medium text-[#334155]">
            <span>Destination port</span>
            <input
              className={inputClass}
              type="number"
              min={0}
              max={65535}
              step={1}
              value={destinationPort}
              onChange={(event) => setDestinationPort(event.target.value)}
            />
          </label>

          <label className="grid gap-2 text-sm font-medium text-[#334155]">
            <span>Service reference</span>
            <input
              className={inputClass}
              value={serviceReference}
              onChange={(event) => setServiceReference(event.target.value)}
              placeholder="Optional"
              maxLength={256}
            />
          </label>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-xs text-[#64748B]">
            Creating a specification creates a new immutable DCS revision; existing revisions are not edited in place.
          </p>
          <Button
            type="submit"
            loading={creating}
            disabled={!sourceId || !destinationId || !destinationPort.trim()}
          >
            Create specification
          </Button>
        </div>
      </form>

      {error ? <p className="mt-3 text-sm text-red-700">{error.message}</p> : null}
      {message ? (
        <p className="mt-3 text-sm text-green-700">{message}</p>
      ) : null}
    </section>
  )
}
