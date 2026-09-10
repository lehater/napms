import { useState } from "react"

import { Button } from "@/components/ui/Button"
import { Field, Select } from "@/components/ui/Field"
import { getTrafficAnalysis } from "@/features/checker/api"
import {
  initialCheckerQuery,
  type CheckerQuery,
  type CheckerResult,
  type NetworkCandidate,
  type ResourceSide,
} from "@/features/checker/model"

const inputClass =
  "min-h-10 w-full rounded-md border border-[#CBD5E1] bg-white px-3 py-2 text-sm text-[#172033]"
type Tab = "overview" | "network" | "policy" | "ownership" | "evidence"

export function CheckerPage() {
  const [form, setForm] = useState<CheckerQuery>(initialCheckerQuery)
  const [result, setResult] = useState<CheckerResult | null>(null)
  const [tab, setTab] = useState<Tab>("overview")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const update = (key: keyof CheckerQuery, value: string) =>
    setForm((current) => ({ ...current, [key]: value }))

  return (
    <section className="mx-auto grid max-w-[1500px] gap-5">
      <header>
        <div className="text-xs font-semibold uppercase tracking-[0.14em] text-[#64748B]">Technical lookup</div>
        <h1 className="mt-1 text-2xl font-bold text-[#172033]">Checker</h1>
        <p className="mt-1 max-w-4xl text-sm text-[#64748B]">
          Technical-to-domain analysis using stored evidence. Network Context returns an unordered candidate set, not a proven path.
        </p>
      </header>

      <form
        className="grid gap-4 rounded-lg border border-[#E2E8F0] bg-white p-5 lg:grid-cols-[1fr_1fr_150px_150px_250px_auto] lg:items-end"
        onSubmit={(event) => {
          event.preventDefault()
          setLoading(true)
          setError(null)
          void getTrafficAnalysis(form)
            .then((value) => {
              setResult(value)
              setTab("overview")
            })
            .catch((reason: unknown) =>
              setError(reason instanceof Error ? reason.message : "Traffic analysis failed."),
            )
            .finally(() => setLoading(false))
        }}
      >
        <Field label="Source address"><input className={inputClass} value={form.sourceAddress} onChange={(e) => update("sourceAddress", e.target.value)} required /></Field>
        <Field label="Destination address"><input className={inputClass} value={form.destinationAddress} onChange={(e) => update("destinationAddress", e.target.value)} required /></Field>
        <Field label="Protocol"><Select value={form.protocol} onChange={(e) => update("protocol", e.target.value)}><option>TCP</option><option>UDP</option><option>ICMP</option></Select></Field>
        <Field label="Port / range"><input className={inputClass} value={form.port} onChange={(e) => update("port", e.target.value)} required /></Field>
        <Field label="As of" hint="Explicit logical time"><input className={inputClass} type="datetime-local" value={toLocalInput(form.asOf)} onChange={(e) => e.target.value && update("asOf", new Date(e.target.value).toISOString())} required /></Field>
        <Button type="submit" loading={loading}>Analyze</Button>
      </form>

      {error ? <div className="rounded-md border border-[#F2B8B5] bg-[#FFF5F5] px-4 py-3 text-sm text-[#9B1C1C]">{error}</div> : null}
      {!result ? (
        <div className="rounded-lg border border-dashed border-[#CBD5E1] bg-white p-10 text-center text-sm text-[#64748B]">Run analysis to resolve the traffic tuple against current NAPMS data.</div>
      ) : <Result result={result} tab={tab} onTab={setTab} />}
    </section>
  )
}

