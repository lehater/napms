import { useState } from "react"

import { Button } from "@/components/ui/Button"
import { Field, Select } from "@/components/ui/Field"
import {
  checkerFixture,
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

  const update = (key: keyof CheckerQuery, value: string) =>
    setForm((current) => ({ ...current, [key]: value }))

  return (
    <section className="mx-auto grid max-w-[1500px] gap-5">
      <header>
        <div className="text-xs font-semibold uppercase tracking-[0.14em] text-[#64748B]">
          Technical lookup
        </div>
        <h1 className="mt-1 text-2xl font-bold text-[#172033]">Checker</h1>
        <p className="mt-1 max-w-4xl text-sm text-[#64748B]">
          Analyze one traffic tuple across domain context, policy, Network Context candidates,
          stored technical evidence and operational ownership. Network candidates are not a
          proven forwarding path.
        </p>
      </header>

      <form
        className="grid gap-4 rounded-lg border border-[#E2E8F0] bg-white p-5 lg:grid-cols-[1fr_1fr_160px_160px_260px_auto] lg:items-end"
        onSubmit={(event) => {
          event.preventDefault()
          setResult(checkerFixture(form))
          setTab("overview")
        }}
      >
        <Field label="Source address">
          <input
            className={inputClass}
            value={form.sourceAddress}
            onChange={(event) => update("sourceAddress", event.target.value)}
            required
          />
        </Field>
        <Field label="Destination address">
          <input
            className={inputClass}
            value={form.destinationAddress}
            onChange={(event) => update("destinationAddress", event.target.value)}
            required
          />
        </Field>
        <Field label="Protocol">
          <Select
            value={form.protocol}
            onChange={(event) => update("protocol", event.target.value)}
          >
            <option>TCP</option>
            <option>UDP</option>
            <option>ICMP</option>
          </Select>
        </Field>
        <Field label="Port">
          <input
            className={inputClass}
            value={form.port}
            onChange={(event) => update("port", event.target.value)}
            required
          />
        </Field>
        <Field label="As of" hint="Explicit logical time">
          <input
            className={inputClass}
            type="datetime-local"
            value={toLocalInput(form.asOf)}
            onChange={(event) => {
              const value = event.target.value
              if (value) update("asOf", new Date(value).toISOString())
            }}
            required
          />
        </Field>
        <Button type="submit">Analyze</Button>
      </form>

      {!result ? (
        <div className="rounded-lg border border-dashed border-[#CBD5E1] bg-white p-10 text-center text-sm text-[#64748B]">
          Enter a traffic tuple and run analysis. The local fixture is available for
          10.10.10.10 → 10.20.20.20 TCP/443.
        </div>
      ) : (
        <CheckerResultView result={result} tab={tab} onTab={setTab} />
      )}
    </section>
  )
}

