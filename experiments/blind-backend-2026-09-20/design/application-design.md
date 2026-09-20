# Blind backend application design

Status: ACCEPTED candidate

## Responsibility

Application Design composes domain-owner contracts into supported backend commands/queries. It owns orchestration and materialization semantics, not domain truth.

## Command flows

### Catalogue/application curation

Each mutation:
1. authenticates/admission-checks the actor according to Security Architecture;
2. resolves required upstream references through owner ports;
3. invokes exactly one owning aggregate mutation;
4. commits one owner transaction;
5. returns owner identity/version or explicit rejection/conflict.

No command writes two domain owners in one transaction.

### SubmitAccessRequest

1. open one database transaction whose snapshot is shared by the validation read ports and the Access Policy write port;
2. resolve active Need and exact InteractionRevision in that transaction snapshot;
3. resolve source/destination Deployments and confirm their ComponentRefs match Interaction direction;
4. admission-check submit action;
5. call Access Policy SubmitAccessRequest with immutable references/provenance, including the owner versions/revision identities validated;
6. commit only Access Policy-owned state plus idempotency evidence.

This is not a distributed/cross-owner write transaction: peer contexts are read-only participants. The accepted meaning of "Need is current at submission" is the Need state observed in the same database transaction snapshot that commits the AccessRequest.

### RecordPermissionDecision

1. authenticate/admission-check the decision-recording action;
2. locate exact pending AccessRequest;
3. accept external decision result ALLOWED or DENIED with immutable decision reference/provenance;
4. atomically store final decision; when ALLOWED establish the idempotent PolicyRule in the same Access Policy transaction;
5. return RuleRef for ALLOWED or explicit denied outcome.

The mechanism/reasons that produce the decision remain outside current NAPMS ownership.

### SetPolicyRuleEffect

1. admission-check policy-effect mutation;
2. optimistic-concurrency check PolicyRule version;
3. change ACTIVE/INACTIVE preserving decision provenance;
4. commit one Access Policy transaction.

## Query/materialization flows

### MaterializeCurrentPolicy

Input: no historical `asOf` is accepted from the caller. The backend establishes `evaluationAt` when the read transaction begins.

Algorithm:
1. open one read-only coherent database snapshot and record `evaluationAt`;
2. read all current ACTIVE PolicyRules from that snapshot;
3. for each Rule resolve exact InteractionRevision and source/destination Deployments;
4. resolve each Deployment's Resource and every endpoint whose address is current in the same snapshot;
5. require at least one trustworthy addressed endpoint on each side; missing/ambiguous required realization creates an unresolved item;
6. expand each InteractionRevision traffic clause over source/destination endpoint combinations, preserving HostAddress/Prefix and source/destination port-range meaning;
7. emit normalized rows carrying RuleRef, NeedRef, decision provenance, InteractionRevisionRef, DeploymentRefs, ResourceRefs and relevant realization provenance;
8. if any effective Rule is unresolved, return overall status UNRESOLVED plus diagnostics/partial rows; partial rows are not a successful export;
9. otherwise return COMPLETE with one coherent logical snapshot and `evaluationAt`.

Historical/time-travel materialization is explicitly outside this MVP.

## Consistency semantics

- Commands use one owning aggregate transaction and optimistic version checks.
- Cross-context validation reads may share the owning write transaction snapshot when one physical database provides the required consistency; peer schemas remain read-only.
- If an upstream reference later changes or becomes unavailable, historical reference remains resolvable; current materialization may become UNRESOLVED rather than silently rebinding.
- Policy materialization is read-only and must observe a coherent logical snapshot. Architecture/Data Design must prevent mixing incompatible current points in time.
- Idempotency is required for retried permission recording and externally retried create commands where duplicate creation would be material; exact transport representation belongs to Interface Design.

## Synchronous/asynchronous applicability

All current MVP commands/queries can be synchronous. No source requirement needs asynchronous messaging/eventual completion. Domain history/audit facts may be emitted as post-commit events for diagnostics/integration, but no accepted behavior depends on asynchronous delivery.

## Error classes exposed downstream

- NOT_FOUND / INVALID_REFERENCE
- VALIDATION_REJECTED
- UNSUPPORTED_TRAFFIC_SEMANTICS
- UNAUTHORIZED / FORBIDDEN / AUTHORITY_UNKNOWN
- CONFLICT_STALE_VERSION
- DECISION_ALREADY_FINAL
- UNRESOLVED_MATERIALIZATION
- DEPENDENCY_UNAVAILABLE
- INTERNAL_FAILURE

Interface Design owns external representation while preserving these meanings.
