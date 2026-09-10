# Active execution

Current: `PLAN-I31-application-catalogue-target-migration.md`

Goal: migrate the accepted Application Catalogue target end to end without rewriting existing downstream semantic identities or historical policy truth.

Current task: WP-1 final validation/integration for target Domain/Application/Ports.

## Working set

Read first:
- `docs/plans/active/PLAN-I31-application-catalogue-target-migration.md`
- `src/napms/application_catalogue/application/target_ports.py`

Expand only when required into the target Tactical DDD, ADR-013, `target_curation.py`, `target_lifecycle.py`, `target_binding_curation.py`, `target_metadata_curation.py`, `target_read.py`, domain target model and matching tests.

## Blockers

No known P0/P1 blocker. M0 is merged. M1 self-review closed compatibility-binding leakage and made the effective-binding dependency query explicit in the owned target repository contract.

## Gate

Infrastructure remains closed for WP-1: no PostgreSQL, HTTP or Web implementation belongs in PR #59. M1 local semantic exit is satisfied pending final hosted validation. Mark Ready only to request the core/harness gates; inspect their exact run/job status before claiming PASS or merging.

## Next

Run final hosted validation for PR #59. If green, squash-merge M1. Start WP-2 from a new branch based on resulting `main`; implement additive PostgreSQL persistence and the explicit Deployment Interaction compatibility projection there.
