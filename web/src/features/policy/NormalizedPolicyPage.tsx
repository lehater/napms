import { useState } from "react"

import {
  ApiError,
  getNormalizedPolicy,
  type NormalizedPolicyResponse,
  type PortConstraintDto,
} from "@/api"
import { PolicyViewControls } from "@/features/policy/PolicyViewControls"

function renderPorts(value: PortConstraintDto): string {
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

export function NormalizedPolicyPage() {
  const [result, setResult] = useState<NormalizedPolicyResponse | null>(null)
  const [error, setError] = useState<ApiError | null>(null)
  const [running, setRunning] = useState(false)

  async function run(scope: string, asOf: string) {
    setRunning(true)
    setError(null)
    try {
      setResult(await getNormalizedPolicy(scope, asOf))
    } catch (caught) {
      setResult(null)
      setError(
        caught instanceof ApiError
          ? caught
          : new ApiError(500, "InternalError", "Normalized policy could not be loaded."),
      )
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="mx-auto max-w-[1460px]">
      <header className="mb-6">
        <div className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#64748B]">
          Policy Views
        </div>
        <h1 className="text-[28px] font-bold tracking-tight text-[#172033]">
          Normalized Policy
        </h1>
        <p className="mt-2 max-w-3xl text-sm text-[#64748B]">
          Vendor-neutral effective policy projection with Rule, Authority, ACC and RC
          provenance preserved.
        </p>
      </header>

      <PolicyViewControls onRun={run} running={running} />

      {error ? (
        <div
          role="alert"
          className="mt-5 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800"
        >
          <div className="font-semibold">{error.code}</div>
          <div className="mt-1">{error.message}</div>
          {error.correlationId ? (
            <div className="mt-2 text-xs">Correlation: {error.correlationId}</div>
          ) : null}
        </div>
      ) : null}

      {result ? (
        <section className="mt-5 overflow-hidden rounded-lg border border-[#E2E8F0] bg-white">
          <div className="border-b border-[#E2E8F0] px-5 py-4">
            <div className="font-semibold text-[#172033]">{result.scope}</div>
            <div className="mt-1 text-xs text-[#64748B]">
              asOf {result.asOf} · authority {result.authorityReference} ·{" "}
              {result.rows.length} row(s)
            </div>
          </div>

          {result.rows.length === 0 ? (
            <div className="p-10 text-center text-sm text-[#64748B]">
              Authorized normalized policy is empty at this instant.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[1420px] text-left text-sm">
                <thead className="bg-[#F8FAFC] text-xs uppercase tracking-wide text-[#64748B]">
                  <tr>
                    <th className="px-4 py-3 font-semibold">Rule</th>
                    <th className="px-4 py-3 font-semibold">Source</th>
                    <th className="px-4 py-3 font-semibold">Destination</th>
                    <th className="px-4 py-3 font-semibold">Protocol</th>
                    <th className="px-4 py-3 font-semibold">Source ports</th>
                    <th className="px-4 py-3 font-semibold">Destination ports</th>
                    <th className="px-4 py-3 font-semibold">Service</th>
                    <th className="px-4 py-3 font-semibold">Provenance</th>
                  </tr>
                </thead>
                <tbody>
                  {result.rows.map((row, index) => (
                    <tr
                      key={`${row.ruleId}-${row.source.endpointReference}-${row.destination.endpointReference}-${row.traffic.protocol}-${index}`}
                      className="border-t border-[#E2E8F0] align-top"
                    >
                      <td className="px-4 py-3">
                        <div className="font-mono text-xs">{row.ruleId}</div>
                        <div className="mt-1 text-xs text-[#64748B]">
                          decision {row.decisionReference ?? "—"}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="font-mono text-xs">
                          {row.source.technicalAddress}
                        </div>
                        <div className="mt-1 text-xs text-[#64748B]">
                          {row.source.resourceReference} / {row.source.endpointReference}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="font-mono text-xs">
                          {row.destination.technicalAddress}
                        </div>
                        <div className="mt-1 text-xs text-[#64748B]">
                          {row.destination.resourceReference} /{" "}
                          {row.destination.endpointReference}
                        </div>
                      </td>
                      <td className="px-4 py-3 font-mono text-xs">
                        {row.traffic.protocol}
                      </td>
                      <td className="px-4 py-3 font-mono text-xs">
                        {renderPorts(row.traffic.sourcePorts)}
                      </td>
                      <td className="px-4 py-3 font-mono text-xs">
                        {renderPorts(row.traffic.destinationPorts)}
                      </td>
                      <td className="px-4 py-3 text-xs">
                        {row.traffic.serviceReference ?? "—"}
                      </td>
                      <td className="px-4 py-3">
                        <details className="text-xs">
                          <summary className="cursor-pointer font-semibold text-[#2563EB]">
                            View
                          </summary>
                          <dl className="mt-2 grid gap-1 text-[#475569]">
                            <div>
                              <dt className="inline font-semibold">Read authority: </dt>
                              <dd className="inline font-mono">
                                {row.readAuthorityReference}
                              </dd>
                            </div>
                            <div>
                              <dt className="inline font-semibold">ACC fact: </dt>
                              <dd className="inline font-mono">
                                {row.applicationCommunicationCatalogue.factReference}
                              </dd>
                            </div>
                            <div>
                              <dt className="inline font-semibold">ACC validity: </dt>
                              <dd className="inline font-mono">
                                {row.applicationCommunicationCatalogue.validityReference}
                              </dd>
                            </div>
                            <div>
                              <dt className="inline font-semibold">ACC provenance: </dt>
                              <dd className="inline font-mono">
                                {row.applicationCommunicationCatalogue.provenanceReference}
                              </dd>
                            </div>
                            <div>
                              <dt className="inline font-semibold">Source fact: </dt>
                              <dd className="inline font-mono">
                                {row.source.factReference}
                              </dd>
                            </div>
                            <div>
                              <dt className="inline font-semibold">Source validity: </dt>
                              <dd className="inline font-mono">
                                {row.source.validityReference}
                              </dd>
                            </div>
                            <div>
                              <dt className="inline font-semibold">Source provenance: </dt>
                              <dd className="inline font-mono">
                                {row.source.provenanceReference}
                              </dd>
                            </div>
                            <div>
                              <dt className="inline font-semibold">Destination fact: </dt>
                              <dd className="inline font-mono">
                                {row.destination.factReference}
                              </dd>
                            </div>
                            <div>
                              <dt className="inline font-semibold">Destination validity: </dt>
                              <dd className="inline font-mono">
                                {row.destination.validityReference}
                              </dd>
                            </div>
                            <div>
                              <dt className="inline font-semibold">
                                Destination provenance:{" "}
                              </dt>
                              <dd className="inline font-mono">
                                {row.destination.provenanceReference}
                              </dd>
                            </div>
                          </dl>
                        </details>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      ) : null}
    </div>
  )
}
