# Active execution

Current: `PLAN-I31-application-catalogue-target-migration.md`

Goal: migrate the accepted Application Catalogue target end to end without rewriting existing downstream semantic identities or historical policy truth.

Current task: WP-3 finalize bounded target read models and task-oriented HTTP API.

## Working set

Read first:
- `docs/plans/active/PLAN-I31-application-catalogue-target-migration.md`
- `docs/engineering/application-catalogue-target-http-contract.md`
- `src/napms/application_catalogue/application/target_read.py`
- `src/napms/application_catalogue/application/target_retirement.py`
- `src/napms/runtime/catalogue_target_http.py`
- `src/napms/runtime/catalogue_target_retirement_http.py`

Expand only when required into target PostgreSQL query/repository adapters, catalogue composition, owner-specific dependency queries and focused runtime/integration tests.

## Blockers

None known. M0-M2 are squash-merged. WP-3 keeps compatibility Component Deployment/DCS IDs backend-only, uses explicit `asOf` for temporal projections, and keeps potentially unbounded catalogue/dependency reads server-bounded.

## Gate

WP-3 exits when the accepted target UI can consume Definition/Deployment lists, Definition tabs, Deployment connectivity/resource-set drill-downs, available-interaction selection, target task commands and blocked-dependency drill-down entirely through authenticated HTTP without client-manufactured internal IDs. No Web implementation belongs in this stage.

## Next

Self-review PR #61 against the WP-3 contract and architecture boundaries. Fix P0/P1 findings, then move the PR to Ready once on the final head so core/PostgreSQL/harness/knowledge/Docker checks execute before squash integration.
