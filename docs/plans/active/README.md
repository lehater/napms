# Active execution — resume capsule

Current: `PLAN-029-i16a-scoped-connectivity-workspace.md`

Roadmap: `docs/engineering/post-wave1-product-completion-roadmap.md`

Goal: close the selected responsibility scope -> local Resource semantics and implement the first resource-centric Scoped Connectivity Inventory / Connectivity workspace.

Current task: WP-01 — Domain re-entry: responsibility scope and local Resources.

Working mode: domain semantics.

Primary workflow: `.agents/skills/domain-model-change/SKILL.md`.

## Working set

Read first:
- `docs/domain/resource-role-model.md`
- `docs/domain/semantic-ownership.md`
- `docs/domain/capabilities.md`
- `docs/requirements/scoped-connectivity-inventory.md`

Expand only if the current decision crosses those boundaries:
- `docs/domain/ubiquitous-language.md`
- `docs/domain/strategic-model.md`
- `docs/architecture/scoped-connectivity-inventory.md`

Do not read the full PLAN-029 by default. Use it for coordination, stage transition, or when this capsule lacks a material fact required by the current task.

## Known / accepted

- The selected responsibility scope defines the local/responsibility side of the workspace.
- Resource identity must remain independent from changing responsibility relations.
- Responsibility, Authority Management admission and catalogue visibility are separate concerns.
- Do not introduce `Resource.owner_id` / `Resource.scope_id` as an implementation shortcut.

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
