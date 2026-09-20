# Backend quality design

Status: ACCEPTED after Coding-Agent Challenge 04 repair

## Correctness and integrity

- No protected mutation returns success before its owning transaction commits.
- Unknown/failed commit is never fabricated as success; recovery uses accepted idempotency semantics.
- Concurrent mutation of one aggregate uses its accepted optimistic version and fails stale writes explicitly.
- Cross-Application Interaction is valid when referenced Components and communication semantics are valid; quality/infrastructure layers must not reintroduce a same-Application constraint.
- Equal AccessSubjects across multiple ALLOWED AccessRequests converge on one authoritative PolicyRule.
- A new AuthorizationEvidence or justification association mutates the whole PolicyRule aggregate version; operational state/window is not reset by later ALLOWED evidence.
- DENIED creates no new Rule/current access.
- Need currentness is Business Connectivity truth; retirement does not silently rewrite permission/operational state.
- PolicyRule effectiveness is evaluated from ACTIVE/INACTIVE + absolute effective window at one server-owned evaluationAt.
- Policy materialization reports COMPLETE only when every selected **effective** Rule is fully resolvable.
- INACTIVE/out-of-window selected Rules do not impose technical-realization completeness.
- Zero current Need yields reconciliation evidence, not automatic revocation and not materialization failure by itself.
- Normalization never broadens/narrows traffic semantics or erases independent Rule provenance.

## Consistency

### Write ownership

Strong atomic consistency is required inside each owner transaction.

Optimistic aggregate owners:
- Resource — endpoint/address/Site/responsibility mutation;
- Application — Component creation;
- Interaction — revision publication;
- BusinessProcess — organization/Need mutation;
- AccessRequest — final decision;
- PolicyRule — authorization-evidence set, justification set, operational state/window.

No child-level competing version is allowed.

### Cross-owner reads

- Cross-owner references are validated synchronously through owner ports.
- Ordinary owner writes use PostgreSQL READ COMMITTED.
- SubmitAccessRequest and justification attachment require mutable ConnectivityNeed currentness to remain valid through Access Policy commit; Business Connectivity supplies a transaction-bound FOR SHARE-equivalent Need read lock that blocks retirement/update until transaction end.
- Peer owner tables remain read-only to Access Policy.
- Composed multi-owner reads use read-only REPEATABLE READ snapshots.
- Historical immutable refs are never silently rebound.

### Idempotency

For accepted duplicate-sensitive commands:
- committed same-key/same-fingerprint replay is resolved before NEW-command If-Match validation;
- concrete target participates in idempotency scope;
- different fingerprint conflicts;
- state + idempotency result commit atomically;
- automatic application-level mutation retry is forbidden;
- concurrent identical idempotency wait resolves to replay after commit, NEW after rollback, or DEPENDENCY_UNAVAILABLE/503 on bounded timeout/DB failure; in-progress equality is never itself a conflict.

### Current policy materialization

- caller-selected historical asOf is not supported;
- backend assigns one current `evaluationAt` when the read snapshot begins;
- selected Rules, Need currentness, InteractionRevision, Deployment and Resource realization are read from one coherent snapshot;
- materialization is read-only and owns no durable semantic state;
- dependency failure is not converted into UNRESOLVED.

## Collection/query boundedness

No accepted source supplies numeric dataset-size/latency/throughput targets, but unbounded request memory/query surfaces are not acceptable implementation ambiguity.

Therefore every externally exposed **growing collection query** has a cursor-paged contract:
- Resource endpoints;
- Resource history;
- Application Components;
- Interaction revisions;
- BusinessProcess Needs;
- PolicyRule AuthorizationEvidence;
- PolicyRule justifications;
- PolicyRule operational history.

Interface Design owns the page contract:
- default page size 50;
- valid range 1–200;
- opaque query-specific forward cursor;
- no silent truncation.

Parent/current entity reads expose scalar state and collection counts, not unbounded embedded arrays.

Fixed-cardinality values are exempt:
- Resource OWNER/ADMINISTRATOR current slots;
- AccessSubject;
- current operational state/window.

## Materialization capacity behavior

Policy materialization is an export operation rather than an ordinary collection-query endpoint.

Requirements:
- one read-only coherent snapshot remains open for a two-phase operation;
- Phase 1 preflights all selected effective facts/issues/dependencies with bounded page/chunk reads and determines COMPLETE/UNRESOLVED before HTTP response commitment;
- dependency/runtime failure during preflight returns 503/500 before any 200 body is committed;
- Phase 2 repeats bounded traversal in the same snapshot and streams the already-determined result;
- implementation must not require holding the complete export row set in memory;
- row order has no domain meaning unless Interface Design states otherwise;
- every selected Rule emits one complete streamed export-provenance record containing its authorization evidence, participant-attributed Need justifications/currentness and reconciliation flags;
- PolicyRuleRef correlates normalized technical rows to that provenance record;
- full provenance is therefore self-contained in the export and does not require `policy.read`;
- the same audit remains separately available through paginated Rule read endpoints;
- transport/cancellation failure after response commitment yields an incomplete/truncated response, never a valid syntactically complete export.

Exact SQL cursor/chunk size, HTTP buffering/chunking implementation and memory data structures are implementation freedoms so long as the self-contained export provenance, response contract and one-snapshot semantics are preserved. Explicit subset size has no domain cardinality cap; only configured HTTP request-body bytes bound transport input.

## Reliability/failure semantics

- Dependency timeout/unavailability is distinct from domain rejection.
- Retriable transport/storage error cannot alter domain outcome without committed transaction.
- No automatic retry of a mutation after unknown commit.
- Client cancellation/deadline propagates to DB/materialization work.
- A committed mutation is never later represented as rolled back because response delivery was cancelled.
- OIDC invalid credential is distinct from inability to validate because key dependency is unavailable.

## Performance/capacity applicability

Numeric latency, throughput, concurrency and dataset-size objectives are DEFERRED_NONBLOCKING because no source target exists.

Correctness gates still include:
- accepted pagination limits;
- request/database timeouts;
- bounded materialization memory behavior;
- no accidental N+1 external dependency fetch in materialization (all current dependencies are local DB owner reads).

Reopen quantitative Performance/Capacity Design when concrete load/SLO inputs exist.

## Availability/recovery applicability

Authoritative state is durable, but no accepted RPO/RTO/site-failure target exists. Backup/restore/HA topology remains DEFERRED_NONBLOCKING for product-code closure and must be resolved before production continuity claims.

Migrations remain deterministic and restart-safe.

## Change-transition applicability

Blind target is greenfield. Migration/adoption from existing NAPMS is NOT_APPLICABLE until post-freeze comparison/transition work.

## External dependency applicability

Material runtime dependencies are PostgreSQL, OIDC/JWT validation and selected Go/runtime libraries. Dependency pinning/provenance/vulnerability verification belongs to Engineering Policy/Verification; package contents do not define product semantics.
