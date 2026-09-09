# Network Environment Operations — tactical model

Status: `accepted I22 stub-first Tactical DDD`.

Date: 2026-09-10.

## Responsibility

Network Environment Operations owns the lifecycle and outcome of one controlled target mutation attempt downstream of accepted rendering.

A separate semantic boundary is justified because execution has its own operation identity, mutation authority, optimistic-concurrency boundary, failure/recovery vocabulary and audit lifecycle. It does not own Access Rule, desired enforcement, placement or rendered configuration meaning.

## Aggregate/value model

`NetworkOperation` is identified by `operation_id` and binds:
- Enforcement Target;
- renderer name/version;
- artifact digest;
- actor/scope;
- pre-state expectation;
- ordered operation events;
- final operation result when known.

The first executable slice keeps state in memory through a port-backed repository/stub. Durable persistence is deferred.

## Outcomes

Final outcome:
- `Verified`;
- `Rejected`;
- `PreconditionFailed`;
- `Drift`;
- `Unknown`.

Apply transport outcome:
- `Applied`;
- `Rejected`;
- `Unknown`.

`Applied` is intermediate only. It never means verified desired state by itself.

## Invariants

1. One operation id binds exactly one target + artifact digest intent.
2. Reusing an operation id with different intent is conflict/fail-closed.
3. Identical retry returns the established operation result and does not repeat mutation.
4. Mutation cannot start before explicit mutation authority admission and successful pre-check.
5. Expected revision mismatch or observed concurrent revision change prevents mutation.
6. Unknown apply outcome cannot be converted into success or blindly retried.
7. Verified requires successful post-check proving requested artifact correspondence.
8. Transport/provider references are provenance, not domain identity.
9. I22 never rewrites I21 rendered artifact semantics for device convenience.
10. Stub execution proves orchestration semantics only, not real Cisco compatibility.

## Stub-first execution boundary

The first adapter is a deterministic in-process target stub with explicit scenario controls. It models target revision + applied artifact digest and can inject rejection, uncertain apply, concurrent drift and post-apply drift.

This adapter is test/runtime simulation, not a Cisco implementation. A future real Cisco adapter must satisfy the same application-owned ports and may require a new accepted target transport contract without changing operation identity/outcome semantics unless real evidence forces a domain revision.

## Ownership boundaries

Authority Management owns whether the actor may execute the mutation action.

Access Policy Realization/I21 owns rendered artifact correctness.

Network Enforcement Placement owns Enforcement Target placement meaning.

Technical Access Evidence may later record independently sourced configured/post-change evidence, but I22's immediate post-check observation is operation evidence and does not automatically become TAE truth.
