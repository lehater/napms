# Active execution

Current: `PLAN-I31-application-catalogue-target-migration.md`

Goal: migrate the accepted Application Catalogue target end to end without rewriting existing downstream semantic identities or historical policy truth.

Current task: WP-3 implement bounded target read models and task-oriented HTTP API.

## Working set

Read first:
- `docs/plans/active/PLAN-I31-application-catalogue-target-migration.md`
- `src/napms/application_catalogue/application/target_read.py`
- `src/napms/runtime/catalogue_application_workspace_http.py`

Expand only when required into the target PostgreSQL repository, catalogue composition, target curation/lifecycle/binding use cases, HTTP error conventions and focused runtime/integration tests.

## Blockers

None known. M0-M2 are squash-merged. WP-3 must keep compatibility Component Deployment IDs backend-only and must implement server-bounded search/filter/sort/paging rather than rebuilding the old whole-tree workspace contract.

## Gate

WP-3 exits when the accepted target UI can consume Definition/Deployment lists, Definition tabs, Deployment connectivity/resource-set drill-downs and task commands entirely through authenticated HTTP without client-manufactured internal IDs. No Web implementation belongs in this stage.

## Next

Implement the PostgreSQL target read projection first, then expose authenticated target routes and mutation composition. Add focused HTTP/security/integration tests and keep the current I27 routes available only as compatibility until the Web switches in WP-4.
