# Active execution

Current: `PLAN-I31-application-catalogue-target-migration.md`

Goal: migrate the accepted Application Catalogue target end to end without rewriting existing downstream semantic identities or historical policy truth.

Current task: WP-2 implement additive PostgreSQL persistence and compatibility projection.

## Working set

Read first:
- `docs/plans/active/PLAN-I31-application-catalogue-target-migration.md`
- `src/napms/application_catalogue/application/target_ports.py`
- `src/napms/application_catalogue/adapters/postgres/curation_repository.py`

Expand only when required into ACC migrations, target domain/application models, PostgreSQL integration tests, existing migration/UoW helpers and curation support factories.

## Blockers

None known. M0 and M1 are squash-merged. WP-2 may add infrastructure but must preserve legacy rows and must not invent target Company/Environment/Scope or interaction ownership for legacy data.

## Gate

WP-2 exits when fresh target entities persist/reload transactionally, Deployment Interaction compatibility mapping is explicit and stable, legacy rows remain untouched/readable, concurrency/idempotency behavior is deterministic, and migration replay plus PostgreSQL integration tests pass. No HTTP or Web implementation belongs in this stage.

## Next

Add the minimum additive schema first, then implement the PostgreSQL target repository/factories and focused integration tests. Prove fresh target selection -> compatibility sides/DCS/bindings while preserving legacy coexistence.
