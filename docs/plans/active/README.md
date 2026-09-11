# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final `contexts / workflows / platform` taxonomy without product/domain semantic change.
Current task: M3 — final implementation package complete; awaiting architectural review.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if needed: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.

## Blockers

None.

## Gate

Implementation gate passed: all five workflows exist only under `napms.workflows`; generic `napms.composition` is absent; ACC dependency/read integrations use peer application contracts; platform owns wiring/config/migrations only. Validation: `make test` 806 passed, `make harness-check` passed, `make knowledge-check` passed, PostgreSQL 16 `make postgres-test` 141 passed.

Hosted PR gates remain deferred until complete M3 milestone review.

## Next

Perform final M3 architectural review. Do not start M4 or create the PR before that review.
