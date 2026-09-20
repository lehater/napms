# Blind backend application design

Status: ACCEPTED after Source Corpus amendment 02

## Responsibility

Compose owner-domain contracts into supported backend commands/queries. Application Design owns orchestration, atomicity across Access Policy-owned records, policy selection/materialization and reconciliation projection; it does not re-own peer domain truth.

## Common command semantics

For every protected mutation:

1. authenticate and authorize the exact Security permission or scoped authority required by the operation;
2. strictly validate Interface request/header preconditions;
3. for Idempotent-create, perform idempotency replay/conflict lookup before evaluating current If-Match on a NEW command;
4. resolve required peer facts through public owner ports in the command transaction snapshot;
5. mutate exactly one semantic owner's state;
6. commit owner state/history + idempotency result atomically when applicable;
7. return accepted result/version or explicit error.

No command writes two semantic owners.

Aggregate concurrency owners:
- Resource owns Endpoint/address/Site/OWNER/ADMINISTRATOR changes;
- Application owns Component creation;
- Interaction is an independent Application Communication aggregate: creation validates referenced Components read-only; Interaction owns revision publication;
- BusinessProcess owns responsible organization/criticality/Need create/retire;
- AccessRequest owns final decision;
- PolicyRule owns operational/window and justification-association mutation.

## Catalogue/application curation

- Site, ResponsibilityGroup and ComponentDeployment are immutable after registration in selected MVP.
- Resource role set is singular per role; replacing OWNER/ADMINISTRATOR closes prior assignment atomically.
- Application/Component records are immutable after creation except Application aggregate version advances for Component creation.
- Interaction source/destination/purpose are immutable; published InteractionRevisions are immutable.
- Cross-Application Interaction is valid when both ComponentRefs resolve and directed communication semantics are explicit; no same-Application check is permitted.
- BusinessProcess name/description and Need business basis are immutable; responsible organization and criticalityLabel use BusinessProcess-version mutations.
- same accepted state-set request is a semantic no-op where explicitly defined by owner contract.

## SubmitAccessRequest

Inside one write transaction:

1. idempotency NEW/replay decision for the concrete target command;
2. establish server-owned `admissionAt` from the write transaction clock;
3. through the transaction-bound Business Connectivity port, acquire the current Need FOR SHARE-equivalent validation lock and resolve BusinessProcess/Interaction/participant facts; the lock remains until AccessRequest commit;
4. resolve exact InteractionRevision;
5. resolve source/destination Deployments, their Resources and each Resource AuthorityScopeRef; verify Component direction;
6. verify Need Interaction matches revision's Interaction and Need participantComponentRef equals that Interaction's source or destination Component;
7. deduplicate source/destination AuthorityScopeRefs and require effective scoped `access.request` authority for each at admissionAt; collect immutable RequestAuthorityEvidence for the exact grants used;
8. create immutable `AccessSubject(sourceDeploymentRef,destinationDeploymentRef,interactionRevisionRef)`;
9. persist AccessRequest with initialNeedRef, validatedBusinessProcessVersion, actor/admissionAt and RequestAuthorityEvidence;
10. commit idempotency result.

Need is required submission justification but is not part of AccessSubject.

## RecordPermissionDecision

Inside one Access Policy transaction:

1. authorize `access.decide`;
2. resolve idempotency replay/conflict before NEW-command AccessRequest ETag check;
3. load PENDING request under expected version;
4. record final ALLOWED or DENIED decision;
5. if DENIED: commit request + idempotency, no Rule mutation;
6. if ALLOWED:
   - resolve/create PolicyRule by unique AccessSubject;
   - when newly created, initialize ACTIVE with unbounded effective window and initial operational history;
   - append AuthorizationEvidence for this AccessRequest;
   - attach initialNeedRef justification if absent;
   - when Rule already existed, serialize on that Rule aggregate, advance Rule version exactly once for the new evidence/association set, and do not append operational history;
   - do **not** reset existing Rule state/window when Rule already existed;
7. commit request, Rule/evidence/association and idempotency atomically.

Concurrent ALLOWED requests for same AccessSubject converge on one PolicyRule using Data Design's unique subject resolution.

## ManagePolicyRuleOperationalState

1. authorize `access.manage`;
2. require current Rule ETag;
3. normalize `effectState + EffectiveWindow`;
4. same normalized values -> no-op, unchanged ETag/history;
5. otherwise update state/window, increment Rule version and append operational history.

No new permission decision is required.

## AttachPolicyRuleJustification

Inside one transaction:

1. authorize `access.manage`;
2. idempotency replay/conflict before NEW-command Rule ETag check;
3. load Rule under expected version;
4. acquire the Business Connectivity current-Need FOR SHARE-equivalent validation lock in the Access Policy write transaction; require ACTIVE and retain the lock through Rule-association commit;
5. require Need Interaction to equal the Interaction owning Rule.interactionRevisionRef and participantComponentRef to be one of that Interaction's participants;
6. if Need association already exists, return semantic no-op/replay result;
7. append JustificationAssociation and increment Rule version;
8. do not add AuthorizationEvidence and do not change effect state/window;
9. commit association + idempotency.

Need retirement later does not mutate Access Policy.

## ReadPolicyRule

Compose:
- Access Policy Rule/evidence/justification refs/history;
- Business Connectivity current/historical Need facts.

