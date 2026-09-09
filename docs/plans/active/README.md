# Active execution — resume capsule

Current: `PLAN-029-i16a-scoped-connectivity-workspace.md`

Roadmap: `docs/engineering/post-wave1-product-completion-roadmap.md`

Goal: close the selected responsibility scope -> local Resource semantics and implement the first resource-centric Scoped Connectivity Inventory / Connectivity workspace.

Current task: WP-01 — Domain re-entry: responsibility scope and local Resources.

Working mode: domain semantics.

Primary workflow: `.agents/skills/domain-model-change/SKILL.md`.

## Working set

Read first:
- `docs/domain/resource-role-model.md` — ownership, organizational relations and lifecycle consequences.
- `docs/domain/semantic-ownership.md` — ownership map.
- `docs/domain/capabilities.md` — current capability ownership.

Expand only if the current decision requires more evidence:
- `docs/requirements/scoped-connectivity-inventory.md`
- `docs/domain/ubiquitous-language.md`
- `docs/domain/strategic-model.md`
- `docs/architecture/scoped-connectivity-inventory.md`

Do not read the full PLAN-029 by default. Use it for coordination, task transition, or when this capsule lacks a material fact required by the current task.

## Recovery facts — non-authoritative

These are compact recovery summaries; their canonical owners win if they conflict.

- The selected responsibility scope defines the local/responsibility side of the workspace. Source: `docs/requirements/scoped-connectivity-inventory.md`.
- Resource identity must remain independent from changing responsibility relations. Source: `docs/domain/resource-role-model.md`.
- Responsibility, Authority Management admission and catalogue visibility are separate concerns. Sources: `docs/domain/resource-role-model.md`, `docs/requirements/scoped-connectivity-inventory.md`.
- Do not introduce `Resource.owner_id` / `Resource.scope_id` as an implementation shortcut. Source: `docs/requirements/scoped-connectivity-inventory.md`.

## Blockers

P0 — selected responsibility scope -> local Resource semantics are not yet accepted:
- semantic owner of the relation;
- relation identity and cardinality;
- temporal semantics;
- whether one Resource may participate in multiple responsibility scopes;
- relationship to Authority Management assignments.

## Gate

Implementation is CLOSED until the scope-to-Resource semantic relation is unambiguous enough for an application query.

## Next

Resolve the relation owner, identity, cardinality and temporal semantics using current canonical domain evidence. Update the highest affected canonical DDD artifacts first; only then advance to the inventory semantic-contract stage.
