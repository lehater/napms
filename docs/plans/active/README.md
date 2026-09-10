# Active execution

Current: `PLAN-I31-application-catalogue-target-migration.md`

Goal: migrate the accepted Application Catalogue target end to end without rewriting existing downstream semantic identities or historical policy truth.

Current task: WP-4 final validation of the target Applications Web projection in Draft PR #62.

## Working set

Read first:
- `docs/plans/active/PLAN-I31-application-catalogue-target-migration.md`
- `docs/ui/application-catalogue-target.md`
- `docs/engineering/application-catalogue-target-http-contract.md`

Expand only when required into the target Web catalogue feature, target lifecycle composition/HTTP adapter and focused browser/runtime tests.

## Blockers

None known. M0-M3 are squash-merged. WP-4 keeps compatibility Component Deployment/DCS identities out of the Applications UI and preserves server-owned lifecycle/concurrency semantics.

## Gate

WP-4 exits when `Definitions | Deployments`, Definition tabs, target create/edit/retire flows, Deployment connectivity/selection, Resource-set membership and blocked-dependency UX are server-bounded and pass all applicable core/PostgreSQL/Web/harness/Docker/browser gates.

## Next

Run the final hosted gates on the documentation-final PR #62 head, fix concrete failures only, complete diff/review-thread inspection, then mark Ready and squash-merge M4 before starting WP-5 from the resulting `main`.
