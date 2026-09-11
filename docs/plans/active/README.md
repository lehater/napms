# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final `contexts / workflows / platform` taxonomy without product/domain semantic change.
Current task: M2 — final milestone PR and hosted gates.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if the architectural decision rationale is needed: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.

## Blockers

None.

## Gate

All ten bounded contexts are under `napms.contexts`; legacy top-level context packages are absent; architecture, core, harness and knowledge checks pass; configured PostgreSQL evidence is 141 passed / 0 skipped. The remaining M2 gate is the final hosted PR suite.

## Next

Open the final M2 milestone PR, run required hosted gates, and squash-merge if green. Do not start M3 before M2 is merged.
