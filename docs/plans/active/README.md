# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final `contexts / workflows / platform` taxonomy without product/domain semantic change.
Current task: M4 — architectural review complete; final milestone PR and hosted gates.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if needed: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.

## Blockers

None.

## Gate

M4 implementation and architectural review are complete: production taxonomy is `contexts / workflows / platform`; legacy `napms.bootstrap`, `napms.runtime`, and `napms.composition` are absent; generic HTTP shell is feature-independent; feature HTTP wiring and executable assembly live under `platform/bootstrap`; core layers do not import platform. Validation: targeted auth 13 passed, platform/architecture 183 passed, `make test` 807 passed, `make harness-check` passed, `make knowledge-check` passed, PostgreSQL 16 `make postgres-test` 141 passed without skips, and Docker Compose config/build passed.

The remaining M4 gate is the final hosted PR suite.

## Next

Open the final M4 milestone PR, run required hosted gates, and squash-merge if green. Do not start M5 before M4 is merged.
