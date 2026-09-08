import { useState } from "react"

import {
  ApiError,
  getEffectiveDesiredPolicy,
  type EffectivePolicyResponse,
} from "@/api"
import { StatusBadge } from "@/components/ui/StatusBadge"
import { PolicyViewControls } from "@/features/policy/PolicyViewControls"

function shortId(value: string) {
  return value.length <= 18 ? value : `${value.slice(0, 8)}…${value.slice(-6)}`
}

export function EffectivePolicyPage({
  onOpenRule,
}: {
  onOpenRule: (ruleId: string) => void
}) {
  const [result, setResult] = useState<EffectivePolicyResponse | null>(null)
  const [error, setError] = useState<ApiError | null>(null)
  const [running, setRunning] = useState(false)

  async function run(scope: string, asOf: string) {
    setRunning(true)
    setError(null)
    try {
      setResult(await getEffectiveDesiredPolicy(scope, asOf))
    } catch (caught) {
      setResult(null)
      setError(
        caught instanceof ApiError
          ? caught
          : new ApiError(500, "InternalError", "Effective policy could not be loaded."),
      )
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="mx-auto max-w-[1280px]">
      <header className="mb-6">
        <div className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#64748B]">
          Policy Views
        </div>
        <h1 className="text-[28px] font-bold tracking-tight text-[#172033]">
          Effective Desired Policy
        </h1>
        <p className="mt-2 max-w-3xl text-sm text-[#64748B]">
          Authoritative Rules that contribute desired effect for one governance scope
          at one explicit instant.
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
              asOf {result.asOf} · authority {result.authorityReference}
            </div>
          </div>

          {result.rules.length === 0 ? (
            <div className="p-10 text-center text-sm text-[#64748B]">
              Authorized selection is empty at this instant.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[980px] text-left text-sm">
                <thead className="bg-[#F8FAFC] text-xs uppercase tracking-wide text-[#64748B]">
                  <tr>
                    <th className="px-5 py-3 font-semibold">Rule</th>
                    <th className="px-5 py-3 font-semibold">Source</th>
                    <th className="px-5 py-3 font-semibold">Destination</th>
                    <th className="px-5 py-3 font-semibold">DCS revision</th>
                    <th className="px-5 py-3 font-semibold">State</th>
                    <th className="px-5 py-3 font-semibold">Effective window</th>
                  </tr>
                </thead>
                <tbody>
                  {result.rules.map((rule) => (
                    <tr
                      key={rule.ruleId}
                      className="border-t border-[#E2E8F0] hover:bg-[#F8FAFC]"
                    >
                      <td className="px-5 py-3">
                        <button
                          type="button"
                          className="font-mono text-xs text-[#2563EB] hover:underline"
                          onClick={() => onOpenRule(rule.ruleId)}
                        >
                          {shortId(rule.ruleId)}
                        </button>
                      </td>
                      <td className="px-5 py-3 font-mono text-xs">
                        {shortId(rule.semanticIdentity.sourceComponentDeploymentId)}
                      </td>
                      <td className="px-5 py-3 font-mono text-xs">
                        {shortId(rule.semanticIdentity.destinationComponentDeploymentId)}
                      </td>
                      <td className="px-5 py-3 font-mono text-xs">
                        {shortId(rule.semanticIdentity.dcsContractRevisionId)}
                      </td>
                      <td className="px-5 py-3">
                        <StatusBadge value={rule.operationalState} />
                      </td>
                      <td className="px-5 py-3 text-xs text-[#475569]">
                        {rule.effectiveWindow
                          ? `${rule.effectiveWindow.start} → ${rule.effectiveWindow.end}`
                          : "No restriction"}
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
