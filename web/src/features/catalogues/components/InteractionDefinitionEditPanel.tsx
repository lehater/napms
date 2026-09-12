import { useEffect, useState } from "react"
import { X } from "lucide-react"

import { Button } from "@/design-system/components/Button"
import { Input } from "@/design-system/components/Field"
import { SearchInput } from "@/design-system/components/SearchInput"
import {
  retireInteractionDefinition,
  TargetCatalogueApiError,
  updateInteractionEndpoints,
  updateInteractionTraffic,
  type DependencyGroupDto,
  type InteractionDefinitionDto,
} from "@/features/catalogues/api/targetCommands"
import {
  listApplicationComponents,
  type ApplicationComponentDto,
} from "@/features/catalogues/api/targetCatalogue"
import { DependencyBlockPanel } from "@/features/catalogues/components/DependencyBlockPanel"
import type {
  PortConstraintDto,
  TrafficAlternativeDto,
} from "@/features/catalogues/model/interaction"
import { ApiError } from "@/lib/api"

type Choice = { id: string; name: string }
type TrafficDraft = {
  key: number
  protocol: string
  sourcePorts: string
  destinationPorts: string
  serviceReference: string
}

function messageFrom(caught: unknown, fallback: string) {
  return caught instanceof Error ? caught.message : fallback
}

function blockersFrom(caught: unknown): DependencyGroupDto[] | null {
  return caught instanceof TargetCatalogueApiError && caught.code === "CatalogueDependencyBlocked"
    ? (caught.details?.dependencies ?? [])
    : null
}

function constraintText(value: PortConstraintDto) {
  if (value.kind === "Any") return "any"
  if (value.kind === "NotApplicable") return "n/a"
  return (value.ranges ?? [])
    .map((range) => (range.first === range.last ? String(range.first) : `${range.first}-${range.last}`))
    .join(", ")
}

function parsePorts(value: string): PortConstraintDto {
  const normalized = value.trim().toLowerCase()
  if (normalized === "any") return { kind: "Any" }
  if (normalized === "n/a" || normalized === "na") return { kind: "NotApplicable" }
  if (!normalized) throw new Error("Port constraint is required.")
  const parts = normalized.split(",")
  if (parts.some((part) => !part.trim())) throw new Error("Port list contains an empty value.")
  const ranges = parts.map((part) => {
    const pieces = part.trim().split("-")
    if (pieces.length < 1 || pieces.length > 2 || pieces.some((piece) => !piece.trim())) {
      throw new Error(`Invalid port range: ${part}`)
    }
    const first = Number(pieces[0])
    const last = Number(pieces[1] ?? pieces[0])
    if (!Number.isInteger(first) || !Number.isInteger(last) || first < 0 || last > 65535 || first > last) {
      throw new Error(`Invalid port range: ${part}`)
    }
    return { first, last }
  })
  return { kind: "Ranges", ranges }
}

function trafficDrafts(values: TrafficAlternativeDto[]): TrafficDraft[] {
  return values.map((value, index) => ({
    key: index + 1,
    protocol: value.protocol,
    sourcePorts: constraintText(value.sourcePorts),
    destinationPorts: constraintText(value.destinationPorts),
    serviceReference: value.serviceReference ?? "",
  }))
}

function trafficValue(row: TrafficDraft): TrafficAlternativeDto {
  const protocol = row.protocol.trim().toLowerCase()
  if (!protocol) throw new Error("Protocol is required for every traffic row.")
  return {
    protocol,
    sourcePorts: parsePorts(row.sourcePorts),
    destinationPorts: parsePorts(row.destinationPorts),
    serviceReference: row.serviceReference.trim() || null,
  }
}

