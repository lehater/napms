import { PageTab, PageTabs } from "@/design-system/layout/PageTabs"
import { Surface } from "@/design-system/primitives/Surface"
import type { CheckerResult, NetworkCandidate, ResourceSide } from "@/features/checker/model"

export type CheckerResultTab = "overview" | "network" | "policy" | "ownership" | "evidence"

export function CheckerResultView({ result, tab, onTab }: { result: CheckerResult; tab: CheckerResultTab; onTab: (tab: CheckerResultTab) => void }) {
  const firstPolicy = result.policyMatches[0]
  return (
    <div className="grid gap-4">
      <Panel title={`${result.query.sourceAddress} → ${result.query.destinationAddress} · ${result.query.protocol}/${result.query.port}`}>
        <div className="mb-4 text-xs text-[var(--napms-color-text-secondary)]">As of {formatTime(result.query.asOf)}</div>
        <div className="flex flex-wrap gap-2">
          <Fact label="Source" value={result.source.state} />
          <Fact label="Destination" value={result.destination.state} />
          <Fact label="Requirement" value={singleOrMultiple(result.policyMatches.map((item) => item.requirement))} />
          <Fact label="Decision" value={singleOrMultiple(result.policyMatches.map((item) => item.decision))} />
          <Fact label="Rule" value={singleOrMultiple(result.policyMatches.map((item) => item.rule))} />
          <Fact label="Relevant devices" value={String(result.networkContext.candidates.length)} />
          {firstPolicy?.partial ? <Fact label="Policy view" value="Partial" /> : null}
        </div>
      </Panel>
      <PageTabs>
        {([ ["overview","Overview"], ["network","Network Context"], ["policy","Policy"], ["ownership","Ownership"], ["evidence","Evidence"] ] as const).map(([key,label]) => (
          <PageTab key={key} active={tab === key} onClick={() => onTab(key)}>{label}</PageTab>
        ))}
      </PageTabs>
      {tab === "overview" ? <Overview result={result} /> : null}
      {tab === "network" ? <Network result={result} /> : null}
      {tab === "policy" ? <Policy result={result} /> : null}
      {tab === "ownership" ? <Ownership result={result} /> : null}
      {tab === "evidence" ? <Evidence result={result} /> : null}
    </div>
  )
}

function Overview({ result }: { result: CheckerResult }) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Panel title="Source resolution"><ResolutionSummary side={result.source} /></Panel>
      <Panel title="Destination resolution"><ResolutionSummary side={result.destination} /></Panel>
      <Panel title="Policy summary"><Rows values={[["Matches", String(result.policyMatches.length)],["Requirement", singleOrMultiple(result.policyMatches.map((item) => item.requirement))],["Decision", singleOrMultiple(result.policyMatches.map((item) => item.decision))],["Access Rule", singleOrMultiple(result.policyMatches.map((item) => item.rule))]]} /></Panel>
      <Panel title="Network summary"><Rows values={[["Candidates", String(result.networkContext.candidates.length)],["Enumeration complete", result.networkContext.completeForPair ? "Yes" : "No"],["With snapshots", String(result.networkContext.candidates.filter((item) => item.snapshot).length)]]} /></Panel>
      <div className="lg:col-span-2"><Panel title="Findings">{result.findings.length ? <ul className="list-disc space-y-2 pl-5 text-sm text-[var(--napms-color-text-body)]">{result.findings.map((finding) => <li key={finding}>{finding}</li>)}</ul> : <p className="text-sm text-[var(--napms-color-text-secondary)]">No findings.</p>}</Panel></div>
    </div>
  )
}

function Network({ result }: { result: CheckerResult }) {
  return (
    <div className="grid gap-4">
      <div className="rounded-[var(--napms-control-radius)] border border-[var(--napms-color-warning-dot)] bg-[var(--napms-color-warning-bg)] px-4 py-3 text-sm text-[var(--napms-color-warning)]">Unordered relevant-device candidates. Membership does not prove traversal. Candidate enumeration complete: {result.networkContext.completeForPair ? "yes" : "no"}.</div>
      {result.networkContext.knowledgeGaps.map((gap) => <div key={gap} className="text-sm text-[var(--napms-color-text-secondary)]">Knowledge gap: {gap}</div>)}
      {result.networkContext.candidates.map((item) => <Candidate key={item.deviceReference} item={item} asOf={result.query.asOf} />)}
      {!result.networkContext.candidates.length ? <Panel title="Relevant devices"><p className="text-sm text-[var(--napms-color-text-secondary)]">No candidates available. This is not proof of no forwarding or no enforcement.</p></Panel> : null}
    </div>
  )
}

