# Active execution

Current: `PLAN-I31-application-catalogue-target-migration.md`

Goal: migrate the accepted Application Catalogue target end to end without rewriting existing downstream semantic identities or historical policy truth.

Current task: WP-1 implement target Domain/Application/Ports and executable core tests.

## Working set

Read first:
- `docs/domain/application-communication-catalogue/target-tactical-model.md`
- `src/napms/application_catalogue/application/ports.py`

Expand only when required into ADR-013, `src/napms/application_catalogue/domain/`, the smallest existing curation service used as a pattern, and matching `tests/application_catalogue/` files.

## Blockers

None known. M0 contract is merged and authoritative.

## Gate

Infrastructure gate is closed for WP-1: no PostgreSQL, HTTP or Web implementation. Local exit requires target entities/invariants, application commands and owned ports to be executable in memory with tests, while existing downstream identity contracts remain unchanged. Run core and harness checks before final integration.

## Next

Implement the minimum target domain model first, then target application commands/dependency ports and core tests. Keep compatibility identity as an ACC-owned contract; do not implement persistence mapping in WP-1.
