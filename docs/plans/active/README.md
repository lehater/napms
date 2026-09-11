# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final `contexts / workflows / platform` taxonomy without product/domain semantic change.
Current task: M4 — implementation complete; awaiting architectural review.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if needed: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.

## Blockers

None.

## Gate

M4 implementation gate passed: production taxonomy is `contexts / workflows / platform`; legacy `napms.bootstrap` and `napms.runtime` are absent; the generic HTTP shell is feature-independent; all feature wiring and executable assembly live under `platform/bootstrap`. Validation: targeted platform/architecture 183 passed, `make test` 807 passed, `make harness-check` passed, `make knowledge-check` passed, PostgreSQL 16 `make postgres-test` 141 passed, and Docker Compose config/build passed.

## Next

Perform final M4 architectural review. Do not start M5 or create the PR before that review.