function ComponentSearch({
  applicationId,
  selected,
  onSelect,
}: {
  applicationId: string
  selected: Choice
  onSelect: (choice: Choice) => void
}) {
  const [draft, setDraft] = useState("")
  const [search, setSearch] = useState("")
  const [items, setItems] = useState<ApplicationComponentDto[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)

  useEffect(() => {
    let active = true
    setLoading(true)
    setError(null)
    void listApplicationComponents({ applicationId, page: 1, pageSize: 20, search })
      .then((result) => { if (active) setItems(result.items) })
      .catch((caught) => {
        if (active) setError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Components could not be loaded."))
      })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [applicationId, search])

  return (
    <div className="grid gap-2">
      <div className="rounded-[var(--napms-control-radius)] border border-[var(--napms-color-primary-border)] bg-[var(--napms-color-primary-subtle)] px-3 py-2 text-sm font-semibold text-[var(--napms-color-primary-hover)]">
        {selected.name}
      </div>
      <form className="flex gap-2" onSubmit={(event) => { event.preventDefault(); setSearch(draft.trim()) }}>
        <SearchInput value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Search components" aria-label="Search components" />
        <Button type="submit" variant="secondary">Search</Button>
      </form>
      {loading ? (
        <div className="text-xs text-[var(--napms-color-text-secondary)]">Loading…</div>
      ) : error ? (
        <div className="text-xs text-[var(--napms-color-danger)]">{error.message}</div>
      ) : (
        <div className="max-h-40 overflow-y-auto rounded-[var(--napms-control-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)]">
          {items.map((item) => (
            <button
              key={item.componentId}
              type="button"
              className="block w-full border-b border-[var(--napms-color-surface-muted)] px-3 py-2 text-left text-sm last:border-0 hover:bg-[var(--napms-color-surface-subtle)]"
              onClick={() => onSelect({ id: item.componentId, name: item.displayName })}
            >
              <span className="font-semibold text-[var(--napms-color-text-primary)]">{item.displayName}</span>
              {item.componentType ? <span className="ml-2 text-xs text-[var(--napms-color-text-secondary)]">{item.componentType}</span> : null}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export function InteractionDefinitionEditPanel({
  interaction,
  sourceName,
  destinationName,
  onChanged,
  onRetired,
  onCancel,
}: {
  interaction: InteractionDefinitionDto
  sourceName: string
  destinationName: string
  onChanged: (interaction: InteractionDefinitionDto) => void
  onRetired: () => void
  onCancel: () => void
}) {
  const [current, setCurrent] = useState(interaction)
  const [source, setSource] = useState<Choice>({ id: interaction.sourceComponentId, name: sourceName })
  const [destination, setDestination] = useState<Choice>({ id: interaction.destinationComponentId, name: destinationName })
  const [rows, setRows] = useState<TrafficDraft[]>(trafficDrafts(interaction.trafficAlternatives))
  const [nextKey, setNextKey] = useState(interaction.trafficAlternatives.length + 1)
  const [savingEndpoints, setSavingEndpoints] = useState(false)
  const [savingTraffic, setSavingTraffic] = useState(false)
  const [retiring, setRetiring] = useState(false)
  const [confirmRetire, setConfirmRetire] = useState(false)
  const [endpointError, setEndpointError] = useState<string | null>(null)
  const [trafficError, setTrafficError] = useState<string | null>(null)
  const [retireError, setRetireError] = useState<string | null>(null)
  const [trafficBlockers, setTrafficBlockers] = useState<DependencyGroupDto[] | null>(null)
  const [retireBlockers, setRetireBlockers] = useState<DependencyGroupDto[] | null>(null)

  async function saveEndpoints() {
    setSavingEndpoints(true)
    setEndpointError(null)
    try {
      const updated = await updateInteractionEndpoints(current, source.id, destination.id)
      setCurrent(updated)
      onChanged(updated)
    } catch (caught) {
      setEndpointError(messageFrom(caught, "Interaction endpoints could not be updated."))
    } finally {
      setSavingEndpoints(false)
    }
  }

  async function saveTraffic() {
    let traffic: TrafficAlternativeDto[]
    try {
      traffic = rows.map(trafficValue)
    } catch (caught) {
      setTrafficError(messageFrom(caught, "Traffic is invalid."))
      return
    }
    setSavingTraffic(true)
    setTrafficError(null)
    setTrafficBlockers(null)
    try {
      const updated = await updateInteractionTraffic(current, traffic)
      setCurrent(updated)
      onChanged(updated)
    } catch (caught) {
      const blockers = blockersFrom(caught)
      if (blockers) setTrafficBlockers(blockers)
      else setTrafficError(messageFrom(caught, "Interaction traffic could not be updated."))
    } finally {
      setSavingTraffic(false)
    }
  }

  async function retire() {
    setRetiring(true)
    setRetireError(null)
    setRetireBlockers(null)
    try {
      await retireInteractionDefinition(current)
      onRetired()
    } catch (caught) {
      const blockers = blockersFrom(caught)
      if (blockers) setRetireBlockers(blockers)
      else setRetireError(messageFrom(caught, "Interaction Definition could not be retired."))
    } finally {
      setRetiring(false)
      setConfirmRetire(false)
    }
  }

  return (
    <div className="my-3 grid gap-5 rounded-[var(--napms-control-radius)] bg-[var(--napms-color-surface-subtle)] p-4">
      <section className="grid gap-3">
        <div>
          <h3 className="font-semibold text-[var(--napms-color-text-primary)]">Endpoints</h3>
          <p className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">Saved independently from traffic.</p>
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          <ComponentSearch applicationId={current.applicationId} selected={source} onSelect={setSource} />
          <ComponentSearch applicationId={current.applicationId} selected={destination} onSelect={setDestination} />
        </div>
        {endpointError ? <div className="text-sm text-[var(--napms-color-danger)]">{endpointError}</div> : null}
        <div className="flex justify-end"><Button loading={savingEndpoints} onClick={() => void saveEndpoints()}>Save endpoints</Button></div>
      </section>

      <section className="grid gap-3 border-t border-[var(--napms-color-border)] pt-5">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h3 className="font-semibold text-[var(--napms-color-text-primary)]">Traffic</h3>
            <p className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">Saved as the Interaction Definition traffic truth.</p>
          </div>
          <Button variant="secondary" size="sm" onClick={() => { setRows((currentRows) => [...currentRows, { key: nextKey, protocol: "tcp", sourcePorts: "any", destinationPorts: "443", serviceReference: "" }]); setNextKey((value) => value + 1) }}>Add traffic row</Button>
        </div>
        {rows.map((row) => (
          <div key={row.key} className="grid gap-2 rounded-[var(--napms-control-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)] p-3 md:grid-cols-[8rem_1fr_1fr_1fr_auto]">
            <Input value={row.protocol} onChange={(event) => setRows((currentRows) => currentRows.map((item) => item.key === row.key ? { ...item, protocol: event.target.value } : item))} aria-label="Protocol" />
            <Input value={row.sourcePorts} onChange={(event) => setRows((currentRows) => currentRows.map((item) => item.key === row.key ? { ...item, sourcePorts: event.target.value } : item))} aria-label="Source ports" />
            <Input value={row.destinationPorts} onChange={(event) => setRows((currentRows) => currentRows.map((item) => item.key === row.key ? { ...item, destinationPorts: event.target.value } : item))} aria-label="Destination ports" />
            <Input value={row.serviceReference} onChange={(event) => setRows((currentRows) => currentRows.map((item) => item.key === row.key ? { ...item, serviceReference: event.target.value } : item))} placeholder="Service" aria-label="Service reference" />
            <Button variant="ghost" disabled={rows.length === 1} onClick={() => setRows((currentRows) => currentRows.filter((item) => item.key !== row.key))} aria-label="Remove traffic row"><X className="size-4" aria-hidden="true" /></Button>
          </div>
        ))}
        {trafficError ? <div className="text-sm text-[var(--napms-color-danger)]">{trafficError}</div> : null}
        {trafficBlockers ? <DependencyBlockPanel groups={trafficBlockers} onClose={() => setTrafficBlockers(null)} /> : null}
        <div className="flex justify-end"><Button loading={savingTraffic} onClick={() => void saveTraffic()}>Save traffic</Button></div>
      </section>

      <section className="flex flex-wrap items-center justify-between gap-2 border-t border-[var(--napms-color-border)] pt-5">
        <div>
          {retireError ? <div className="mb-2 text-sm text-[var(--napms-color-danger)]">{retireError}</div> : null}
          {confirmRetire ? (
            <div className="flex items-center gap-2">
              <span className="text-sm text-[var(--napms-color-text-secondary)]">Retire this Interaction Definition?</span>
              <Button variant="secondary" onClick={() => setConfirmRetire(false)}>Cancel</Button>
              <Button loading={retiring} onClick={() => void retire()}>Retire</Button>
            </div>
          ) : <Button variant="ghost" onClick={() => setConfirmRetire(true)}>Retire interaction</Button>}
        </div>
        <Button variant="secondary" onClick={onCancel}>Close editor</Button>
      </section>
      {retireBlockers ? <DependencyBlockPanel groups={retireBlockers} subjectKind="interaction-definition" subjectId={current.interactionDefinitionId} onClose={() => setRetireBlockers(null)} /> : null}
    </div>
  )
}
