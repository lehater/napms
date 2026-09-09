import { Button } from "@/components/ui/Button"

export type PlannedFeature = {
  slug: string
  increment: string
  title: string
  eyebrow: string
  purpose: string
  columns: string[]
  sections: Array<{ title: string; description: string }>
  actions: string[]
  guardrail: string
}

export const plannedFeatures: PlannedFeature[] = [
  {
    slug: "connectivity-decisions",
    increment: "I16",
    title: "Connectivity Decisions",
    eyebrow: "Connectivity Governance",
    purpose:
      "Inspect and record durable final connectivity decisions for an exact subject and governance scope.",
    columns: ["Subject", "Scope", "Outcome", "Validity", "Reason", "Decided by", "Decision ID"],
    sections: [
      {
        title: "Decision details",
        description:
          "Exact Source → Destination → DCS subject, final outcome, validity, reason and immutable identity.",
      },
      {
        title: "Provenance",
        description:
          "Deciding principal, decision time, authority reference, evidence references and supersession relationship.",
      },
    ],
    actions: ["Record final decision", "Open decision"],
    guardrail:
      "No Pending / Approved / Rejected lifecycle or approval queue is part of the accepted model.",
  },
  {
    slug: "technical-evidence",
    increment: "I17",
    title: "Technical Access Evidence",
    eyebrow: "Technical Access",
    purpose:
      "Inspect source-qualified technical access evidence without treating evidence as authorization.",
    columns: ["Evidence", "Kind", "Technical predicate", "Source", "Observed at", "Provenance"],
    sections: [
      {
        title: "Evidence details",
        description:
          "Normalized technical predicate, source-qualified identity and accepted evidence classification.",
      },
      {
        title: "Freshness and provenance",
        description:
          "Source, observation/import time and future accepted freshness/coverage metadata.",
      },
    ],
    actions: ["Open evidence", "Ingest evidence"],
    guardrail:
      "Evidence remains evidence; this surface must not imply that configured or observed access is Allowed.",
  },
  {
    slug: "access-resolution",
    increment: "I18",
    title: "Technical-to-Domain Resolution",
    eyebrow: "Technical Access",
    purpose:
      "Explain how normalized technical access maps to domain interactions while preserving unresolved technical remainder.",
    columns: ["Technical predicate", "Domain interaction", "Resolution", "Effective time", "Provenance"],
    sections: [
      {
        title: "Resolution input",
        description:
          "Technical evidence/predicate context plus the relevant Resource and Application Communication catalogue context.",
      },
      {
        title: "Resolution explanation",
        description:
          "Domain mapping result and unresolved/ambiguous remainder using only statuses accepted by I18.",
      },
    ],
    actions: ["Resolve predicate", "Open explanation"],
    guardrail:
      "The exact resolution algebra remains owned by I18 and is not invented by this preview.",
  },
  {
    slug: "enforcement-placement",
    increment: "I19",
    title: "Network Enforcement Placement",
    eyebrow: "Enforcement",
    purpose:
      "Explain where domain traffic is subject to enforcement without conflating Logical Firewall identity with vendor/device identity.",
    columns: ["Domain traffic", "Path context", "Logical Firewall", "Attachment", "Effective time", "Provenance"],
    sections: [
      {
        title: "Traffic and path context",
        description:
          "Domain traffic context and the normalized forwarding/path knowledge used by placement semantics.",
      },
      {
        title: "Placement result",
        description:
          "Logical Firewall, enforcement selection/attachment and explanation of the derived placement.",
      },
    ],
    actions: ["Evaluate placement", "Open placement"],
    guardrail:
      "Vendor/device configuration belongs downstream; Logical Firewall remains a distinct domain concept.",
  },
  {
    slug: "reconciliation",
    increment: "I20",
    title: "Desired vs Configured Reconciliation",
    eyebrow: "Enforcement",
    purpose:
      "Compare desired Access Policy realization with technical evidence and explain the remaining semantic delta.",
    columns: ["Desired interaction", "Configured evidence", "Reconciliation", "Placement", "As of", "Provenance"],
    sections: [
      {
        title: "Desired policy",
        description:
          "The business-correct desired enforcement intent derived from Access Policy and accepted placement semantics.",
      },
      {
        title: "Configured evidence",
        description:
          "Observed/configured technical evidence considered for the same comparison context.",
      },
      {
        title: "Semantic delta",
        description:
          "The future reconciliation conclusion; exact add/remove/replace/no-op algebra is not assumed before I20.",
      },
    ],
    actions: ["Run reconciliation", "Open explanation"],
    guardrail:
      "Preview does not invent delta classifications before I20 accepts the exact semantics.",
  },
  {
    slug: "configuration-rendering",
    increment: "I21",
    title: "Configuration Rendering",
    eyebrow: "Enforcement",
    purpose:
      "Translate accepted vendor-neutral enforcement intent into target-specific configuration representation.",
    columns: ["Intent", "Target", "Renderer", "Artifact", "Equivalence", "Provenance"],
    sections: [
      {
        title: "Rendering context",
        description:
          "Accepted vendor-neutral enforcement intent and selected concrete target/renderer.",
      },
      {
        title: "Rendered artifact",
        description:
          "Target-specific representation with provenance and semantics-equivalence evidence.",
      },
    ],
    actions: ["Render configuration", "Open artifact"],
    guardrail:
      "Rendering must not broaden or narrow desired traffic and does not itself apply configuration.",
  },
  {
    slug: "network-operations",
    increment: "I22",
    title: "Network Environment Operations",
    eyebrow: "Network Operations",
    purpose:
      "Operate one supported enforcement target through current-state acquisition, pre-check, apply and post-check.",
    columns: ["Target", "Operation", "State", "Started", "Result", "Audit"],
    sections: [
      {
        title: "Execution preparation",
        description:
          "Target/current-state context, accepted pre-checks and rendered change input.",
      },
      {
        title: "Execution and verification",
        description:
          "Apply/post-check structure plus explicit result/audit, retry and recovery semantics once I22 defines them.",
      },
    ],
    actions: ["Pre-check", "Apply change", "Post-check"],
    guardrail:
      "No fake successful execution, rollback promise or retry semantics are shown before I22 implements them.",
  },
  {
    slug: "explainability-audit",
    increment: "I25",
    title: "Explainability & Audit",
    eyebrow: "Product Operations",
    purpose:
      "Navigate end-to-end provenance and operator explanations across the completed product chain.",
    columns: ["Time", "Object", "Domain", "Event / explanation", "Actor / source", "Correlation"],
    sections: [
      {
        title: "Global explanation",
        description:
          "Cross-domain navigation from Requirement through Decision, Rule, realization, execution and evidence.",
      },
      {
        title: "Operator search",
        description:
          "Mature bounded search/filtering and future bulk/operator tools only where accepted by I25.",
      },
    ],
    actions: ["Search provenance", "Open correlation"],
    guardrail:
      "Dashboard metrics and bulk operations remain undefined until concrete read models and operator use cases exist.",
  },
]

