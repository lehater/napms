import type { PortConstraintDto, TrafficAlternativeDto } from "@/features/catalogues/model/interaction"

function rangeText(constraint: PortConstraintDto): string {
  if (constraint.kind === "Any") return "any"
  if (constraint.kind === "NotApplicable") return "n/a"
  const ranges = constraint.ranges ?? []
  const ports = ranges.flatMap((range) => {
    if (range.first === range.last) return [String(range.first)]
    return [`${range.first}–${range.last}`]
  })
  if (ports.length <= 3) return ports.join(", ")
  return `${ports.length} port ranges`
}

export function trafficSummary(alternatives: TrafficAlternativeDto[]): string {
  if (alternatives.length === 0) return "—"
  const rendered = alternatives.map((item) => {
    const protocol = item.protocol.toUpperCase()
    const destination = rangeText(item.destinationPorts)
    return destination === "n/a" ? protocol : `${protocol} (${destination})`
  })
  if (rendered.length <= 2) return rendered.join(", ")
  return `${rendered.slice(0, 2).join(", ")} +${rendered.length - 2}`
}

export function resourceCount(count: number): string {
  return `${count} ${count === 1 ? "resource" : "resources"}`
}
