# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: finish the structural migration and leave final backend/Web taxonomy protected by executable rules.
Current task: M7 implementation complete; awaiting architectural review.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

## Blockers

None.

## Gate

M1-M6 are merged. M7 removed the pre-M5 ACC curation facade and transitional dependency-port fallbacks, replaced vacuous legacy checks with final generic taxonomy enforcement, and aligned canonical structure guidance with the repository. Backend, Web, Harness, Knowledge, PostgreSQL 16, Docker and J01/J02/J03 local gates pass.

## Next

Perform the M7 architectural review. Do not create the final PR or retire the active plan yet.
