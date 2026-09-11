# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final `contexts / workflows / platform` taxonomy without product/domain semantic change.
Current task: M3 — final milestone PR and hosted gates.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if needed: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.

## Blockers

None.

## Gate

M3 implementation and architectural review are complete: all five workflows live only under `napms.workflows`; generic `napms.composition` is absent; ACC cross-context dependency/read integrations use peer application contracts; workflow persistence bypass is prohibited by architecture tests. Validation: `make test` 806 passed, `make harness-check` passed, `make knowledge-check` passed, PostgreSQL 16 `make postgres-test` 141 passed.

The remaining M3 gate is the final hosted PR suite.

## Next

Open the final M3 milestone PR, run required hosted gates, and squash-merge if green. Do not start M4 before M3 is merged.
