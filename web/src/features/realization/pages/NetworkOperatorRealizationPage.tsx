import { useState } from "react"

import { ErrorState } from "@/design-system/components/PageState"
import { PageHeader } from "@/design-system/layout/PageHeader"
import { PageWorkspace } from "@/design-system/layout/PageWorkspace"
import { Surface } from "@/design-system/primitives/Surface"
import { PolicyViewControls } from "@/features/policy/components/PolicyViewControls"
import { getNetworkOperatorRealization, type NetworkOperatorRealizationResponse } from "@/features/realization/api"
import { RealizationAvailabilityStatus } from "@/features/realization/components/RealizationAvailabilityStatus"
import { ApiError } from "@/lib/api"

function ruleId(reference: string): string | null {
  return reference.startsWith("access-rule:") ? reference.slice("access-rule:".length) : null
}

function StageCard({ title, availability, children }: { title: string; availability: string; children: React.ReactNode }) {
  return (
    <Surface className="p-5">
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="font-semibold text-[var(--napms-color-text-primary)]">{title}</h2>
        <RealizationAvailabilityStatus value={availability} />
      </div>
      {children}
    </Surface>
  )
}

export function NetworkOperatorRealizationPage({ onOpenRule }: { onOpenRule: (ruleId: string) => void }) {
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
      setError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Operator realization could not be loaded."))
    } finally {
      setRunning(false)
    }
  }

  return (
    <PageWorkspace width="content">
      <PageHeader title="Realization" description="Read-only view of desired policy, enforcement placement, reconciliation, rendered target configuration and actual controlled-operation evidence." />
      <PolicyViewControls onRun={run} running={running} />
      {error ? <ErrorState message={`${error.code}: ${error.message}`} /> : null}
      {result ? (
        <div className="space-y-4">
          <Surface className="px-5 py-4">
            <div className="font-semibold text-[var(--napms-color-text-primary)]">{result.scope}</div>
            <div className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">asOf {result.asOf} · authority {result.authorityReference}</div>
          </Surface>
          <div className="grid gap-4 lg:grid-cols-2">
            <StageCard title="Desired and placement" availability={result.desired.availability}>
              <div className="text-sm text-[var(--napms-color-text-body)]">APR status: <span className="font-medium text-[var(--napms-color-text-primary)]">{result.desired.status ?? "—"}</span></div>
              {result.desired.ruleReferences.length ? <div className="mt-4"><div className="mb-2 text-xs font-semibold uppercase tracking-wide text-[var(--napms-color-text-secondary)]">Contributing rules</div><div className="flex flex-wrap gap-2">{result.desired.ruleReferences.map((reference) => { const id = ruleId(reference); return id ? <button key={reference} type="button" className="font-mono text-xs text-[var(--napms-color-primary)] hover:underline" onClick={() => onOpenRule(id)}>{reference}</button> : <span key={reference} className="font-mono text-xs text-[var(--napms-color-text-body)]">{reference}</span> })}</div></div> : null}
              {result.desired.targets.map((target) => <div key={`${target.logicalFirewallId}:${target.enforcementAttachmentId}`} className="mt-4 rounded-[var(--napms-control-radius)] bg-[var(--napms-color-surface-subtle)] p-3 text-xs text-[var(--napms-color-text-body)]"><div>Firewall: <span className="font-mono">{target.logicalFirewallId}</span></div><div className="mt-1">Attachment: <span className="font-mono">{target.enforcementAttachmentId}</span></div>{target.placementProvenanceReferences.length ? <div className="mt-2">Placement provenance: {target.placementProvenanceReferences.join(", ")}</div> : null}</div>)}
              {result.desired.reason ? <div className="mt-3 text-xs text-[var(--napms-color-text-secondary)]">{result.desired.reason}</div> : null}
            </StageCard>
            <StageCard title="Reconciliation" availability={result.reconciliation.availability}>
              <div className="text-sm text-[var(--napms-color-text-body)]">Status: <span className="font-medium text-[var(--napms-color-text-primary)]">{result.reconciliation.status ?? "Not selected"}</span></div>
              <div className="mt-2 text-sm text-[var(--napms-color-text-body)]">Required change: <span className="font-medium text-[var(--napms-color-text-primary)]">{result.reconciliation.requiredChange ?? "—"}</span></div>
              {result.reconciliation.reason ? <div className="mt-3 text-xs text-[var(--napms-color-text-secondary)]">{result.reconciliation.reason}</div> : null}
            </StageCard>
            <StageCard title="Rendered configuration" availability={result.rendering.availability}>
              {result.rendering.artifacts.length ? <div className="space-y-3">{result.rendering.artifacts.map((artifact) => <div key={`${artifact.logicalFirewallId}:${artifact.enforcementAttachmentId}`}><div className="text-xs text-[var(--napms-color-text-secondary)]">{artifact.rendererName} · contract {artifact.rendererContractVersion}</div>{artifact.content ? <pre className="mt-2 overflow-x-auto rounded-[var(--napms-control-radius)] bg-[var(--napms-color-nav-bg)] p-3 text-xs text-white">{artifact.content}</pre> : null}{artifact.reason ? <div className="mt-2 text-xs text-[var(--napms-color-text-secondary)]">{artifact.reason}</div> : null}</div>)}</div> : <div className="text-sm text-[var(--napms-color-text-secondary)]">No rendered artifact is available.</div>}
            </StageCard>
            <StageCard title="Controlled operation" availability={result.operation.availability}>
              <div className="text-sm text-[var(--napms-color-text-body)]">Outcome: <span className="font-medium text-[var(--napms-color-text-primary)]">{result.operation.outcome ?? "No operation evidence"}</span></div>
              {result.operation.operationId ? <div className="mt-2 font-mono text-xs text-[var(--napms-color-text-body)]">{result.operation.operationId}</div> : null}
              {result.operation.provenanceReferences.length ? <div className="mt-3 text-xs text-[var(--napms-color-text-secondary)]">Provenance: {result.operation.provenanceReferences.join(", ")}</div> : null}
              {result.operation.reason ? <div className="mt-3 text-xs text-[var(--napms-color-text-secondary)]">{result.operation.reason}</div> : null}
            </StageCard>
          </div>
        </div>
      ) : null}
    </PageWorkspace>
  )
}
