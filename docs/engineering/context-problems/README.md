# Bounded-context problem registers

## Purpose

This directory stores durable context-local registers of unresolved problems discovered during domain/architecture review.

A problem register answers:

> What remains unresolved in this bounded context, what is already fixed, what depends on what, and what blocks implementation?

It deliberately does **not** answer:

> In what total order will we execute all of this work?

Current execution is owned by `docs/plans/active/`. Optional evidence-backed sequencing belongs in a roadmap only when preserving that order has real value.

Lifecycle rules: `docs/process/plan-lifecycle.md`.

## Placement rule

Use:

```text
docs/domain/<context>/...
    = semantic/domain truth

docs/requirements/... + docs/architecture/... + docs/decisions/...
    = accepted behavior and structural decisions

docs/engineering/context-problems/<context>.md
    = unresolved problems, gaps, questions, dependencies and blockers

docs/engineering/roadmaps/<context>.md
    = optional ordered future work only when sequencing is justified

docs/plans/active/PLAN-*.md
    = only selected current execution
```

## Minimum context-problem contract

A useful register should make these items easy to identify:

- bounded context;
- canonical semantic sources;
- accepted/fixed starting constraints that materially bound the open work;
- open problems/questions/decisions;
- known target-versus-current gaps where already established;
- causal dependencies between problems when known;
- implementation blockers/gates;
- evidence still needed;
- revisit triggers;
- closed/resolved items only when keeping a short closure note prevents rediscovery.

Do not copy large canonical specifications into the register. Link to their owners and retain only enough context to explain why an item remains open.

Do not assign an execution order merely because items have identifiers. IDs are stable references, not priority or sequence.

When a problem is resolved:
1. update the highest canonical owner first;
2. remove or mark the register item resolved with a concise pointer to the canonical decision;
3. update related dependencies/blockers;
4. do not leave obsolete alternatives as living guidance.

## Roadmap admission

A problem register is the default durable parking artifact.

Create a roadmap only when ordering is itself useful current engineering truth, such as a required migration sequence, hard dependency chain or staged rollout/rollback plan. A roadmap that loses its justification should be removed/superseded, with still-open content retained here as unordered problems and real dependencies.

## Registry

| Bounded context | Problem register | Known implementation gate |
| --- | --- | --- |
| Access Policy Realization | `access-policy-realization.md` | closed while blocking target-design problems remain unresolved |

Add another row only after concrete unresolved context work has been identified. Do not create empty placeholders for every bounded context.

## Relationship to project-wide planning

A project-wide planning pass should consume these registers to compare value, risk, dependencies and MVP criticality across contexts.

That project-level planning may choose an execution order without rewriting the context registers into mini-roadmaps. Once a concrete increment is selected, create/update an active `PLAN-*.md` for that work.
