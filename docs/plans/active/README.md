# Active execution

Current: `PLAN-016B-i16b-connectivity-decision-runtime.md`

Goal: replace the transitional local Decision provider with the accepted durable Connectivity Decision runtime while preserving the completed I16A architecture.

Current task: WP6 — make the normal local product journey use real durable Decisions and remove deterministic local allow plumbing from normal composition.

## Working set

Read first:
- `docs/plans/active/PLAN-016B-i16b-connectivity-decision-runtime.md`

Expand only into current local seed/composition, Decision authority assignments, Docker smoke and runtime configuration when a concrete WP6 question requires them.

## Blockers

None. Deterministic Decision adapters may remain only as explicit test plumbing after WP6; they must not be selectable by the normal local runtime.

## Gate

WP5 green evidence on commit `5977f7dd2075999fe0d6d51212468b32739200a1`:
- web gate #48 — success;
- core gate #90 — success;
- postgres persistence gate #75 — success;
- docker local runtime gate #49 — success;
- harness gate #95 — success.

WP5 now proves:
- Decisions is an active specialized workspace under the current Connectivity-first shell;
- authorized final Decisions can be recorded, listed and inspected with reason/provenance/validity/evidence/supersession;
- Decision replacement is explicit immutable supersession rather than edit;
- Connectivity routes NoFinalDecision to Record decision;
- Request access is offered only when a final Allowed Decision already exists;
- NotAllowed and Unknown do not expose a misleading Request access action;
- the historical Compose-first UI was not reintroduced.

## Next

Execute WP6 only: seed local DecideConnectivity / ReadConnectivityDecision authority, provide durable Allowed and NotAllowed demo paths, switch normal local Access Policy composition from `local-dev:allowed` to the durable Decision consumer, and prove the Docker/public endpoint journey. Do not start canonical closure/WP7 until this is green.
