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

No command updates two domain owners in one transaction.

### SubmitAccessRequest

1. resolve active Need and exact InteractionRevision;
2. resolve source/destination Deployments and confirm their ComponentRefs match Interaction direction;
3. admission-check submit action;
4. call Access Policy SubmitAccessRequest with immutable references/provenance;
5. commit Access Policy transaction.

Validation reads do not transfer ownership; Access Policy persists stable references/provenance, not copies of mutable Resource address data.

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

### MaterializeCurrentPolicy(asOf)

Input: logical `asOf`; optional selection/filter must not change semantic meaning.

Algorithm:
1. read all PolicyRules effective at `asOf`;
2. for each Rule resolve exact InteractionRevision and source/destination Deployments;
3. resolve each Deployment's Resource and all current ResourceEndpoints valid at `asOf`;
4. require at least one trustworthy addressed endpoint on each side; missing/ambiguous required realization creates an unresolved item;
5. expand each InteractionRevision traffic clause over source/destination endpoint combinations, preserving HostAddress/Prefix form;
6. emit normalized rows carrying RuleRef, NeedRef, decision provenance, InteractionRevisionRef, DeploymentRefs, ResourceRefs and relevant realization provenance;
7. if any selected/effective Rule is unresolved, return overall status UNRESOLVED plus diagnostics/partial rows; partial rows are not a successful export;
8. otherwise return COMPLETE with one coherent logical snapshot.

## Consistency semantics

- Commands use one owning aggregate transaction and optimistic version checks.
- Cross-context validation is precondition checking, not a distributed transaction.
- If an upstream reference becomes invalid after a request/rule is accepted, historical reference remains resolvable; current materialization may become UNRESOLVED rather than silently rebinding.
- Policy materialization is read-only and must observe a coherent logical snapshot. Architecture/Data Design must provide snapshot semantics sufficient to avoid mixing incompatible points in time.
- Idempotency is required for retried permission recording/materialization and SHOULD be available for externally retried create commands via request idempotency key; exact transport representation belongs to Interface Design.

## Synchronous/asynchronous applicability

All current MVP commands/queries can be synchronous. No source requirement needs asynchronous messaging/eventual completion. Domain history/audit facts may be emitted as post-commit events for diagnostics/integration, but no accepted behavior depends on asynchronous delivery.

## Error classes exposed downstream

- NOT_FOUND / INVALID_REFERENCE
- VALIDATION_REJECTED
- UNAUTHORIZED / FORBIDDEN / AUTHORITY_UNKNOWN
- CONFLICT_STALE_VERSION
- DECISION_ALREADY_FINAL
- UNRESOLVED_MATERIALIZATION
- DEPENDENCY_UNAVAILABLE
- INTERNAL_FAILURE

Interface Design owns external representation while preserving these meanings.
