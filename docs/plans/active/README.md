# Active execution

Current: `PLAN-016B-i16b-connectivity-decision-runtime.md`

Goal: replace the transitional local Decision provider with the accepted durable Connectivity Decision runtime while preserving the completed I16A architecture.

Current task: WP3 — integrate durable Decision summary into the existing I16A Scoped Connectivity Inventory without leaking protected Decision detail.

## Working set

Read first:
- `docs/plans/active/PLAN-016B-i16b-connectivity-decision-runtime.md`
- `docs/requirements/scoped-connectivity-inventory.md`
- `docs/architecture/scoped-connectivity-inventory.md`
- `docs/architecture/connectivity-decision-boundary.md`

Expand only into current Scoped Connectivity ports/adapters/composition and Decision selection code required by WP3.

## Blockers

None. PR #26 remains historical implementation evidence only; it has no I16A Scoped Connectivity integration to copy.

## Gate

WP2 green evidence on commit `d3d70b0ad4bcd65adf4333dcb381ba8e011072c2`:
- core gate #83 — success;
- postgres persistence gate #68 — success;
- docker local runtime gate #42 — success;
- harness gate #88 — success.

WP2 now proves:
- exact Access Policy Decision lookup by subject + governance scope + logical time;
- durable Allowed Decision materializes an Access Rule;
- durable NotAllowed creates no Rule;
- missing/expired Decision fails closed as DecisionUnknown;
- ambiguous/not-found Decision selection maps to the consumer-owned Unknown projection;
- the transitional local adapter conforms to the same exact consumer contract without becoming durable truth.

## Next

Execute WP3 only: replace `DeferredConnectivityDecisionSummaryAdapter` with a real Decision summary adapter in current I16A composition, preserve coarse `Allowed | NotAllowed | NoFinalDecision | Unknown` semantics, and prove no protected reason/provenance detail crosses the inventory boundary.
