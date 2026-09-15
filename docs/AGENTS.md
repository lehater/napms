# Documentation scope

Apply root `AGENTS.md` first.

## Canonical ownership

- `requirements/` — current observable product/quality behavior.
- `domain/` — current meaning, identity, lifecycle and semantic ownership.
- `architecture/` — current accepted structural/runtime constraints.
- `engineering/` — current operational and implementation contracts.
- `ui/` — current reusable presentation/interaction guidance.
- `plans/active/` — current execution state only.
- `process/` — reusable working protocols.

Git history is the sole archive. Do not retain completed milestones, supersession chains, migration diaries, audit reports, previous models or absorbed decision records in the working documentation tree.

## Layer discipline

Requirements answer what observable behavior must hold. Domain answers what concepts mean and who owns them. Architecture answers how current semantic owners compose and what structural constraints preserve correctness. Engineering describes current executable/operational mechanics. UI describes presentation. Active plans describe only the selected current delta.

Keep current truth at its highest owning layer and link downward instead of retelling it. If an artifact is no longer current or its decision has been fully absorbed by its owner, remove it.

## Knowledge discipline

Classify material content as accepted, hypothesis, unknown or conflict. Do not turn an unknown into an implementation assumption.

When code evidence conflicts with accepted behavior/domain/architecture, update the highest affected canonical truth before implementation. Runtime artifacts may be evidence of implementation state, but they do not override current product/domain truth.
