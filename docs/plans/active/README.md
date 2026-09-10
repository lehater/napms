# Active execution

Current: `PLAN-I31-application-catalogue-target-migration.md`

Goal: migrate the accepted Application Catalogue target end to end without rewriting existing downstream semantic identities or historical policy truth.

Current task: WP-4 replace the I27 Applications Web projection with the accepted target information architecture.

## Working set

Read first:
- `docs/plans/active/PLAN-I31-application-catalogue-target-migration.md`
- `docs/ui/application-catalogue-target.md`
- `docs/ui/application-catalogue-wireframes.md`

Expand only when required into the target HTTP contract, current Web Applications implementation, shared Web primitives and focused Web/browser tests.

## Blockers

None known. M0-M3 are squash-merged. WP-4 consumes only the target HTTP API and keeps compatibility Component Deployment/DCS identities out of the UI.

## Gate

WP-4 exits when the representative Application Catalogue Web flow implements `Definitions | Deployments`, Definition tabs, Deployment connectivity/Resource-set drill-down, Add interaction and blocked-dependency UX while remaining server-bounded and avoiding hard delete/internal identity noise.

## Next

Open Draft PR #62 from `i31/m4-web-target`, implement the smallest end-to-end target working-set slice first, run Web-focused validation, then expand only to the remaining accepted flows.
