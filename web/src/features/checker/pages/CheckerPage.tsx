import { useState } from "react"

import { Button } from "@/design-system/components/Button"
import { Field, Input, Select } from "@/design-system/components/Field"
import { getTrafficAnalysis } from "@/features/checker/api"
import { CheckerResultView, type CheckerResultTab } from "@/features/checker/components/CheckerResult"
import {
  initialCheckerQuery,
  type CheckerQuery,
  type CheckerResult,
} from "@/features/checker/model"

export function CheckerPage() {
  const [form, setForm] = useState<CheckerQuery>(initialCheckerQuery)
  const [result, setResult] = useState<CheckerResult | null>(null)
  const [tab, setTab] = useState<CheckerResultTab>("overview")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const update = (key: keyof CheckerQuery, value: string) =>
    setForm((current) => ({ ...current, [key]: value }))

  return (
    <section className="mx-auto grid max-w-[1500px] gap-5">
      <header>
        <div className="text-xs font-semibold uppercase tracking-[0.14em] text-[#64748B]">Technical lookup</div>
        <h1 className="mt-1 text-2xl font-bold text-[#172033]">Checker</h1>
        <p className="mt-1 max-w-4xl text-sm text-[#64748B]">Technical-to-domain analysis using stored evidence. Network Context returns an unordered candidate set, not a proven path.</p>
      </header>

      <form
        className="grid gap-4 rounded-lg border border-[#E2E8F0] bg-white p-5 lg:grid-cols-[1fr_1fr_150px_150px_250px_auto] lg:items-end"
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

      {error ? <div className="rounded-md border border-[#F2B8B5] bg-[#FFF5F5] px-4 py-3 text-sm text-[#9B1C1C]">{error}</div> : null}
      {!result ? <div className="rounded-lg border border-dashed border-[#CBD5E1] bg-white p-10 text-center text-sm text-[#64748B]">Run analysis to resolve the traffic tuple against current NAPMS data.</div> : <CheckerResultView result={result} tab={tab} onTab={setTab} />}
    </section>
  )
}

function toLocalInput(value: string) {
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return ""
  const offset = parsed.getTimezoneOffset() * 60_000
  return new Date(parsed.getTime() - offset).toISOString().slice(0, 16)
}
