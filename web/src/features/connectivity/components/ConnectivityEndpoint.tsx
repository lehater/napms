import type { ScopedConnectivityResource } from "@/features/connectivity/api"

export function connectivityEndpointText(resource: ScopedConnectivityResource): string {
  if (resource.realizationState === "Unknown") return "Realization unknown"
  if (resource.endpoints.length === 0) {
    return resource.realizationState === "Unresolved"
      ? "No current endpoint realization"
      : "No endpoints"
  }
  return resource.endpoints
    .map((endpoint) => endpoint.technicalAddress)
    .join(", ")
}

export function ConnectivityRemoteSide({
  resourcesKnown,
  resources,
  componentName,
  componentId,
}: {
  resourcesKnown: boolean
  resources: ScopedConnectivityResource[]
  componentName: string | null
  componentId: string
}) {
  return (
    <div className="min-w-[180px]">
      <div className="font-medium text-[var(--napms-color-text-primary)]">
        {componentName?.trim() || componentId}
      </div>
      {componentName?.trim() ? (
        <div className="mt-0.5 font-mono text-[var(--napms-font-size-caption)] text-[var(--napms-color-text-muted)]">
          {componentId}
        </div>
      ) : null}
      <div className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">
        {!resourcesKnown
          ? "Remote resource data unavailable"
          : resources.length === 0
            ? "Remote resource unresolved"
            : resources
                .map(
                  (resource) =>
                    `${resource.resourceReference} · ${connectivityEndpointText(resource)}`,
                )
                .join(" · ")}
      </div>
    </div>
  )
}