function CheckerResultView({
  result,
  tab,
  onTab,
}: {
  result: CheckerResult
  tab: Tab
  onTab: (tab: Tab) => void
}) {
  return (
    <div className="grid gap-4">
      <div className="rounded-lg border border-[#E2E8F0] bg-white p-5">
        <div className="text-sm font-semibold text-[#172033]">
          {result.query.sourceAddress} → {result.query.destinationAddress} ·{" "}
          {result.query.protocol}/{result.query.port}
        </div>
        <div className="mt-1 text-xs text-[#64748B]">As of {formatTime(result.query.asOf)}</div>
        <div className="mt-4 flex flex-wrap gap-2">
          <Fact label="Source" value={result.source.state} />
          <Fact label="Destination" value={result.destination.state} />
          <Fact label="Required" value={result.policy.requirement} />
          <Fact label="Decision" value={result.policy.decision} />
          <Fact label="Rule" value={result.policy.rule} />
          <Fact
            label="Network candidates"
            value={String(result.networkContext.candidates.length)}
          />
        </div>
      </div>

      <div className="overflow-x-auto rounded-lg border border-[#E2E8F0] bg-white px-2 pt-2">
        <div className="flex min-w-max gap-1">
          {(
            [
              ["overview", "Overview"],
              ["network", "Network Context"],
              ["policy", "Policy"],
              ["ownership", "Ownership"],
              ["evidence", "Evidence"],
            ] as const
          ).map(([key, label]) => (
            <button
              key={key}
              type="button"
              className={
                tab === key
                  ? "border-b-2 border-[#2563EB] px-4 py-3 text-sm font-semibold text-[#172033]"
                  : "px-4 py-3 text-sm font-medium text-[#64748B] hover:text-[#172033]"
              }
              onClick={() => onTab(key)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {tab === "overview" ? <Overview result={result} /> : null}
      {tab === "network" ? <NetworkContext result={result} /> : null}
      {tab === "policy" ? <Policy result={result} /> : null}
      {tab === "ownership" ? <Ownership result={result} /> : null}
      {tab === "evidence" ? <Evidence result={result} /> : null}
    </div>
  )
}

function Overview({ result }: { result: CheckerResult }) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Panel title="Resolved connectivity">
        <dl className="grid gap-3 text-sm">
          <Row label="Source" value={result.connectivity.sourceComponent ?? "Unknown"} />
          <Row
            label="Destination"
            value={result.connectivity.destinationComponent ?? "Unknown"}
          />
          <Row label="Interaction" value={result.connectivity.dcs ?? "Unknown"} />
          <Row label="Access" value={result.connectivity.access ?? "Unknown"} />
        </dl>
      </Panel>
      <Panel title="Analysis summary">
        <dl className="grid gap-3 text-sm">
          <Row label="Requirement" value={result.policy.requirement} />
          <Row label="Decision" value={result.policy.decision} />
          <Row label="Access Rule" value={result.policy.rule} />
          <Row label="Effective" value={result.policy.effective} />
          <Row
            label="Relevant devices"
            value={String(result.networkContext.candidates.length)}
          />
        </dl>
      </Panel>
      <Panel title="Source ownership">
        <SideSummary side={result.source} />
      </Panel>
      <Panel title="Destination ownership">
        <SideSummary side={result.destination} />
      </Panel>
      <div className="lg:col-span-2">
        <Panel title="Findings">
          {result.findings.length ? (
            <ul className="list-disc space-y-2 pl-5 text-sm text-[#475569]">
              {result.findings.map((finding) => (
                <li key={finding}>{finding}</li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-[#64748B]">No findings.</p>
          )}
        </Panel>
      </div>
    </div>
  )
}

function NetworkContext({ result }: { result: CheckerResult }) {
  return (
    <div className="grid gap-4">
      <div className="rounded-md border border-[#F1D59A] bg-[#FFF9EB] px-4 py-3 text-sm text-[#74520A]">
        This is an unordered relevant-device candidate set. Membership does not prove traffic
        traversal. Candidate enumeration complete: {result.networkContext.completeForPair ? "yes" : "no"}.
      </div>
      {result.networkContext.knowledgeGaps.map((gap) => (
        <div key={gap} className="text-sm text-[#64748B]">
          Knowledge gap: {gap}
        </div>
      ))}
      {result.networkContext.candidates.map((candidate) => (
        <CandidateCard key={candidate.deviceReference} candidate={candidate} />
      ))}
      {!result.networkContext.candidates.length ? (
        <Panel title="Relevant devices">
          <p className="text-sm text-[#64748B]">
            No Network Context candidates are available. This is not proof of no forwarding or
            no enforcement.
          </p>
        </Panel>
      ) : null}
    </div>
  )
}

function CandidateCard({ candidate }: { candidate: NetworkCandidate }) {
  return (
    <details className="rounded-lg border border-[#E2E8F0] bg-white" open>
      <summary className="cursor-pointer list-none p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="font-semibold text-[#172033]">{candidate.deviceReference}</div>
            <div className="mt-1 text-xs text-[#64748B]">
              {candidate.logicalFirewallReference ?? "Logical firewall unknown"}
            </div>
          </div>
          <span className="rounded-full bg-[#EEF2F7] px-2.5 py-1 text-xs font-semibold text-[#475569]">
            Relevance: {candidate.relevance ?? "Unknown"}
          </span>
        </div>
      </summary>
      <div className="border-t border-[#E2E8F0] p-5">
        <dl className="grid gap-2 text-sm md:grid-cols-2">
          <Row label="Attachment" value={candidate.attachmentReference ?? "Unknown"} />
          <Row label="Provenance" value={candidate.provenanceReferences.join(", ")} />
        </dl>
        <div className="mt-5">
          <div className="text-sm font-semibold text-[#172033]">Last-known configured evidence</div>
          {!candidate.snapshot ? (
            <p className="mt-2 text-sm text-[#9A3412]">No applicable stored snapshot.</p>
          ) : (
            <div className="mt-2 grid gap-3">
              <div className="grid gap-2 text-xs text-[#64748B] md:grid-cols-3">
                <div>Snapshot: {candidate.snapshot.reference}</div>
                <div>Captured: {formatTime(candidate.snapshot.capturedAt)}</div>
                <div>Recorded: {formatTime(candidate.snapshot.recordedAt)}</div>
              </div>
              {candidate.snapshot.entries.map((entry) => (
                <div
                  key={`${candidate.snapshot?.reference}-${entry.reference}`}
                  className="rounded-md border border-[#E2E8F0] bg-[#F8FAFC] p-3"
                >
                  <div className="flex flex-wrap justify-between gap-2 text-sm">
                    <span className="font-semibold text-[#172033]">{entry.reference}</span>
                    <span className="text-[#475569]">{entry.action} · {entry.match}</span>
                  </div>
                  <div className="mt-2 font-mono text-xs text-[#475569]">{entry.normalized}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </details>
  )
}

function Policy({ result }: { result: CheckerResult }) {
  return (
    <Panel title="Policy and governance">
      <dl className="grid gap-3 text-sm">
        <Row label="Requirement" value={`${result.policy.requirement}${ref(result.policy.requirementReference)}`} />
        <Row label="Decision" value={`${result.policy.decision}${ref(result.policy.decisionReference)}`} />
        <Row label="Access Rule" value={`${result.policy.rule}${ref(result.policy.ruleReference)}`} />
        <Row label="Effective Policy" value={result.policy.effective} />
      </dl>
      <p className="mt-5 text-xs text-[#64748B]">
        Requirement, decision, desired Access Rule and configured technical evidence are separate
        owner facts and are not collapsed into one status.
      </p>
    </Panel>
  )
}

function Ownership({ result }: { result: CheckerResult }) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Panel title="Source resource">
        <OwnershipSide side={result.source} />
      </Panel>
      <Panel title="Destination resource">
        <OwnershipSide side={result.destination} />
      </Panel>
    </div>
  )
}

function OwnershipSide({ side }: { side: ResourceSide }) {
  return (
    <div className="grid gap-4">
      <dl className="grid gap-2 text-sm">
        <Row label="Resource" value={side.resourceReference ?? "Unknown"} />
        <Row label="Component / service" value={side.serviceName ?? side.componentName ?? "Unknown"} />
        <Row label="Responsibility scope" value={side.responsibilityScope ?? "Unknown"} />
      </dl>
      <div>
        <div className="text-xs font-semibold uppercase tracking-wide text-[#64748B]">
          Operational responsibility
        </div>
        {side.responsibilities.length ? (
          <div className="mt-2 grid gap-2">
            {side.responsibilities.map((item) => (
              <div key={`${item.role}-${item.party}`} className="rounded-md bg-[#F8FAFC] p-3 text-sm">
                <div className="font-semibold text-[#172033]">{item.role}</div>
                <div className="mt-1 text-[#475569]">{item.party}</div>
                {item.contact ? <div className="text-xs text-[#64748B]">{item.contact}</div> : null}
              </div>
            ))}
          </div>
        ) : (
          <p className="mt-2 text-sm text-[#64748B]">Ownership/contact information unavailable.</p>
        )}
      </div>
      <p className="text-xs text-[#64748B]">
        Operational responsibility is not NAPMS action authority.
      </p>
    </div>
  )
}

function Evidence({ result }: { result: CheckerResult }) {
  const candidatesWithEvidence = result.networkContext.candidates.filter((item) => item.snapshot)
  return (
    <div className="grid gap-4">
      <div className="rounded-md border border-[#D8E2F0] bg-[#F8FAFC] px-4 py-3 text-sm text-[#475569]">
        Configured rules shown here are stored Technical Access Evidence snapshots. Checker does
        not query firewalls live and does not claim the snapshot is the current device state.
      </div>
      {candidatesWithEvidence.map((candidate) => (
        <Panel key={candidate.deviceReference} title={candidate.deviceReference}>
          <dl className="grid gap-2 text-sm md:grid-cols-2">
            <Row label="Snapshot" value={candidate.snapshot?.reference ?? "Unknown"} />
            <Row label="Source" value={candidate.snapshot?.source ?? "Unknown"} />
            <Row label="Captured" value={formatTime(candidate.snapshot?.capturedAt)} />
            <Row label="Recorded" value={formatTime(candidate.snapshot?.recordedAt)} />
          </dl>
        </Panel>
      ))}
      {!candidatesWithEvidence.length ? (
        <Panel title="Technical Access Evidence">
          <p className="text-sm text-[#64748B]">No applicable configured snapshots.</p>
        </Panel>
      ) : null}
    </div>
  )
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-lg border border-[#E2E8F0] bg-white p-5">
      <h2 className="mb-4 text-base font-semibold text-[#172033]">{title}</h2>
      {children}
    </section>
  )
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md bg-[#F8FAFC] px-3 py-2">
      <div className="text-[11px] font-semibold uppercase tracking-wide text-[#64748B]">{label}</div>
      <div className="mt-0.5 text-sm font-semibold text-[#172033]">{value}</div>
    </div>
  )
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="grid grid-cols-[140px_1fr] gap-3">
      <dt className="text-[#64748B]">{label}</dt>
      <dd className="min-w-0 break-words font-medium text-[#172033]">{value}</dd>
    </div>
  )
}

function SideSummary({ side }: { side: ResourceSide }) {
  return (
    <dl className="grid gap-2 text-sm">
      <Row label="Resource" value={side.resourceReference ?? side.state} />
      <Row label="Service" value={side.serviceName ?? "Unknown"} />
      <Row
        label="Primary contact"
        value={side.responsibilities[0]?.party ?? "Unavailable"}
      />
    </dl>
  )
}

function ref(value: string | null) {
  return value ? ` · ${value}` : ""
}

function formatTime(value: string | null | undefined) {
  if (!value) return "Unknown"
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString()
}

function toLocalInput(value: string) {
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return ""
  const offset = parsed.getTimezoneOffset() * 60_000
  return new Date(parsed.getTime() - offset).toISOString().slice(0, 16)
}
