import { useState } from "react"

import { ApiError } from "@/lib/api"
import { PolicyViewControls } from "@/features/policy/PolicyViewControls"
import {
  getNetworkOperatorRealization,
  type NetworkOperatorRealizationResponse,
} from "@/features/realization/api"

function ruleId(reference: string): string | null {
  return reference.startsWith("access-rule:") ? reference.slice("access-rule:".length) : null
}

function AvailabilityBadge({ value }: { value: string }) {
  return (
    <span className="rounded-full border border-[#CBD5E1] bg-[#F8FAFC] px-2.5 py-1 text-xs font-semibold text-[#475569]">
      {value}
    </span>
  )
}

function StageCard({
  title,
  availability,
  children,
}: {
  title: string
  availability: string
  children: React.ReactNode
}) {
  return (
    <section className="rounded-lg border border-[#E2E8F0] bg-white p-5">
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="font-semibold text-[#172033]">{title}</h2>
        <AvailabilityBadge value={availability} />
      </div>
      {children}
    </section>
  )
}

export function NetworkOperatorRealizationPage({
  onOpenRule,
}: {
  onOpenRule: (ruleId: string) => void
}) {
  const [result, setResult] = useState<NetworkOperatorRealizationResponse | null>(null)
  const [error, setError] = useState<ApiError | null>(null)
  const [running, setRunning] = useState(false)

  async function run(scope: string, asOf: string) {
    setRunning(true)
    setError(null)
    try {
      setResult(await getNetworkOperatorRealization(scope, asOf))
    } catch (caught) {
      setResult(null)
      setError(
        caught instanceof ApiError
          ? caught
          : new ApiError(500, "InternalError", "Operator realization could not be loaded."),
      )
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="mx-auto max-w-[1280px]">
      <header className="mb-6">
        <div className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#64748B]">
          Network Operations
        </div>
        <h1 className="text-[28px] font-bold tracking-tight text-[#172033]">
          Realization
        </h1>
        <p className="mt-2 max-w-3xl text-sm text-[#64748B]">
          Read-only view of desired policy, enforcement placement, reconciliation,
          rendered target configuration and actual controlled-operation evidence.
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
        </div>
      ) : null}

      {result ? (
        <div className="mt-5 space-y-4">
          <div className="rounded-lg border border-[#E2E8F0] bg-white px-5 py-4">
            <div className="font-semibold text-[#172033]">{result.scope}</div>
            <div className="mt-1 text-xs text-[#64748B]">
              asOf {result.asOf} · authority {result.authorityReference}
            </div>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <StageCard title="Desired and placement" availability={result.desired.availability}>
              <div className="text-sm text-[#475569]">
                APR status: <span className="font-medium text-[#172033]">{result.desired.status ?? "—"}</span>
              </div>
              {result.desired.ruleReferences.length ? (
                <div className="mt-4">
                  <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-[#64748B]">
                    Contributing rules
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {result.desired.ruleReferences.map((reference) => {
                      const id = ruleId(reference)
                      return id ? (
                        <button
                          key={reference}
                          type="button"
                          className="font-mono text-xs text-[#2563EB] hover:underline"
                          onClick={() => onOpenRule(id)}
                        >
                          {reference}
                        </button>
                      ) : (
                        <span key={reference} className="font-mono text-xs text-[#475569]">
                          {reference}
                        </span>
                      )
                    })}
                  </div>
                </div>
              ) : null}
              {result.desired.targets.map((target) => (
                <div key={`${target.logicalFirewallId}:${target.enforcementAttachmentId}`} className="mt-4 rounded-md bg-[#F8FAFC] p-3 text-xs text-[#475569]">
                  <div>Firewall: <span className="font-mono">{target.logicalFirewallId}</span></div>
                  <div className="mt-1">Attachment: <span className="font-mono">{target.enforcementAttachmentId}</span></div>
                  {target.placementProvenanceReferences.length ? (
                    <div className="mt-2">Placement provenance: {target.placementProvenanceReferences.join(", ")}</div>
                  ) : null}
                </div>
              ))}
              {result.desired.reason ? <div className="mt-3 text-xs text-[#64748B]">{result.desired.reason}</div> : null}
            </StageCard>

            <StageCard title="Reconciliation" availability={result.reconciliation.availability}>
              <div className="text-sm text-[#475569]">
                Status: <span className="font-medium text-[#172033]">{result.reconciliation.status ?? "Not selected"}</span>
              </div>
              <div className="mt-2 text-sm text-[#475569]">
                Required change: <span className="font-medium text-[#172033]">{result.reconciliation.requiredChange ?? "—"}</span>
              </div>
              {result.reconciliation.reason ? <div className="mt-3 text-xs text-[#64748B]">{result.reconciliation.reason}</div> : null}
            </StageCard>

            <StageCard title="Rendered configuration" availability={result.rendering.availability}>
              {result.rendering.artifacts.length ? (
                <div className="space-y-3">
                  {result.rendering.artifacts.map((artifact) => (
                    <div key={`${artifact.logicalFirewallId}:${artifact.enforcementAttachmentId}`}>
                      <div className="text-xs text-[#64748B]">
                        {artifact.rendererName} · contract {artifact.rendererContractVersion}
                      </div>
                      {artifact.content ? (
                        <pre className="mt-2 overflow-x-auto rounded-md bg-[#0F172A] p-3 text-xs text-white">
                          {artifact.content}
                        </pre>
                      ) : null}
                      {artifact.reason ? <div className="mt-2 text-xs text-[#64748B]">{artifact.reason}</div> : null}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-sm text-[#64748B]">No rendered artifact is available.</div>
              )}
            </StageCard>

            <StageCard title="Controlled operation" availability={result.operation.availability}>
              <div className="text-sm text-[#475569]">
                Outcome: <span className="font-medium text-[#172033]">{result.operation.outcome ?? "No operation evidence"}</span>
              </div>
              {result.operation.operationId ? (
                <div className="mt-2 font-mono text-xs text-[#475569]">{result.operation.operationId}</div>
              ) : null}
              {result.operation.provenanceReferences.length ? (
                <div className="mt-3 text-xs text-[#64748B]">
                  Provenance: {result.operation.provenanceReferences.join(", ")}
                </div>
              ) : null}
              {result.operation.reason ? <div className="mt-3 text-xs text-[#64748B]">{result.operation.reason}</div> : null}
            </StageCard>
          </div>
        </div>
      ) : null}
    </div>
  )
}
