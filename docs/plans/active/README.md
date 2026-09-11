# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final `contexts / workflows / platform` taxonomy without product/domain semantic change.
Current task: M2 — the `technical_access_evidence` and `network_enforcement_placement` work package is complete on the milestone branch and awaits architectural review.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if the architectural decision rationale is needed: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.

## Blockers

Local PostgreSQL execution evidence is unavailable: `make postgres-test` completed successfully but skipped all 141 tests because the PostgreSQL test environment was not configured.

## Gate

Both contexts use only the final `napms.contexts` namespace, all consumers are updated, architecture boundaries are enforced, and targeted/core/harness/knowledge checks are green. PostgreSQL tests remain to be exercised in a configured environment.

Hosted PR gates are deferred until the complete M2 milestone is ready for one final PR.

## Next

Review the completed `technical_access_evidence` and `network_enforcement_placement` work package. Do not select another context or start M3 before that review.
