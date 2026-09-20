# Backend quality design

Status: ACCEPTED candidate

## Correctness and integrity

- No protected mutation returns success before its owning transaction commits.
- A failed/unknown commit is surfaced as failure/unknown; retries rely on idempotency keys or owner identity constraints rather than blind replay.
- Concurrent mutation of one aggregate uses optimistic version checking; stale writes fail explicitly.
- Permission recording is final per AccessRequest and idempotent for the same decision payload.
- First ALLOWED rule materialization is idempotent for one AccessRequest.
- Policy materialization never reports COMPLETE when any included effective rule is unresolved.

## Consistency

- Write consistency: strong atomic consistency inside one aggregate/owning module transaction.
- Cross-context writes: none required for accepted flows; references are validated synchronously then stored as immutable references/provenance.
- Policy materialization: one coherent read snapshot across all required module-owned persistence at the requested logical `asOf`.
- Historical references must remain resolvable or produce explicit UNRESOLVED; no silent rebinding to newer semantic identity.

## Reliability/failure semantics

- Dependency timeout/unavailability is distinct from domain rejection.
- Retriable transport/storage failure does not change domain outcome without a committed transaction.
- No automatic retry of non-idempotent operation without an idempotency key/known commit status.
- Cancellation propagates to in-flight read/query work; committed mutations are never represented as cancelled/rolled back after commit.

## Performance/capacity applicability

No accepted source supplies numeric latency, throughput, dataset-size or availability targets. Therefore:
- numeric SLO/capacity optimization is DEFERRED_NONBLOCKING;
- queries exposed as collections must be paginated/bounded;
- materialization must stream or page internal reads where necessary but preserve one logical snapshot;
- reopen performance/capacity design when concrete deployment/load targets appear.

## Availability/recovery applicability

The selected MVP requires durable authoritative state but no accepted RPO/RTO/site-failure target. Recovery technology/topology is DEFERRED_NONBLOCKING for product-code implementation and must be resolved before a production deployment claims backup/continuity guarantees. Data migrations must remain deterministic and restart-safe.

## Change-transition applicability

This experiment defines a greenfield target backend rather than migration from the current NAPMS implementation. Change Transition Design is NOT_APPLICABLE to blind target closure. Any later adoption/migration from old NAPMS is a separate post-freeze transition problem.

## External dependency applicability

Material dependencies are limited to runtime/framework, relational database and OIDC provider/client libraries selected downstream. Dependency provenance/vulnerability policy is Engineering Policy/verification work; no product semantics are derived from packages.
