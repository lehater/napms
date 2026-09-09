# Active execution

Current: `PLAN-016B-i16b-connectivity-decision-runtime.md`

Goal: replace the transitional local Decision provider with the accepted durable Connectivity Decision runtime while preserving the completed I16A architecture.

Current task: WP2 — deliberate review boundary after green WP0/WP1; next implementation is minimal Access Policy integration.

## Working set

Read first:
- `docs/plans/active/PLAN-016B-i16b-connectivity-decision-runtime.md`
- `docs/requirements/connectivity-decision-core.md`
- `docs/architecture/connectivity-decision-boundary.md`

Expand only when WP2 requires a current Access Policy port/materialization file.

## Blockers

None. PR #26 remains historical implementation evidence only; its pre-I16A composition/UI must not be merged or rebased.

## Gate

WP0/WP1 green evidence on commit `ebea4aec5306d2cd8c9f02aff44e8af4225ed09a`:
- core gate #81 — success;
- postgres persistence gate #66 — success;
- docker local runtime gate #40 — success;
- harness gate #86 — success.

## Next

Review the durable Decision record/select slice. Then execute WP2 only: evolve the Access Policy Decision consumer projection to exact subject + governance scope + asOf, integrate the Decision adapter, and prove Allowed/NotAllowed/missing/expired fail-closed materialization before touching Scoped Connectivity or Web.
