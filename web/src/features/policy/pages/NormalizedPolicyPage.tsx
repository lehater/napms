import { useState } from "react"

import { EmptyState, ErrorState } from "@/design-system/components/PageState"
import { PageHeader } from "@/design-system/layout/PageHeader"
import { PageWorkspace } from "@/design-system/layout/PageWorkspace"
import { Surface } from "@/design-system/primitives/Surface"
import { getNormalizedPolicy, type NormalizedPolicyResponse } from "@/features/policy/api"
import { NormalizedPolicyTable } from "@/features/policy/components/NormalizedPolicyTable"
import { PolicyViewControls } from "@/features/policy/components/PolicyViewControls"
import { ApiError } from "@/lib/api"

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
      setError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Normalized policy could not be loaded."))
    } finally {
      setRunning(false)
    }
  }

  return (
    <PageWorkspace>
      <PageHeader title="Normalized Policy" description="Vendor-neutral effective policy projection with Rule, Authority, ACC and RC provenance preserved." />
      <PolicyViewControls onRun={run} running={running} />
      {error ? <ErrorState message={`${error.code}: ${error.message}${error.correlationId ? ` · Correlation: ${error.correlationId}` : ""}`} /> : null}
      {result ? (
        <Surface className="min-w-0 overflow-hidden">
          <div className="border-b border-[var(--napms-color-border)] px-5 py-4">
            <div className="font-semibold text-[var(--napms-color-text-primary)]">{result.scope}</div>
            <div className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">asOf {result.asOf} · authority {result.authorityReference} · {result.rows.length} row(s)</div>
          </div>
          {result.rows.length === 0 ? <EmptyState title="Authorized normalized policy is empty at this instant" /> : <NormalizedPolicyTable rows={result.rows} />}
        </Surface>
      ) : null}
    </PageWorkspace>
  )
}
