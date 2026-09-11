import { useMemo } from "react"
import { Search } from "lucide-react"

import { Field, Select } from "@/design-system/components/Field"
import {
  shortId,
  trafficAlternativeText,
} from "@/features/catalogues/components/CatalogueIdentity"
import type { ProposalInteraction } from "@/features/catalogues/model/interaction"

export function catalogueOptionLabel(
  name: string | null | undefined,
  id: string,
) {
  const readable = name?.trim()
  return readable ? `${readable} · ${shortId(id)}` : shortId(id)
}

export function catalogueDcsLabel(item: ProposalInteraction) {
  const base = catalogueOptionLabel(
    item.catalogue?.dcsDisplayName,
    item.dcsContractRevisionId,
  )
  const alternatives = item.catalogue?.trafficAlternatives ?? []
  return alternatives.length > 0
    ? `${base} — ${alternatives.map(trafficAlternativeText).join(" | ")}`
    : base
}

export function CatalogueInteractionSelector({
  interactions,
  searchInput,
  onSearchInputChange,
  searchDisabled = false,
  searchLabel = "Search interaction",
  searchPlaceholder = "Search interactions",
  loading = false,
  source,
  onSourceChange,
  destination,
  onDestinationChange,
  dcs,
  onDcsChange,
  disabled = false,
}: {
  interactions: ProposalInteraction[]
  searchInput: string
  onSearchInputChange: (value: string) => void
  searchDisabled?: boolean
  searchLabel?: string
  searchPlaceholder?: string
  loading?: boolean
  source: string
  onSourceChange: (value: string) => void
  destination: string
  onDestinationChange: (value: string) => void
  dcs: string
  onDcsChange: (value: string) => void
  disabled?: boolean
}) {
  const sourceOptions = useMemo(() => {
    const values = new Map<string, string | null | undefined>()
    for (const item of interactions) {
      if (!values.has(item.sourceComponentDeploymentId)) {
        values.set(
          item.sourceComponentDeploymentId,
          item.catalogue?.sourceDisplayName,
        )
      }
    }
    return [...values.entries()]
  }, [interactions])

  const destinationOptions = useMemo(() => {
    const values = new Map<string, string | null | undefined>()
    for (const item of interactions) {
      if (item.sourceComponentDeploymentId !== source) continue
      if (!values.has(item.destinationComponentDeploymentId)) {
        values.set(
          item.destinationComponentDeploymentId,
          item.catalogue?.destinationDisplayName,
        )
      }
    }
    return [...values.entries()]
  }, [interactions, source])

  const dcsOptions = useMemo(
    () =>
      interactions.filter(
        (item) =>
          item.sourceComponentDeploymentId === source &&
          item.destinationComponentDeploymentId === destination,
      ),
    [interactions, source, destination],
  )

  return (
    <>
      <Field label={searchLabel}>
        <div className="relative">
          <Search
            className="pointer-events-none absolute left-3 top-3 size-4 text-[#94A3B8]"
            aria-hidden="true"
          />
          <input
            type="search"
            value={searchInput}
            maxLength={256}
            onChange={(event) => onSearchInputChange(event.target.value)}
            disabled={searchDisabled}
            placeholder={searchPlaceholder}
            className="min-h-10 w-full rounded-md border border-[#CBD5E1] py-2 pl-9 pr-3 text-sm disabled:bg-[#F8FAFC]"
          />
        </div>
      </Field>

      <Field label="Source Component Deployment">
        <Select
          value={source}
          onChange={(event) => onSourceChange(event.target.value)}
          disabled={disabled || loading}
          required
        >
          <option value="">Select source</option>
          {sourceOptions.map(([id, name]) => (
            <option key={id} value={id}>{catalogueOptionLabel(name, id)}</option>
          ))}
        </Select>
      </Field>

      <Field label="Destination Component Deployment">
        <Select
          value={destination}
          onChange={(event) => onDestinationChange(event.target.value)}
          disabled={disabled || !source || loading}
          required
        >
          <option value="">Select destination</option>
          {destinationOptions.map(([id, name]) => (
            <option key={id} value={id}>{catalogueOptionLabel(name, id)}</option>
          ))}
        </Select>
      </Field>

      <Field label="DCS / Access">
        <Select
          value={dcs}
          onChange={(event) => onDcsChange(event.target.value)}
          disabled={disabled || !destination || loading}
          required
        >
          <option value="">Select access</option>
          {dcsOptions.map((item) => (
            <option
              key={item.dcsContractRevisionId}
              value={item.dcsContractRevisionId}
            >
              {catalogueDcsLabel(item)}
            </option>
          ))}
        </Select>
      </Field>
    </>
  )
}
