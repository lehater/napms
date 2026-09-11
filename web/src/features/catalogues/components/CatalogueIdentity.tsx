import type { PortConstraintDto, TrafficAlternativeDto } from "@/features/catalogues/model/interaction"

export function shortId(value: string) {
  return value.length <= 18 ? value : `${value.slice(0, 8)}…${value.slice(-6)}`
}

export function displayName(name: string | null | undefined, id: string) {
  return name?.trim() || shortId(id)
}

export function portConstraintText(value: PortConstraintDto): string {
  if (value.kind === "Any" || value.kind === "NotApplicable") {
    return value.kind
  }
  return (value.ranges ?? [])
    .map((range) =>
      range.first === range.last
        ? String(range.first)
        : `${range.first}-${range.last}`,
    )
    .join(", ")
}

export function trafficAlternativeText(value: TrafficAlternativeDto): string {
  const service = value.serviceReference ? ` · ${value.serviceReference}` : ""
  return `${value.protocol} · dst ${portConstraintText(value.destinationPorts)}${service}`
}

export function CatalogueIdentity({
  name,
  id,
}: {
  name?: string | null
  id: string
}) {
  const readable = name?.trim()
  return (
    <div>
      <div className="font-medium text-[var(--napms-color-text-primary)]">
        {readable || shortId(id)}
      </div>
      {readable ? (
        <div className="mt-0.5 font-mono text-xs text-[var(--napms-color-text-secondary)]">
          {shortId(id)}
        </div>
      ) : null}
    </div>
  )
}