function Result({ result, tab, onTab }: { result: CheckerResult; tab: Tab; onTab: (tab: Tab) => void }) {
  return <div className="grid gap-4">
    <Panel title={`${result.query.sourceAddress} → ${result.query.destinationAddress} · ${result.query.protocol}/${result.query.port}`}>
      <div className="mb-4 text-xs text-[#64748B]">As of {formatTime(result.query.asOf)}</div>
      <div className="flex flex-wrap gap-2">
        <Fact label="Source" value={result.source.state} /><Fact label="Destination" value={result.destination.state} />
        <Fact label="Required" value={result.policy.requirement} /><Fact label="Decision" value={result.policy.decision} />
        <Fact label="Rule" value={result.policy.rule} /><Fact label="Relevant devices" value={String(result.networkContext.candidates.length)} />
      </div>
    </Panel>
    <div className="overflow-x-auto rounded-lg border border-[#E2E8F0] bg-white px-2 pt-2"><div className="flex min-w-max gap-1">
      {([ ["overview","Overview"], ["network","Network Context"], ["policy","Policy"], ["ownership","Ownership"], ["evidence","Evidence"] ] as const).map(([key,label]) =>
        <button key={key} type="button" onClick={() => onTab(key)} className={tab === key ? "border-b-2 border-[#2563EB] px-4 py-3 text-sm font-semibold text-[#172033]" : "px-4 py-3 text-sm font-medium text-[#64748B]"}>{label}</button>)}
    </div></div>
    {tab === "overview" ? <Overview result={result} /> : null}
    {tab === "network" ? <Network result={result} /> : null}
    {tab === "policy" ? <Policy result={result} /> : null}
    {tab === "ownership" ? <Ownership result={result} /> : null}
    {tab === "evidence" ? <Evidence result={result} /> : null}
  </div>
}

function Overview({ result }: { result: CheckerResult }) {
  return <div className="grid gap-4 lg:grid-cols-2">
    <Panel title="Resolved connectivity"><Rows values={[
      ["Source", result.connectivity.sourceComponent ?? "Unknown"], ["Destination", result.connectivity.destinationComponent ?? "Unknown"],
      ["Interaction", result.connectivity.dcs ?? "Unknown"], ["Access", result.connectivity.access ?? "Unknown"],
    ]} /></Panel>
    <Panel title="Policy"><Rows values={[["Requirement",result.policy.requirement],["Decision",result.policy.decision],["Access Rule",result.policy.rule],["Effective",result.policy.effective]]} /></Panel>
    <Panel title="Source ownership"><Side side={result.source} /></Panel>
    <Panel title="Destination ownership"><Side side={result.destination} /></Panel>
    <div className="lg:col-span-2"><Panel title="Findings">{result.findings.length ? <ul className="list-disc space-y-2 pl-5 text-sm text-[#475569]">{result.findings.map((x) => <li key={x}>{x}</li>)}</ul> : <p className="text-sm text-[#64748B]">No findings.</p>}</Panel></div>
  </div>
}

function Network({ result }: { result: CheckerResult }) {
  return <div className="grid gap-4">
    <div className="rounded-md border border-[#F1D59A] bg-[#FFF9EB] px-4 py-3 text-sm text-[#74520A]">Unordered relevant-device candidates. Membership does not prove traversal. Candidate enumeration complete: {result.networkContext.completeForPair ? "yes" : "no"}.</div>
    {result.networkContext.knowledgeGaps.map((x) => <div key={x} className="text-sm text-[#64748B]">Knowledge gap: {x}</div>)}
    {result.networkContext.candidates.map((item) => <Candidate key={item.deviceReference} item={item} />)}
    {!result.networkContext.candidates.length ? <Panel title="Relevant devices"><p className="text-sm text-[#64748B]">No candidates available. This is not proof of no forwarding or no enforcement.</p></Panel> : null}
  </div>
}

function Candidate({ item }: { item: NetworkCandidate }) {
  return <details open className="rounded-lg border border-[#E2E8F0] bg-white"><summary className="cursor-pointer list-none p-5"><div className="flex justify-between gap-3"><div><div className="font-semibold text-[#172033]">{item.deviceReference}</div><div className="text-xs text-[#64748B]">{item.logicalFirewallReference ?? "Logical firewall unknown"}</div></div><span className="h-fit rounded-full bg-[#EEF2F7] px-2.5 py-1 text-xs font-semibold text-[#475569]">Relevance: {item.relevance ?? "Unknown"}</span></div></summary>
    <div className="border-t border-[#E2E8F0] p-5"><Rows values={[["Attachment",item.attachmentReference ?? "Unknown"],["Provenance",item.provenanceReferences.join(", ")]]} />
      <div className="mt-5 text-sm font-semibold text-[#172033]">Last-known configured evidence</div>
      {!item.snapshot ? <p className="mt-2 text-sm text-[#9A3412]">No applicable stored snapshot.</p> : <div className="mt-2 grid gap-3"><div className="grid gap-2 text-xs text-[#64748B] md:grid-cols-3"><div>Snapshot: {item.snapshot.reference}</div><div>Captured: {formatTime(item.snapshot.capturedAt)}</div><div>Recorded: {formatTime(item.snapshot.recordedAt)}</div></div>{item.snapshot.entries.map((entry) => <div key={entry.reference} className="rounded-md border border-[#E2E8F0] bg-[#F8FAFC] p-3"><div className="flex justify-between gap-2 text-sm"><span className="font-semibold">{entry.reference}</span><span>{entry.action} · {entry.match}</span></div><div className="mt-2 font-mono text-xs text-[#475569]">{entry.normalized}</div></div>)}</div>}
    </div></details>
}