For each associated Need return current/retired status, Process/business basis, participantComponentRef, createdAt and createdBySubject. If no associated Need is current, add `NO_CURRENT_BUSINESS_JUSTIFICATION`.

This flag is diagnostic/reconciliation semantics, not revocation/effectiveness.

## MaterializeCurrentPolicy

Input selection:
- absent Rule list -> all current Rules;
- explicit unique non-empty PolicyRuleRef set -> exactly that subset; no semantic count limit exists beyond Interface request-body safety;
- unknown selected Rule -> REFERENCE_INVALID.

One read-only REPEATABLE READ (or stronger) snapshot is opened and database-owned `evaluationAt` is recorded. Export authority is evaluated against that exact time. The same snapshot remains open through both phases below.

### Phase 1 — preflight before HTTP response commitment

1. resolve selected Rule cores through bounded pages for ALL mode or bounded/chunked lookup of the explicit Rule set supplied within the configured request-body limit;
2. evaluate each Rule:
   - INACTIVE -> non-effective;
   - ACTIVE outside effectiveWindow -> non-effective;
   - ACTIVE inside/unbounded window -> effective;
3. page AuthorizationEvidence and justification associations for **every selected Rule**; resolve every referenced Need as current or retired in bounded batches and construct the complete per-Rule export provenance projection; an accepted provenance reference that cannot be resolved is REFERENCE_UNRESOLVABLE and makes the materialization UNRESOLVED regardless of Rule effectiveness;
4. for every selected Rule resolve source/destination Deployments, Resources and Resource AuthorityScopeRefs sufficiently to derive the selected domain-policy scope; deduplicate scope refs and require effective scoped `policy.export` authority for every one at evaluationAt; record ExportAuthorityEvidence;
5. for every selected effective Rule resolve exact InteractionRevision and current addressed Endpoints in bounded/chunked reads;
6. determine every stable MaterializationIssue and nonEffective reason; provenance-reference issues may belong to any selected Rule, while technical-realization issues belong only to selected effective Rules;
7. verify required DB/dependency reads complete successfully;
8. compute final application status COMPLETE only when every selected Rule has complete permission/business provenance and every selected effective Rule has complete technical realization; otherwise UNRESOLVED;
9. do not build the full normalized row set in memory;
10. do not commit/write HTTP response status, headers or body yet.

If any dependency/runtime error prevents preflight completion, abort the snapshot and propagate DEPENDENCY_UNAVAILABLE/INTERNAL failure so Interface Design can return 503/500 before response commitment.

### Phase 2 — emit from the same snapshot

After preflight succeeded:

1. repeat the bounded selected-Rule/fact traversal in the still-open snapshot;
2. stream the already-determined HTTP-200 application result incrementally;
3. emit nonEffective/issues consistently with Phase 1;
4. emit top-level ExportAuthorityEvidence for the authenticated export actor and every distinct selected AuthorityScopeRef, then stream one complete MaterializedRuleProvenance record per selected Rule, including all authorization evidence, all participant-attributed Need justifications/currentness and reconciliation flags;
5. for effective resolvable Rules expand source endpoints × destination endpoints × TrafficClauses and stream normalized rows;
6. each technical row carries PolicyRuleRef, InteractionRevisionRef and explicit Resource-address actor/time facts; its business/permission explanation is the corresponding ruleProvenance record in the same export;
7. paginated policy.read endpoints remain an independent audit/read convenience, not a requirement to explain the export.

The two phases must be deterministic over the same snapshot. Phase 2 must not discover a semantic result different from Phase 1.

If client cancellation/transport failure occurs after HTTP response commitment, the response is truncated/incomplete and is not a valid policy export artifact. The server must not fabricate a closing COMPLETE body/event after the stream failed.

Zero current Need is not a missing provenance reference: associated RETIRED Needs remain resolvable historical provenance, and zero currently ACTIVE Needs yields NO_CURRENT_BUSINESS_JUSTIFICATION without making the Rule non-effective.

Historical/time-travel export is outside MVP.


## Consistency semantics

- every command writes one semantic owner only;
- ordinary owner writes use READ COMMITTED; mutable current-Need validation uses an owner-provided peer read lock held through the Access Policy commit, while peer tables remain read-only to Access Policy;
- historical refs/evidence/justification associations and explicit actor/time provenance are never silently rebound or erased;
- no automatic DB mutation retry; client retry uses Interface idempotency;
- idempotency replay precedes NEW-command optimistic precondition evaluation;
- ordinary paginated collection reads are coherent per request but do not promise a multi-request snapshot; policy materialization alone keeps one snapshot while paging/chunking all internal reads;
- current evaluation time is server-owned; historical caller-selected export is outside MVP.

## Synchronous/asynchronous applicability

All selected MVP commands/queries are synchronous. No message broker/eventual completion is required. Post-commit diagnostics are non-authoritative.

## Application errors/outcomes

Errors:
- NOT_FOUND / INVALID_REFERENCE
- VALIDATION_REJECTED
- NEED_NOT_CURRENT
- INTERACTION_MISMATCH
- UNSUPPORTED_TRAFFIC_SEMANTICS
- UNAUTHORIZED / FORBIDDEN
- CONFLICT_STALE_VERSION
- IDEMPOTENCY_CONFLICT
- DECISION_ALREADY_FINAL
- DEPENDENCY_UNAVAILABLE
- INTERNAL_FAILURE

Materialization `UNRESOLVED` is a normal application result with stable issues, not an error.
