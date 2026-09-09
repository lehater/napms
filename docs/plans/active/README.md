# Active execution

Current: `PLAN-016B-i16b-connectivity-decision-runtime.md`

Goal: replace the transitional local Decision provider with the accepted durable Connectivity Decision runtime while preserving the completed I16A architecture.

Current task: WP4 — expose authorized durable Decision participant record/list/detail runtime without introducing a pending workflow state.

## Working set

Read first:
- `docs/plans/active/PLAN-016B-i16b-connectivity-decision-runtime.md`
- `docs/architecture/connectivity-decision-boundary.md`

Expand only into `docs/engineering/http-api-contract.md`, current Decision application use cases, Authority/ACC adapters, FastAPI runtime/composition and Decision HTTP acceptance tests when a concrete WP4 question requires them.

## Blockers

None. The accepted model owns only final `Allowed | NotAllowed`; no pending/approval queue state may be introduced for UI convenience.

## Gate

WP3 green evidence on commit `da9fd0036412e7419b2a61c2dacb871c1e85efb3`:
- core gate #85 — success;
- postgres persistence gate #70 — success;
- docker local runtime gate #44 — success;
- harness gate #90 — success.

WP3 now proves:
- Scoped Connectivity obtains Decision summaries from the durable Decision BC;
- exact subjects are batch-read under selected responsibility scope + logical asOf;
- Allowed/NotAllowed are projected as coarse final outcomes;
- authoritative absence is NoFinalDecision;
- ambiguity is Unknown;
- persistence failure marks only the Decision enrichment unavailable/partial;
- protected Decision ID/reason/evidence/actor/provenance do not cross the coarse inventory contract;
- the I16A deferred Decision adapter has been removed.

## Next

Execute WP4 only: wire Decision authority and ACC subject adapters into current composition, expose authorized final record/list/detail HTTP contracts, preserve server-owned actor/time/provenance, and keep Web/participant workspace out of scope until runtime gates are green.