function Policy({ result }: { result: CheckerResult }) { return <Panel title="Policy and governance"><Rows values={[["Requirement",result.policy.requirement],["Decision",result.policy.decision],["Access Rule",result.policy.rule],["Effective Policy",result.policy.effective]]} /><p className="mt-5 text-xs text-[#64748B]">Requirement, decision, desired policy and configured technical evidence remain separate facts.</p></Panel> }

function Ownership({ result }: { result: CheckerResult }) { return <div className="grid gap-4 lg:grid-cols-2"><Panel title="Source resource"><Side side={result.source} detailed /></Panel><Panel title="Destination resource"><Side side={result.destination} detailed /></Panel></div> }

function Side({ side, detailed = false }: { side: ResourceSide; detailed?: boolean }) {
  return <div className="grid gap-3"><Rows values={[["Resource",side.resourceReference ?? side.state],["Component",side.componentName ?? "Unknown"],["Scope",side.responsibilityScope ?? "Unknown"]]} />
    {detailed ? <div className="grid gap-2">{side.responsibilities.length ? side.responsibilities.map((x) => <div key={`${x.role}-${x.party}`} className="rounded-md bg-[#F8FAFC] p-3 text-sm"><div className="font-semibold">{x.role}</div><div>{x.party}</div>{x.contact ? <div className="text-xs text-[#64748B]">{x.contact}</div> : null}</div>) : <p className="text-sm text-[#64748B]">Ownership/contact information unavailable.</p>}<p className="text-xs text-[#64748B]">Operational responsibility is not NAPMS action authority.</p></div> : null}
  </div>
}

function Evidence({ result }: { result: CheckerResult }) {
  return <div className="grid gap-4"><div className="rounded-md border border-[#D8E2F0] bg-[#F8FAFC] px-4 py-3 text-sm text-[#475569]">Configured rules are stored Technical Access Evidence snapshots. Checker does not query firewalls live or claim the snapshot is current device state.</div>{result.networkContext.candidates.map((x) => x.snapshot ? <Panel key={x.deviceReference} title={x.deviceReference}><Rows values={[["Snapshot",x.snapshot.reference],["Source",x.snapshot.source],["Captured",formatTime(x.snapshot.capturedAt)],["Recorded",formatTime(x.snapshot.recordedAt)],["Matching entries",String(x.snapshot.entries.length)]]} /></Panel> : null)}</div>
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) { return <section className="rounded-lg border border-[#E2E8F0] bg-white p-5"><h2 className="mb-4 text-base font-semibold text-[#172033]">{title}</h2>{children}</section> }
function Fact({ label, value }: { label: string; value: string }) { return <div className="rounded-md bg-[#F8FAFC] px-3 py-2"><div className="text-[11px] font-semibold uppercase tracking-wide text-[#64748B]">{label}</div><div className="text-sm font-semibold text-[#172033]">{value}</div></div> }
function Rows({ values }: { values: Array<[string,string]> }) { return <dl className="grid gap-2 text-sm">{values.map(([label,value]) => <div key={label} className="grid grid-cols-[140px_1fr] gap-3"><dt className="text-[#64748B]">{label}</dt><dd className="break-words font-medium text-[#172033]">{value}</dd></div>)}</dl> }
function formatTime(value: string | null | undefined) { if (!value) return "Unknown"; const parsed = new Date(value); return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString() }
function toLocalInput(value: string) { const parsed = new Date(value); if (Number.isNaN(parsed.getTime())) return ""; const offset = parsed.getTimezoneOffset() * 60_000; return new Date(parsed.getTime() - offset).toISOString().slice(0,16) }
