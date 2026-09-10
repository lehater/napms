import { useEffect, useState } from "react"
import { Plus, Search, X } from "lucide-react"

import { ApiError } from "@/api"
import { Button } from "@/components/ui/Button"
import {
  createInteractionDefinition,
  TargetCatalogueApiError,
} from "@/features/catalogues/targetCatalogueCommands"
import {
  listApplicationComponents,
  type ApplicationComponentDto,
  type PortConstraintDto,
  type TrafficAlternativeDto,
} from "@/features/catalogues/targetCatalogueApi"

const inputClass =
  "min-h-10 w-full rounded-md border border-[#CBD5E1] bg-white px-3 py-2 text-sm text-[#172033] outline-none focus:border-[#2563EB] focus:ring-2 focus:ring-[#DBEAFE]"

type SelectedComponent = { id: string; name: string }
type TrafficDraft = {
  key: number
  protocol: string
  sourcePorts: string
  destinationPorts: string
  serviceReference: string
}

function ComponentPicker({
  applicationId,
  label,
  selected,
  onSelect,
}: {
  applicationId: string
  label: string
  selected: SelectedComponent | null
  onSelect: (value: SelectedComponent) => void
}) {
  const [query, setQuery] = useState("")
  const [applied, setApplied] = useState("")
  const [items, setItems] = useState<ApplicationComponentDto[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)

  useEffect(() => {
    let active = true
    setLoading(true)
    setError(null)
    void listApplicationComponents({
      applicationId,
      page: 1,
      pageSize: 20,
      search: applied,
    })
      .then((result) => {
        if (!active) return
        setItems(result.items)
        setTotal(result.total)
      })
      .catch((caught) => {
        if (active) {
          setError(
            caught instanceof ApiError
              ? caught
              : new ApiError(500, "InternalError", "Components could not be loaded."),
          )
        }
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [applicationId, applied])

  return (
    <div className="grid gap-2" role="group" aria-label={label}>
      <div className="text-sm font-semibold text-[#475569]">{label}</div>
      {selected ? (
        <div className="rounded-md border border-[#BFDBFE] bg-[#EFF6FF] px-3 py-2 text-sm font-semibold text-[#1D4ED8]">
          {selected.name}
        </div>
      ) : null}
      <form
        className="flex gap-2"
        onSubmit={(event) => {
          event.preventDefault()
          setApplied(query.trim())
        }}
      >
        <div className="relative min-w-0 flex-1">
          <Search className="pointer-events-none absolute left-3 top-3 size-4 text-[#94A3B8]" aria-hidden="true" />
          <input className={`${inputClass} pl-9`} value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search components" aria-label={`Search ${label}`} />
        </div>
        <Button type="submit" variant="secondary">Search</Button>
      </form>
      {loading ? (
        <div className="text-xs text-[#64748B]">Loading…</div>
      ) : error ? (
        <div className="text-xs text-red-700">{error.message}</div>
      ) : (
        <div className="max-h-44 overflow-y-auto rounded-md border border-[#E2E8F0] bg-white">
          {items.map((item) => (
            <button
              key={item.componentId}
              type="button"
              aria-label={item.displayName}
              className="block w-full border-b border-[#F1F5F9] px-3 py-2 text-left text-sm text-[#172033] last:border-0 hover:bg-[#F8FAFC]"
              onClick={() => onSelect({ id: item.componentId, name: item.displayName })}
            >
              <span className="font-semibold">{item.displayName}</span>
              {item.componentType ? <span className="ml-2 text-xs text-[#64748B]">{item.componentType}</span> : null}
            </button>
          ))}
          {items.length === 0 ? <div className="px-3 py-3 text-xs text-[#64748B]">No components found.</div> : null}
        </div>
      )}
      {total > items.length ? <div className="text-xs text-[#64748B]">{total} matches. Refine search to select beyond the first {items.length}.</div> : null}
    </div>
  )
}

function parsePorts(value: string): PortConstraintDto {
  const normalized = value.trim().toLowerCase()
  if (normalized === "any") return { kind: "Any" }
  if (normalized === "n/a" || normalized === "na") return { kind: "NotApplicable" }
  if (!normalized) throw new Error("Port constraint is required.")
  const ranges = normalized.split(",").map((part) => {
    const token = part.trim()
    if (!token) throw new Error("Port list contains an empty item.")
    const pieces = token.split("-")
    if (
      pieces.length < 1 ||
      pieces.length > 2 ||
      pieces.some((piece) => !piece.trim())
    ) {
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

function trafficFromDraft(draft: TrafficDraft): TrafficAlternativeDto {
  const protocol = draft.protocol.trim().toLowerCase()
  if (!protocol) throw new Error("Protocol is required for every traffic row.")
  return {
    protocol,
    sourcePorts: parsePorts(draft.sourcePorts),
    destinationPorts: parsePorts(draft.destinationPorts),
    serviceReference: draft.serviceReference.trim() || null,
  }
}

export function InteractionDefinitionCreatePanel({
  applicationId,
  onCreated,
  onCancel,
}: {
  applicationId: string
  onCreated: () => void
  onCancel: () => void
}) {
  const [source, setSource] = useState<SelectedComponent | null>(null)
  const [destination, setDestination] = useState<SelectedComponent | null>(null)
  const [rows, setRows] = useState<TrafficDraft[]>([
    { key: 1, protocol: "tcp", sourcePorts: "any", destinationPorts: "443", serviceReference: "" },
  ])
  const [nextKey, setNextKey] = useState(2)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function updateRow(key: number, field: keyof Omit<TrafficDraft, "key">, value: string) {
    setRows((current) => current.map((row) => (row.key === key ? { ...row, [field]: value } : row)))
  }

  async function save() {
    if (!source || !destination) {
      setError("Select both source and destination Components.")
      return
    }
    let traffic: TrafficAlternativeDto[]
    try {
      traffic = rows.map(trafficFromDraft)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Traffic is invalid.")
      return
    }
    setSaving(true)
    setError(null)
    try {
      await createInteractionDefinition(applicationId, {
        sourceComponentId: source.id,
        destinationComponentId: destination.id,
        trafficAlternatives: traffic,
      })
      onCreated()
    } catch (caught) {
      setError(
        caught instanceof TargetCatalogueApiError
          ? caught.message
          : "Interaction Definition could not be created.",
      )
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="grid gap-5 border-b border-[#E2E8F0] bg-[#F8FAFC] p-5">
      <div className="grid gap-4 lg:grid-cols-2">
        <ComponentPicker applicationId={applicationId} label="Source Component" selected={source} onSelect={setSource} />
        <ComponentPicker applicationId={applicationId} label="Destination Component" selected={destination} onSelect={setDestination} />
      </div>

      <div className="grid gap-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-[#172033]">Traffic</h3>
            <p className="mt-1 text-xs text-[#64748B]">Ports accept `any`, `n/a`, single ports, comma lists or ranges such as `443, 8443-8445`.</p>
          </div>
          <Button
            variant="secondary"
            onClick={() => {
              setRows((current) => [...current, { key: nextKey, protocol: "tcp", sourcePorts: "any", destinationPorts: "443", serviceReference: "" }])
              setNextKey((value) => value + 1)
            }}
          >
            <Plus className="size-4" aria-hidden="true" />Add traffic row
          </Button>
        </div>
        {rows.map((row) => (
          <div key={row.key} className="grid gap-2 rounded-md border border-[#E2E8F0] bg-white p-3 md:grid-cols-[8rem_1fr_1fr_1fr_auto]">
            <input className={inputClass} value={row.protocol} onChange={(event) => updateRow(row.key, "protocol", event.target.value)} placeholder="Protocol" aria-label="Protocol" />
            <input className={inputClass} value={row.sourcePorts} onChange={(event) => updateRow(row.key, "sourcePorts", event.target.value)} placeholder="Source ports" aria-label="Source ports" />
            <input className={inputClass} value={row.destinationPorts} onChange={(event) => updateRow(row.key, "destinationPorts", event.target.value)} placeholder="Destination ports" aria-label="Destination ports" />
            <input className={inputClass} value={row.serviceReference} onChange={(event) => updateRow(row.key, "serviceReference", event.target.value)} placeholder="Service" aria-label="Service reference" />
            <Button variant="ghost" disabled={rows.length === 1} onClick={() => setRows((current) => current.filter((item) => item.key !== row.key))} aria-label="Remove traffic row"><X className="size-4" /></Button>
          </div>
        ))}
      </div>

      {error ? <div className="text-sm text-red-700">{error}</div> : null}
      <div className="flex justify-end gap-2">
        <Button variant="secondary" onClick={onCancel}>Cancel</Button>
        <Button loading={saving} onClick={() => void save()}>Save interaction</Button>
      </div>
    </div>
  )
}
