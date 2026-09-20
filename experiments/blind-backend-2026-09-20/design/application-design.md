# Blind backend application design

Status: ACCEPTED after Source Corpus amendment 02

## Responsibility

Compose owner-domain contracts into supported backend commands/queries. Application Design owns orchestration, atomicity across Access Policy-owned records, policy selection/materialization and reconciliation projection; it does not re-own peer domain truth.

## Common command semantics

For every protected mutation:

1. authenticate and authorize exact Security permission;
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
- BusinessProcess owns responsible organization/Need create/retire;
- AccessRequest owns final decision;
- PolicyRule owns operational/window and justification-association mutation.

## Catalogue/application curation

- Site, ResponsibilityGroup and ComponentDeployment are immutable after registration in selected MVP.
- Resource role set is singular per role; replacing OWNER/ADMINISTRATOR closes prior assignment atomically.
- Application/Component records are immutable after creation except Application aggregate version advances for Component creation.
- Interaction source/destination/purpose are immutable; published InteractionRevisions are immutable.
- Cross-Application Interaction is valid when both ComponentRefs resolve and directed communication semantics are explicit; no same-Application check is permitted.
- BusinessProcess name/description and Need business basis are immutable.
- same accepted state-set request is a semantic no-op where explicitly defined by owner contract.

## SubmitAccessRequest

Inside one write transaction:

1. idempotency NEW/replay decision for the concrete target command;
2. resolve current Need and BusinessProcess version;
3. resolve exact InteractionRevision;
4. resolve source/destination Deployments and verify Component direction;
5. verify Need Interaction matches revision's Interaction and Need participantComponentRef equals that Interaction's source or destination Component;
6. create immutable `AccessSubject(sourceDeploymentRef,destinationDeploymentRef,interactionRevisionRef)`;
7. persist AccessRequest with initialNeedRef, validatedBusinessProcessVersion, actor/time;
8. commit idempotency result.

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
4. resolve Need as CURRENT through Business Connectivity in the same snapshot;
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
- explicit unique non-empty PolicyRuleRef set -> exactly that domain-policy subset;
- unknown selected Rule -> REFERENCE_INVALID.

Within one coherent read snapshot:

1. record server-owned `evaluationAt`;
2. resolve selected Rules;
3. evaluate operational effectiveness:
   - INACTIVE -> non-effective;
   - ACTIVE outside effectiveWindow -> non-effective;
   - ACTIVE inside/unbounded window -> effective;
4. for every selected Rule resolve current/retired Need justification status and reconciliation flags regardless of effectiveness;
5. skip technical realization completeness checks for non-effective Rules;
6. for every effective Rule resolve exact InteractionRevision, Deployments, Resources and all current addressed Endpoints;
7. expand source endpoints × destination endpoints × TrafficClauses exactly;
8. preserve Rule identity, all authorization evidence, all business justifications/currentness/participantComponent attribution and explicit actor/time facts, reconciliation flags, InteractionRevision createdAt/createdBySubject and Resource-address effectiveFrom/changedBySubject;
9. missing source/destination realization or accepted reference -> stable MaterializationIssue;
10. return COMPLETE iff every selected effective Rule resolves fully, otherwise UNRESOLVED;
11. dependency/runtime failure preventing evaluation propagates as failure and is never converted into UNRESOLVED.

Zero current Need is not a MaterializationIssue and does not make an otherwise effective Rule non-effective.

## Consistency semantics

- every command writes one semantic owner only;
- cross-owner validation reads may share owner write transaction snapshot while peers remain read-only;
- historical refs/evidence/justification associations and explicit actor/time provenance are never silently rebound or erased;
- no automatic DB mutation retry; client retry uses Interface idempotency;
- idempotency replay precedes NEW-command optimistic precondition evaluation;
- policy materialization uses one snapshot including Business Connectivity Need currentness;
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
