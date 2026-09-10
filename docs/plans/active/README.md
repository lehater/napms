# Active execution

Current: `PLAN-I31-application-catalogue-target-migration.md`

Goal: migrate the accepted Application Catalogue target end to end without rewriting existing downstream semantic identities or historical policy truth.

Current task: WP-0 final validation/integration after contract closure.

## Working set

Read first:
- `docs/decisions/ADR-013-i31-application-catalogue-compatibility-and-reference-semantics.md`
- `docs/engineering/application-catalogue-target-migration-roadmap.md`

Expand only when required into `docs/domain/application-communication-catalogue/target-tactical-model.md`, `docs/requirements/application-catalogue-target.md`, `docs/architecture/application-catalogue-target-boundary.md`, ADR-012, the current ACC Tactical DDD and repository validation workflows.

## Blockers

No M0 semantic blocker remains. PR #58 is pending the final harness/knowledge validation gate.

## Gate

WP-0 local semantic exit is satisfied. Do not begin WP-1 in PR #58. Mark the draft Ready only to request the final hosted gates; inspect their run/job status before claiming PASS. If green, squash-merge M0 and begin WP-1 from a new branch based on the resulting `main`.

## Next

Request final hosted validation for PR #58. On green M0 integration, advance the capsule to WP-1 on the next branch/PR.
