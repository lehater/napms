# Active execution

Current: `PLAN-I31-application-catalogue-target-migration.md`

Goal: migrate the accepted Application Catalogue target end to end without rewriting existing downstream semantic identities or historical policy truth.

Current task: WP-3 close final CI findings for bounded target read models and task-oriented HTTP API.

## Working set

Read first:
- `docs/plans/active/PLAN-I31-application-catalogue-target-migration.md`
- `docs/engineering/application-catalogue-target-http-contract.md`

Expand only when required into target read/retirement application contracts, HTTP routers, PostgreSQL query/repository adapters, catalogue composition, owner-specific dependency queries and focused runtime/integration tests.

## Blockers

None known. M0-M2 are squash-merged. WP-3 keeps compatibility Component Deployment/DCS IDs backend-only, uses explicit `asOf` for temporal projections, and keeps potentially unbounded catalogue/dependency reads server-bounded.

## Gate

WP-3 exits when the accepted target UI can consume Definition/Deployment lists, Definition tabs, Deployment connectivity/resource-set drill-downs, available-interaction selection, target task commands and blocked-dependency drill-down entirely through authenticated HTTP without client-manufactured internal IDs. No Web implementation belongs in this stage.

## Next

Close the failing PostgreSQL and harness gates on PR #61, rerun all applicable checks on the final head, then squash-merge M3 only after every required gate is green.
