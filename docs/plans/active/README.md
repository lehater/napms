# Active execution

Current: `PLAN-016B-i16b-connectivity-decision-runtime.md`

Goal: replace the transitional local Decision provider with the accepted durable Connectivity Decision runtime while preserving the completed I16A architecture.

Current task: WP1 — make the ported Decision core and PostgreSQL record/select slice green on the current main baseline.

## Working set

Read first:
- `docs/plans/active/PLAN-016B-i16b-connectivity-decision-runtime.md`
- `docs/requirements/connectivity-decision-core.md`
- `docs/architecture/connectivity-decision-boundary.md`

Expand only when a failing gate or implementation dependency requires another file.

## Blockers

None. PR #26 is historical implementation evidence only and must not be merged/rebased into this branch.

## Gate

For the current slice, core, PostgreSQL persistence, Docker local runtime and harness gates must pass. A failing gate is fixed before advancing to Access Policy or Web integration.

## Next

Fix any current WP0/WP1 gate failures, confirm durable record/select is green, update the resume capsule, then stop for review before WP2.