export function plannedFeatureBySlug(slug: string) {
  return plannedFeatures.find((feature) => feature.slug === slug) ?? null
}

export function PlannedFeaturePage({ feature }: { feature: PlannedFeature }) {
  return (
    <div className="mx-auto max-w-[1380px]">
      <header className="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#5F6B7D]">
            {feature.eyebrow}
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-[28px] font-bold tracking-tight text-[#172033]">
              {feature.title}
            </h1>
            <span className="inline-flex rounded-full border border-blue-200 bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-800">
              Preview · Planned {feature.increment}
            </span>
          </div>
          <p className="mt-2 max-w-4xl text-sm text-[#5F6B7D]">
            {feature.purpose}
          </p>
        </div>
      </header>

      <div
        role="note"
        className="mb-5 rounded-md border border-blue-200 bg-blue-50 p-4 text-sm text-blue-950"
      >
        <div className="font-semibold">Structural product preview</div>
        <p className="mt-1 max-w-5xl">
          This page is intentionally visible before the capability is executable.
          Layout and navigation are reviewable now; runtime data, authority and
          mutations are not implemented yet.
        </p>
      </div>

      <section className="overflow-hidden rounded-lg border border-[#E2E8F0] bg-white">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#E2E8F0] px-5 py-4">
          <div>
            <h2 className="text-base font-semibold text-[#172033]">
              Planned operational list
            </h2>
            <p className="mt-1 text-xs text-[#5F6B7D]">
              Columns shown only where the roadmap already establishes the concept.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {feature.actions.map((action) => (
              <Button
                key={action}
                variant="secondary"
                disabled
                title={`Planned in ${feature.increment}; not implemented`}
              >
                {action}
              </Button>
            ))}
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] text-left text-sm">
            <thead className="bg-[#F8FAFC] text-xs uppercase tracking-wide text-[#5F6B7D]">
              <tr>
                {feature.columns.map((column) => (
                  <th key={column} className="px-4 py-3 font-semibold">
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr className="border-t border-[#E2E8F0]">
                <td
                  colSpan={feature.columns.length}
                  className="px-4 py-8 text-center text-sm text-[#5F6B7D]"
                >
                  No runtime data — preview structure only.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <div className="mt-5 grid gap-5 xl:grid-cols-2">
        {feature.sections.map((section) => (
          <section
            key={section.title}
            className="rounded-lg border border-[#E2E8F0] bg-white p-5"
          >
            <h2 className="text-base font-semibold text-[#172033]">
              {section.title}
            </h2>
            <p className="mt-2 text-sm leading-6 text-[#5F6B7D]">
              {section.description}
            </p>
            <div className="mt-4 rounded-md border border-dashed border-[#CBD5E1] bg-[#F8FAFC] p-5 text-sm text-[#5F6B7D]">
              Planned content region · {feature.increment}
            </div>
          </section>
        ))}
      </div>

      <section className="mt-5 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950">
        <div className="font-semibold">Preview guardrail</div>
        <p className="mt-1">{feature.guardrail}</p>
      </section>
    </div>
  )
}
