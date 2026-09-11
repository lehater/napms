# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: finish the structural migration and leave final backend/Web taxonomy protected by executable rules.
Current task: M7 — purge structural compatibility debt and strengthen final enforcement.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

## Blockers

None.

## Gate

M1-M6 are merged. Backend production top-level is already exactly `contexts / workflows / platform`; Web is already `app / features / components/ui / lib`. M7 audit found a pre-M5 ACC curation re-export facade, transitional dependency-port fallbacks, vacuous legacy adapter checks, and structure docs that still describe migration-era state. Accepted product/domain compatibility is not part of this purge.

## Next

Implement the final M7 purge/enforcement package, run full local validation including real PostgreSQL and browser/runtime evidence, push, and stop for architectural review. Do not create the final PR or retire the active plan yet.
