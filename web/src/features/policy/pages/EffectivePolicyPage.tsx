import { useState } from "react"

import { EmptyState, ErrorState } from "@/design-system/components/PageState"
import { PageHeader } from "@/design-system/layout/PageHeader"
import { PageWorkspace } from "@/design-system/layout/PageWorkspace"
import { Surface } from "@/design-system/primitives/Surface"
import { getEffectiveDesiredPolicy, type EffectivePolicyResponse } from "@/features/policy/api"
import { EffectivePolicyTable } from "@/features/policy/components/EffectivePolicyTable"
import { PolicyViewControls } from "@/features/policy/components/PolicyViewControls"
import { ApiError } from "@/lib/api"

export function EffectivePolicyPage({ onOpenRule }: { onOpenRule: (ruleId: string) => void }) {
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
      setError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Effective policy could not be loaded."))
    } finally {
      setRunning(false)
    }
  }

  return (
    <PageWorkspace>
      <PageHeader title="Effective Desired Policy" description="Authoritative Rules that contribute desired effect for one governance scope at one explicit instant." />
      <PolicyViewControls onRun={run} running={running} />
      {error ? <ErrorState message={`${error.code}: ${error.message}${error.correlationId ? ` · Correlation: ${error.correlationId}` : ""}`} /> : null}
      {result ? (
        <Surface className="min-w-0 overflow-hidden">
          <div className="border-b border-[var(--napms-color-border)] px-5 py-4">
            <div className="font-semibold text-[var(--napms-color-text-primary)]">{result.scope}</div>
            <div className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">asOf {result.asOf} · authority {result.authorityReference}</div>
          </div>
          {result.rules.length === 0 ? <EmptyState title="Authorized selection is empty at this instant" /> : <EffectivePolicyTable rules={result.rules} onOpenRule={onOpenRule} />}
        </Surface>
      ) : null}
    </PageWorkspace>
  )
}