function Candidate({ item, asOf }: { item: NetworkCandidate; asOf: string }) {
  return (
    <details open className="rounded-[var(--napms-surface-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)] shadow-[var(--napms-surface-shadow)]">
      <summary className="cursor-pointer list-none p-5">
        <div className="flex justify-between gap-3">
          <div><div className="font-semibold text-[var(--napms-color-text-primary)]">{item.deviceReference}</div><div className="text-xs text-[var(--napms-color-text-secondary)]">{item.logicalFirewallReference ?? "Logical firewall unknown"}</div></div>
          <span className="h-fit rounded-full bg-[var(--napms-color-surface-muted)] px-2.5 py-1 text-xs font-semibold text-[var(--napms-color-text-body)]">Relevance: {item.relevance ?? "Unknown"}</span>
        </div>
      </summary>
      <div className="border-t border-[var(--napms-color-border)] p-5">
        <Rows values={[["Attachment", item.attachmentReference ?? "Unknown"],["Provenance", item.provenanceReferences.join(", ") || "Unknown"]]} />
        <div className="mt-5 text-sm font-semibold text-[var(--napms-color-text-primary)]">Last-known configured evidence</div>
        {!item.snapshot ? <p className="mt-2 text-sm text-[var(--napms-color-warning)]">No applicable stored snapshot.</p> : (
          <div className="mt-2 grid gap-3">
            <div className="grid gap-2 text-xs text-[var(--napms-color-text-secondary)] md:grid-cols-4"><div>Snapshot: {item.snapshot.reference}</div><div>Captured: {formatTime(item.snapshot.capturedAt)}</div><div>Recorded: {formatTime(item.snapshot.recordedAt)}</div><div>Age at analysis: {snapshotAge(asOf, item.snapshot.capturedAt)}</div></div>
            {item.snapshot.entries.length ? item.snapshot.entries.map((entry) => <div key={entry.reference} className="rounded-[var(--napms-control-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface-subtle)] p-3"><div className="flex justify-between gap-2 text-sm"><span className="font-semibold">{entry.reference}</span><span>{entry.action} · {entry.match}</span></div><div className="mt-2 font-mono text-xs text-[var(--napms-color-text-body)]">{entry.normalized}</div></div>) : <p className="text-sm text-[var(--napms-color-text-secondary)]">Snapshot exists, but no technical entry matches the queried traffic.</p>}
          </div>
        )}
      </div>
    </details>
  )
}

function Policy({ result }: { result: CheckerResult }) {
  return <div className="grid gap-4">{result.policyMatches.map((item,index) => <Panel key={`${item.scope ?? "scope"}-${item.dcsReference ?? "dcs"}-${index}`} title={`Policy match ${index + 1}`}><Rows values={[["Source component", item.sourceComponent ?? "Unknown"],["Destination component", item.destinationComponent ?? "Unknown"],["DCS", item.dcsDisplayName ?? item.dcsReference ?? "Unknown"],["Access", item.accessSummary ?? "Unknown"],["Requirement", item.requirement],["Decision", item.decision],["Access Rule", item.rule],["Effective Policy", item.effective],["Scope", item.scope ?? "Unknown"],["Projection completeness", item.partial ? "Partial" : "Complete"]]} /></Panel>)}{!result.policyMatches.length ? <Panel title="Policy and governance"><p className="text-sm text-[var(--napms-color-text-secondary)]">No matching policy projection is available.</p></Panel> : null}<p className="text-xs text-[var(--napms-color-text-secondary)]">Requirement, decision, desired policy and configured technical evidence remain separate facts. Multiple semantic matches are preserved rather than collapsed.</p></div>
}

