import { useEffect, useState } from "react"
import { ArrowLeft } from "lucide-react"

import { ApiError } from "@/api"
import { Button } from "@/components/ui/Button"
import {
  listDeploymentConnectivity,
  readApplicationDeployment,
  type ApplicationDeploymentDto,
  type DeploymentConnectivityDto,
} from "@/features/catalogues/targetCatalogueApi"
import { resourceCount, trafficSummary } from "@/features/catalogues/targetPresentation"

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError
    ? caught
    : new ApiError(500, "InternalError", fallback)
}

export function ApplicationDeploymentPage({
  deploymentId,
  onBack,
}: {
  deploymentId: string
  onBack: () => void
}) {
  const [deployment, setDeployment] = useState<ApplicationDeploymentDto | null>(null)
  const [applicationName, setApplicationName] = useState<string | null>(null)
  const [connectivity, setConnectivity] = useState<DeploymentConnectivityDto[]>([])
  const [selectedTotal, setSelectedTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)

  useEffect(() => {
    let active = true
    setLoading(true)
    setError(null)
    void Promise.all([
      readApplicationDeployment(deploymentId),
      listDeploymentConnectivity({ applicationDeploymentId: deploymentId, page: 1 }),
    ])
      .then(([detail, rows]) => {
        if (!active) return
        setDeployment(detail.deployment)
        setApplicationName(detail.applicationName)
        setConnectivity(rows.items)
        setSelectedTotal(rows.total)
      })
      .catch((caught) => {
        if (active) setError(errorFrom(caught, "Application Deployment could not be loaded."))
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [deploymentId])

  return (
    <div className="mx-auto grid max-w-7xl gap-5">
      <div>
        <Button variant="ghost" className="-ml-3" onClick={onBack}>
          <ArrowLeft className="size-4" aria-hidden="true" />
          Deployments
        </Button>
      </div>

      {loading ? (
        <section className="rounded-lg border border-[#E2E8F0] bg-white p-6 text-sm text-[#64748B]">
          Loading deployment…
        </section>
      ) : error ? (
        <section className="rounded-lg border border-[#E2E8F0] bg-white p-6 text-sm text-red-700">
          {error.message}
        </section>
      ) : deployment ? (
        <>
          <header>
            <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[#64748B]">
              Applications / Deployments
            </div>
            <h1 className="mt-1 text-2xl font-bold text-[#172033]">
              {applicationName ?? "Application"} — {deployment.companyReference} / {deployment.environment}
            </h1>
          </header>

          <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
            <dl className="grid gap-4 md:grid-cols-4">
              <div>
                <dt className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">Application</dt>
                <dd className="mt-1 text-sm font-medium text-[#172033]">{applicationName ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">Company</dt>
                <dd className="mt-1 text-sm text-[#172033]">{deployment.companyReference}</dd>
              </div>
              <div>
                <dt className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">Environment</dt>
                <dd className="mt-1 text-sm text-[#172033]">{deployment.environment}</dd>
              </div>
              <div>
                <dt className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">Scope</dt>
                <dd className="mt-1 text-sm text-[#172033]">{deployment.scopeReference}</dd>
              </div>
            </dl>
          </section>

          <section className="overflow-hidden rounded-lg border border-[#E2E8F0] bg-white shadow-sm">
            <div className="flex items-center justify-between border-b border-[#E2E8F0] px-5 py-4">
              <h2 className="font-semibold text-[#172033]">Connectivity</h2>
              <span className="text-sm font-medium text-[#64748B]">{selectedTotal} selected interactions</span>
            </div>
            {connectivity.length === 0 ? (
              <div className="p-6 text-sm text-[#64748B]">No interactions are selected for this deployment.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[980px] text-left text-sm">
                  <thead className="bg-[#F8FAFC] text-xs font-semibold uppercase tracking-wide text-[#64748B]">
                    <tr>
                      <th className="px-5 py-3">Source component</th>
                      <th className="px-5 py-3 text-right">Source resources</th>
                      <th className="px-5 py-3">Destination component</th>
                      <th className="px-5 py-3 text-right">Destination resources</th>
                      <th className="px-5 py-3">Traffic</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E2E8F0]">
                    {connectivity.map((item) => (
                      <tr key={item.deploymentInteractionId}>
                        <td className="px-5 py-3 font-semibold text-[#172033]">{item.sourceComponent.displayName}</td>
                        <td className="px-5 py-3 text-right tabular-nums text-[#475569]">{resourceCount(item.sourceComponent.resourceCount)}</td>
                        <td className="px-5 py-3 font-semibold text-[#172033]">{item.destinationComponent.displayName}</td>
                        <td className="px-5 py-3 text-right tabular-nums text-[#475569]">{resourceCount(item.destinationComponent.resourceCount)}</td>
                        <td className="px-5 py-3 text-[#475569]">{trafficSummary(item.trafficAlternatives)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      ) : null}
    </div>
  )
}
