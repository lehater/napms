# Active execution

Current: `PLAN-016B-i16b-connectivity-decision-runtime.md`

Goal: close I16B after replacing the transitional deterministic Decision path with the durable Connectivity Decision runtime while preserving I16A architecture.

Current task: WP7 — canonical closure only.

## Working set

Read first:
- `docs/plans/active/PLAN-016B-i16b-connectivity-decision-runtime.md`

Expand only into canonical current-state, roadmap, HTTP/API, Web UI, Decision architecture/ADR and active-plan index files required to record the implemented truth and promote I17.

## Blockers

None. Product implementation WPs 0–6 are green.

## Gate

WP6 green evidence on commit `d9e96c8e419a15a141f86192ba7597afb7b7ed14`:
- web gate #50 — success;
- core gate #92 — success;
- postgres persistence gate #77 — success;
- docker local runtime gate #51 — success;
- harness gate #97 — success.

WP6 now proves:
- normal local HTTP composition does not select a deterministic allow adapter;
- Access Policy consumes durable Decision through the current PostgreSQL composition;
- the local demo actor has independent DecideConnectivity and ReadConnectivityDecision authority;
- public Docker journey starts at NoFinalDecision, records durable Allowed, materializes a Rule, then records immutable superseding NotAllowed;
- a later NotAllowed Decision does not silently mutate the existing Access Rule;
- a proposal under the current NotAllowed Decision returns business NotAllowed/no new Rule;
- deterministic `LocalDevAllowedConnectivityDecisionAdapter` runtime/test files were removed;
- stale Web copy describing `local-dev:allowed` was removed.

## Next

Execute WP7 only: reconcile canonical docs with implemented I16B truth, run final relevant gates, remove this active plan from execution, and promote I17. Do not start I17 implementation on this branch.
