# Documentation scope

Apply root `AGENTS.md` first.

## Canonical ownership

Project documentation is a reconstructable specification, not only a backlog or record of unfinished work.

- `requirements/` — current observable product/quality behavior, whether already implemented or still target-only.
- `domain/` — current meaning, identity, lifecycle and semantic ownership.
- `architecture/` — current as-built and target structural/runtime contracts. When they differ, label the distinction explicitly.
- `decisions/` — design decisions still required to reproduce or safely evolve the current as-built/target system.
- `engineering/` — current API, persistence, runtime, configuration, operational and implementation-facing contracts.
- `ui/` — current product-facing screen/wireframe specifications plus reusable presentation/interaction guidance.
- `plans/active/` — current execution state only.
- `process/` — reusable working protocols.

Git history is the archive for material that is no longer part of either current as-built or current target design: completed milestones, obsolete alternatives, superseded-only decision chains, migration diaries, audit snapshots and previous models.

## Reconstruction rule

Do not delete a requirement, architecture contract, ADR, engineering contract or UI specification merely because it has been implemented.

Before deleting or absorbing project documentation, verify that the remaining working tree can still reconstruct the designed current system from zero without inventing product/domain/architecture decisions. If a document contains both historical narration and required current design, keep or rewrite the current design; remove only the historical narration.

## Layer discipline

Requirements answer what observable behavior must hold. Domain answers what concepts mean and who owns them. Architecture answers how semantic owners compose and what structural/runtime constraints preserve correctness. Engineering defines current executable-facing contracts and runtime mechanics. UI defines current user-facing composition. Active plans describe only the selected current delta.

Keep truth at its highest owning layer and link downward instead of retelling it unnecessarily. As-built and target contracts may coexist when both are required; never let an as-built compatibility model silently override accepted target semantics.

## Knowledge discipline

Classify material content as accepted, hypothesis, unknown or conflict. Do not turn an unknown into an implementation assumption.

When implementation evidence conflicts with accepted behavior/domain/architecture, resolve the highest affected canonical layer. Runtime artifacts are evidence of as-built implementation, but production code is not a substitute for project documentation.
