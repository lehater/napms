# Bounded-context roadmaps

## Purpose

This directory stores durable, context-local roadmaps for bounded contexts whose unresolved future design, migration or implementation work is useful to preserve across workstream switches.

A context roadmap answers:

> When we return to this bounded context, what ordered work remains and where do we resume?

It is not the current execution pointer and it is not a source of domain semantics.

Canonical lifecycle rules are defined in `docs/process/plan-lifecycle.md`.

## Placement rule

Use:

```text
docs/domain/<context>/...
    = semantic/domain truth

docs/requirements/... + docs/architecture/... + docs/decisions/...
    = accepted behavior and structural decisions

docs/engineering/roadmaps/<context>.md
    = durable ordered future work for that bounded context

docs/plans/active/PLAN-*.md
    = only the work being executed now
```

A context roadmap may remain `parked` for a long time without making the context active.

Do not keep a `PLAN-*.md` under `docs/plans/active/` only to remember parked work.

Do not create empty roadmap files for every bounded context. Add one after discovery has identified concrete unresolved work whose ordering is worth preserving.

## Minimum context-roadmap contract

A context roadmap should make these items easy to identify:

- bounded context;
- status: `active | parked | complete`;
- canonical semantic sources;
- fixed/accepted starting constraints;
- ordered stages/work packages;
- blocking dependencies/gates;
- next stage or re-entry point;
- implementation gate when implementation is not yet authorized;
- completion condition.

If later findings change domain semantics, update the canonical semantic owner first and then refresh the roadmap.

## Registry

| Bounded context | Roadmap | State | Resume point | Implementation gate |
| --- | --- | --- | --- | --- |
| Access Policy Realization | `access-policy-realization.md` | parked | D1 — cross-context input/output contracts | closed until D1-D7 are accepted and D8 opens implementation |

Other bounded contexts are added here only when their own concrete roadmap has been produced.

## Relationship to project-wide planning

A future project-wide roadmap may use these context roadmaps as planning inputs to decide cross-context priority and sequencing.

That project-wide roadmap should reference context-local detail instead of copying it. Global prioritization does not automatically change a local roadmap from `parked` to `active`; activation occurs only when a concrete active plan is selected under `docs/plans/active/`.
