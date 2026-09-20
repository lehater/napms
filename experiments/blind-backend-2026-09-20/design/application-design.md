# Blind backend application design

Status: ACCEPTED candidate after Coding-Agent Challenge 01

## Responsibility

Application Design composes domain-owner contracts into supported backend commands/queries. It owns orchestration and materialization semantics, not domain truth or HTTP representation.

## Common command semantics

For every protected mutation:

1. authenticate and admission-check the exact Security Architecture permission;
2. validate Interface-owned idempotency/concurrency preconditions before invoking domain mutation;
3. resolve required cross-owner references only through public owner ports;
4. invoke exactly one semantic owner's aggregate mutation;
5. commit owner state, required history and idempotency evidence atomically where the operation is Interface-marked Idempotent-create;
6. return owner result/version or an explicit accepted rejection/conflict.

No command writes two semantic owners in one transaction.

Nested mutations use the version of their owning aggregate:
- Resource owns Endpoint/Site-assignment/responsibility changes;
- Application owns Component/Interaction/revision creation;
- BusinessProcess owns organization/Need creation/retirement;
- AccessRequest owns final decision state;
- PolicyRule owns effect state.

A semantic no-op explicitly accepted upstream does not create a new version/history entry merely because a request was received.

## Catalogue/application curation

- Site and ResponsibilityGroup are immutable after registration.
- Resource display name is immutable; Resource mutation is limited to Endpoint/address, Site assignment and responsibility assignment/end.
- Application children and published revisions are created under Application optimistic concurrency; published revision content is immutable.
- ComponentDeployment is immutable after registration.
- BusinessProcess name/description and Need business basis are immutable; only responsible organization and Need lifecycle mutate.

Interface-marked create commands use the shared idempotency contract; an idempotent replay returns the original semantic creation rather than invoking a second domain mutation.

## SubmitAccessRequest

1. open one database transaction whose snapshot is shared by peer validation reads and the Access Policy write;
2. resolve the ACTIVE Need and its owning BusinessProcess version in that snapshot;
3. resolve exact immutable InteractionRevision;
4. resolve source/destination Deployments and confirm their ComponentRefs match Interaction direction;
5. admission-check `access.request`;
6. create immutable AccessRequest subject/provenance including validated BusinessProcess version;
7. persist AccessRequest plus Idempotency-Key record atomically.

The accepted meaning of “Need is current at submission” is the Need state observed in the same database transaction snapshot that commits the AccessRequest. Later Need retirement does not rewrite the accepted request/decision/rule.

## RecordPermissionDecision

1. admission-check `access.decide`;
2. require current AccessRequest version and accepted Idempotency-Key;
3. locate the exact PENDING AccessRequest;
4. accept external ALLOWED or DENIED plus optional opaque external decision reference;
5. atomically store the final decision;
6. for ALLOWED, establish exactly one PolicyRule for that AccessRequest in the same transaction;
7. store idempotency result in that transaction.

Outcomes:
- exact same idempotency key/fingerprint -> replay original result;
- different fingerprint for same key -> IDEMPOTENCY_CONFLICT;
- a different command attempts to finalize an already-final request -> DECISION_ALREADY_FINAL;
- no intermediate ALLOWED-without-Rule state is observable.

The mechanism/reasons producing the permission decision remain outside NAPMS ownership.

## SetPolicyRuleEffect

1. admission-check `access.manage`;
2. require current PolicyRule version;
3. if requested state equals current state, return the unchanged Rule/version and append no history;
4. otherwise change ACTIVE/INACTIVE preserving immutable request/decision subject/provenance;
5. commit Rule plus state-history row atomically.

## MaterializeCurrentPolicy

Input: no caller-selected historical time. The backend establishes `evaluationAt` when one read transaction begins.

Algorithm:

1. open one read-only coherent database snapshot and record `evaluationAt`;
2. read all current ACTIVE PolicyRules;
3. for each Rule resolve exact InteractionRevision and immutable source/destination Deployments;
4. resolve each Deployment Resource and every current addressed Endpoint in the same snapshot;
5. if source has no current address, add `SOURCE_REALIZATION_MISSING`;
6. if destination has no current address, add `DESTINATION_REALIZATION_MISSING`;
7. if an accepted referenced fact cannot be resolved, add `REFERENCE_UNRESOLVABLE`;
8. for fully resolvable Rules, expand every source endpoint × destination endpoint × TrafficClause combination while preserving HOST/PREFIX and exact source/destination port semantics;
9. emit rows with independent Rule/Need/decision/revision/deployment/resource/endpoint provenance;
10. return `COMPLETE` only when no Rule has an issue; otherwise return `UNRESOLVED` with diagnostic rows/issues.

`UNRESOLVED` is an application result, not an exception/failure. A database/runtime dependency failure that prevents evaluation is a dependency failure and maps through Interface Design to HTTP 503.

Historical/time-travel materialization is outside this MVP.

## Consistency semantics

- one owning aggregate version controls every mutable command as listed above;
- cross-owner validation reads may share the owning write transaction snapshot while peer schemas remain read-only;
- immutable external references are never silently rebound;
- accepted Resource/Need history preserves facts after later change;
- policy materialization uses one shared read snapshot; no mixed current points in time;
- no automatic database mutation retry exists; Interface idempotency is the recovery mechanism for client retry/unknown commit outcome.

## Synchronous/asynchronous applicability

All current MVP commands/queries are synchronous. No accepted behavior requires asynchronous completion, message broker or eventual consistency.

Post-commit diagnostic signals may be emitted, but:
- they are not domain truth;
- no product outcome depends on their delivery.

## Application outcome/error classes

Domain/admission/conflict failures preserved for Interface mapping:

- NOT_FOUND / INVALID_REFERENCE
- VALIDATION_REJECTED
- UNSUPPORTED_TRAFFIC_SEMANTICS
- UNAUTHORIZED / FORBIDDEN
- CONFLICT_STALE_VERSION
- IDEMPOTENCY_CONFLICT
- DECISION_ALREADY_FINAL
- DEPENDENCY_UNAVAILABLE
- INTERNAL_FAILURE

Policy materialization additionally has the non-error application outcome `UNRESOLVED` with stable issue codes owned by Interface/Application design.

Interface Design owns HTTP/status/body/header representation without reinterpreting these meanings.
