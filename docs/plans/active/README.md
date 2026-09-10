# Active execution

Current: `PLAN-I31-application-catalogue-target-migration.md`

Goal: migrate the accepted Application Catalogue target end to end without rewriting existing downstream semantic identities or historical policy truth.

Current task: WP-2 final validation/integration for PostgreSQL target persistence and compatibility projection.

## Working set

Read first:
- `docs/plans/active/PLAN-I31-application-catalogue-target-migration.md`
- `src/napms/application_catalogue/adapters/postgres/migrations/0005_application_catalogue_target.sql`

Expand only when required into `target_repository.py`, target application/domain contracts, curation support, PostgreSQL migration runner and the I31 target integration tests.

## Blockers

No known P0/P1 blocker. M0/M1 are merged. The target schema is additive, target compatibility sides are explicitly mapped, legacy I27 rows are not promoted, and executable evidence covers target write/reload plus consumption through the existing downstream repository contract.

## Gate

WP-2 local implementation exit is satisfied pending final hosted validation. No HTTP or Web implementation belongs in PR #60. Mark Ready only to request final applicable core/PostgreSQL/harness/browser regression gates; inspect job-level conclusions before claiming PASS or merging.

## Next

Run final hosted validation for PR #60. If green, squash-merge M2. Start WP-3 from a new branch based on resulting `main`; implement bounded HTTP/read models and target task commands there.
