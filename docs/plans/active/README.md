# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final `contexts / workflows / platform` taxonomy without product/domain semantic change.
Current task: M1 — Repository backend boundary; implementation and architectural review complete, final hosted gates pending on PR #73.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if the architectural decision rationale is needed: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.

## Blockers

Final hosted PR gates for M1 are pending. Local J03 failed with `Record Decision` disabled, while the latest pre-M1 hosted browser journey on PR #71 passed; use the hosted M1 journey gate as the authoritative reproduction check.

## Gate

M1 remains active until PR #73 hosted gates pass. Local backend/core, harness, knowledge, Docker build and PostgreSQL integration evidence passes; the reviewed diff is mechanical with no intended semantic change.

## Next

Run the final hosted gates and squash-merge PR #73 if green. Then execute M2 first on `network_environment_operations`: dependency review found only the explicit composition stub and `network_operator_view` as production consumers outside the context, making it the lowest-coupling bounded-context migration candidate. Do not start M2 before M1 merges.
