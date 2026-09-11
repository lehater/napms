# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final `contexts / workflows / platform` taxonomy without product/domain semantic change.
Current task: M1 — Repository backend boundary.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if the architectural decision rationale is needed: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.

## Blockers

None.

## Gate

M1 is behavior-preserving repository movement. Required evidence is defined in the active plan: backend/core, harness, knowledge, affected Docker/integration checks and final hosted PR gates.

## Next

Execute M1 exactly as defined in `PLAN-target-code-structure-migration.md`. Do not start M2 semantic-module moves in the same stage.
