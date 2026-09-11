# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final `contexts / workflows / platform` taxonomy without product/domain semantic change.
Current task: M1 — Repository backend boundary; implementation complete, awaiting architectural review and final hosted gates.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if the architectural decision rationale is needed: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.

## Blockers

Final hosted PR gates are pending because the M1 branch is intentionally not yet represented by a PR.

## Gate

M1 remains the active gate. Local backend/core, harness, knowledge, Docker build and PostgreSQL integration evidence passes; architectural review and final hosted PR gates remain before stage closure.

## Next

Review the M1 repository-boundary migration and run final hosted PR gates. Do not select or start M2 until that review closes M1.
