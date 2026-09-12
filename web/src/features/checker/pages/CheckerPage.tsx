import { useState } from "react"

import { Button } from "@/design-system/components/Button"
import { Field, Input, Select } from "@/design-system/components/Field"
import { EmptyState, ErrorState } from "@/design-system/components/PageState"
import { PageHeader } from "@/design-system/layout/PageHeader"
import { PageWorkspace } from "@/design-system/layout/PageWorkspace"
import { Surface } from "@/design-system/primitives/Surface"
import { getTrafficAnalysis } from "@/features/checker/api"
import { CheckerResultView, type CheckerResultTab } from "@/features/checker/components/CheckerResult"
import { initialCheckerQuery, type CheckerQuery, type CheckerResult } from "@/features/checker/model"

export function CheckerPage() {
  const [form, setForm] = useState<CheckerQuery>(initialCheckerQuery)
  const [result, setResult] = useState<CheckerResult | null>(null)
  const [tab, setTab] = useState<CheckerResultTab>("overview")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const update = (key: keyof CheckerQuery, value: string) => setForm((current) => ({ ...current, [key]: value }))

  return (
    <PageWorkspace>
      <PageHeader title="Checker" description="Technical-to-domain analysis using stored evidence. Network Context returns an unordered candidate set, not a proven path." />

      <Surface className="p-5">
        <form
          className="grid gap-4 lg:grid-cols-[1fr_1fr_150px_150px_250px_auto] lg:items-end"
          onSubmit={(event) => {
            event.preventDefault()
            setLoading(true)
            setError(null)
            void getTrafficAnalysis(form)
              .then((value) => { setResult(value); setTab("overview") })
              .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "Traffic analysis failed."))
              .finally(() => setLoading(false))
          }}
        >
          <Field label="Source address"><Input value={form.sourceAddress} onChange={(event) => update("sourceAddress", event.target.value)} required /></Field>
          <Field label="Destination address"><Input value={form.destinationAddress} onChange={(event) => update("destinationAddress", event.target.value)} required /></Field>
          <Field label="Protocol"><Select value={form.protocol} onChange={(event) => update("protocol", event.target.value)}><option>TCP</option><option>UDP</option><option>ICMP</option></Select></Field>
          <Field label="Port / range"><Input value={form.port} onChange={(event) => update("port", event.target.value)} required /></Field>
          <Field label="As of" hint="Explicit logical time"><Input type="datetime-local" value={toLocalInput(form.asOf)} onChange={(event) => event.target.value && update("asOf", new Date(event.target.value).toISOString())} required /></Field>
          <Button type="submit" loading={loading}>Analyze</Button>
        </form>
      </Surface>

      {error ? <ErrorState message={error} /> : null}
      {!result ? <EmptyState title="Run analysis" description="Resolve the traffic tuple against current NAPMS data." /> : <CheckerResultView result={result} tab={tab} onTab={setTab} />}
    </PageWorkspace>
  )
}

function toLocalInput(value: string) {
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return ""
  const offset = parsed.getTimezoneOffset() * 60_000
  return new Date(parsed.getTime() - offset).toISOString().slice(0, 16)
}