function Ownership({ result }: { result: CheckerResult }) { return <div className="grid gap-4 lg:grid-cols-2"><Panel title="Source resources"><OwnershipSide side={result.source} /></Panel><Panel title="Destination resources"><OwnershipSide side={result.destination} /></Panel></div> }
function ResolutionSummary({ side }: { side: ResourceSide }) { return <div className="grid gap-3"><Rows values={[["State", side.state],["Candidates", String(side.candidates.length)]]} />{side.candidates.map((candidate) => <div key={`${candidate.resourceReference}-${candidate.endpointReference}`} className="rounded-[var(--napms-control-radius)] bg-[var(--napms-color-surface-subtle)] p-3 text-sm"><div className="font-semibold text-[var(--napms-color-text-primary)]">{candidate.resourceReference}</div><div className="mt-1 text-[var(--napms-color-text-body)]">{candidate.componentNames.join(", ") || "Component unknown"}</div><div className="text-xs text-[var(--napms-color-text-secondary)]">Endpoint: {candidate.endpointReference}</div></div>)}</div> }
function OwnershipSide({ side }: { side: ResourceSide }) { if (!side.candidates.length) return <p className="text-sm text-[var(--napms-color-text-secondary)]">No resolved Resource candidate.</p>; return <div className="grid gap-4">{side.candidates.map((candidate) => { const assignments = side.responsibilities.filter((item) => item.resourceReference === candidate.resourceReference); return <section key={`${candidate.resourceReference}-${candidate.endpointReference}`} className="rounded-[var(--napms-control-radius)] border border-[var(--napms-color-border)] p-4"><div className="font-semibold text-[var(--napms-color-text-primary)]">{candidate.resourceReference}</div><div className="mt-1 text-sm text-[var(--napms-color-text-body)]">{candidate.componentNames.join(", ") || "Component unknown"}</div><div className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">Endpoint {candidate.endpointReference}</div><div className="mt-3 grid gap-2">{assignments.length ? assignments.map((item) => <div key={`${item.role}-${item.party}`} className="rounded-[var(--napms-control-radius)] bg-[var(--napms-color-surface-subtle)] p-3 text-sm"><div className="font-semibold">{item.role}</div><div>{item.party}</div>{item.contact ? <div className="text-xs text-[var(--napms-color-text-secondary)]">{item.contact}</div> : null}</div>) : <p className="text-sm text-[var(--napms-color-text-secondary)]">Ownership/contact information unavailable.</p>}</div></section> })}<p className="text-xs text-[var(--napms-color-text-secondary)]">Operational Resource Responsibility is not NAPMS action authority.</p></div> }
function Evidence({ result }: { result: CheckerResult }) { return <div className="grid gap-4"><div className="rounded-[var(--napms-control-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface-subtle)] px-4 py-3 text-sm text-[var(--napms-color-text-body)]">Configured rules are stored Technical Access Evidence snapshots. Checker does not query firewalls live or claim the snapshot is current device state.</div>{result.networkContext.candidates.map((item) => item.snapshot ? <Panel key={item.deviceReference} title={item.deviceReference}><Rows values={[["Snapshot", item.snapshot.reference],["Source", item.snapshot.source],["Captured", formatTime(item.snapshot.capturedAt)],["Recorded", formatTime(item.snapshot.recordedAt)],["Age at analysis", snapshotAge(result.query.asOf, item.snapshot.capturedAt)],["Matching entries", String(item.snapshot.entries.length)]]} /></Panel> : null)}</div> }
function Panel({ title, children }: { title: string; children: React.ReactNode }) { return <Surface className="p-5"><h2 className="mb-4 text-base font-semibold text-[var(--napms-color-text-primary)]">{title}</h2>{children}</Surface> }
function Fact({ label, value }: { label: string; value: string }) { return <div className="rounded-[var(--napms-control-radius)] bg-[var(--napms-color-surface-subtle)] px-3 py-2"><div className="text-[var(--napms-font-size-caption)] font-semibold uppercase tracking-wide text-[var(--napms-color-text-secondary)]">{label}</div><div className="text-sm font-semibold text-[var(--napms-color-text-primary)]">{value}</div></div> }
function Rows({ values }: { values: Array<[string,string]> }) { return <dl className="grid gap-2 text-sm">{values.map(([label,value]) => <div key={label} className="grid grid-cols-[150px_1fr] gap-3"><dt className="text-[var(--napms-color-text-secondary)]">{label}</dt><dd className="break-words font-medium text-[var(--napms-color-text-primary)]">{value}</dd></div>)}</dl> }
function singleOrMultiple(values: string[]) { const unique = [...new Set(values)]; if (!unique.length) return "Unknown"; if (unique.length === 1) return unique[0]; return `Multiple (${unique.join(", ")})` }
function formatTime(value: string | null | undefined) { if (!value) return "Unknown"; const parsed = new Date(value); return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString() }
function snapshotAge(asOf: string, capturedAt: string | null) { if (!capturedAt) return "Unknown"; const end = new Date(asOf).getTime(); const start = new Date(capturedAt).getTime(); if (Number.isNaN(end) || Number.isNaN(start) || end < start) return "Unknown"; const totalMinutes = Math.floor((end-start)/60000); const days = Math.floor(totalMinutes/1440); const hours = Math.floor((totalMinutes%1440)/60); const minutes = totalMinutes%60; return [days ? `${days}d` : "", hours ? `${hours}h` : "", `${minutes}m`].filter(Boolean).join(" ") }
