# Backend HTTP/JSON contract

Status: ACCEPTED after Coding-Agent Challenge 02 repairs

## Boundary-wide rules

Protocol: HTTPS + JSON, UTF-8.  
Version prefix: `/v1`.  
Authentication: OIDC bearer token.  
Time representation: RFC 3339 UTC timestamps.  
Identifiers: opaque strings; clients must not parse identifier structure.  
JSON field naming: lower camel case.

### JSON decoding

- request bodies are JSON objects unless an operation explicitly has no body;
- unknown JSON fields are rejected;
- missing required fields and explicit `null` are distinct;
- `null` is accepted only where explicitly stated;
- names/business-basis values marked required are non-empty after trimming;
- server-owned identity, version, provenance and timestamps cannot be supplied by clients;
- request bodies are bounded by startup-configured `NAPMS_HTTP_MAX_REQUEST_BODY_BYTES`; exceeding it -> `413 PAYLOAD_TOO_LARGE`; this is a transport-safety bound, not a domain cardinality limit.

### Correlation

A client may send `X-Correlation-Id` containing 1–64 characters from `[A-Za-z0-9._-]`. Invalid supplied values are `400 INVALID_INPUT`. If absent, the server generates one. Every response returns the effective `X-Correlation-Id`.

### Optimistic concurrency

An HTTP `ETag` is an opaque quoted token representing the current version of the aggregate named below. Clients never parse it.

Every mutation explicitly marked **If-Match** requires the current aggregate ETag:
- missing header -> `428 PRECONDITION_REQUIRED`;
- stale/non-matching ETag -> `409 STALE_VERSION`;
- success returns the new aggregate ETag.

Nested Resource mutations use the Resource ETag.  
Nested Application Component creation uses the Application ETag. Interaction revision publication uses the Interaction ETag.  
Nested Business Process / Connectivity Need mutations use the BusinessProcess ETag.  
AccessRequest decision uses the AccessRequest ETag.  
PolicyRule operational-state/effective-window and justification mutations use the PolicyRule ETag.

### Idempotency

`Idempotency-Key` is required for every operation explicitly marked **Idempotent-create**. It is an opaque non-empty value up to 128 UTF-8 bytes without control characters.

Idempotency scope is:

`authenticated principal subject + HTTP method + canonical route template + normalized path parameter values + key`.

The deterministic request fingerprint contains the same canonical target plus the normalized accepted JSON body. Correlation id and `If-Match` are not part of the fingerprint.

For an operation that requires both Idempotency-Key and If-Match, processing order is normative:

1. authenticate and authorize the current caller;
2. strictly decode/validate the target and request body enough to compute the canonical fingerprint;
3. inspect the idempotency record;
4. if the same key/fingerprint already committed, replay the original committed status/body/Location/ETag **before** checking the now-current aggregate ETag;
5. if the same scoped key has a different fingerprint, return `409 IDEMPOTENCY_CONFLICT`;
6. only for a NEW idempotency record, evaluate `If-Match` and execute the mutation.

This permits a client to safely retry a command with the original pre-mutation ETag after an uncertain response without receiving a false `STALE_VERSION`.

Committed replay returns:
- original semantic HTTP status;
- original response body;
- original `Location` when present;
- original response `ETag` when present;
- the correlation header for the current retry request.

Concurrent same-scoped-key handling is bounded:
- if the first transaction commits, the waiting identical request replays;
- if it rolls back, the waiter proceeds as NEW and then evaluates If-Match;
- if the first outcome cannot be established before configured request/DB timeout, or database availability prevents determination, return `503 DEPENDENCY_UNAVAILABLE`;
- do not return IDEMPOTENCY_CONFLICT merely because an identical command is still in progress.

An in-progress/unknown outcome never fabricates success. Idempotency is required for state-creating POSTs, permission-decision finalization and justification attachment. Read-only policy materialization does not use an idempotency key.

### Success conventions

- create -> `201 Created`, `Location` for the created resource, canonical response body;
- successful state mutation -> `200 OK`, canonical updated response body;
- read -> `200 OK`;
- policy materialization -> `200 OK` for both `COMPLETE` and `UNRESOLVED`; `UNRESOLVED` is a successfully computed non-complete application result, not an HTTP failure.

### Problem response

HTTP failures use `application/problem+json`:

- `code`: stable machine code;
- `detail`: safe human explanation;
- `correlationId`;
- optional `fieldErrors: [{field, code, detail}]`.

Stable mapping:

| HTTP | code |
| --- | --- |
| 400 | `INVALID_INPUT` |
| 401 | `AUTHENTICATION_REQUIRED` |
| 403 | `FORBIDDEN` |
| 404 | `NOT_FOUND` |
| 409 | `STALE_VERSION`, `DECISION_ALREADY_FINAL`, `IDEMPOTENCY_CONFLICT` |
| 413 | `PAYLOAD_TOO_LARGE` |
| 422 | `REFERENCE_INVALID`, `NEED_NOT_CURRENT`, `INTERACTION_MISMATCH`, `UNSUPPORTED_TRAFFIC_SEMANTICS`, `VALIDATION_REJECTED` |
| 428 | `PRECONDITION_REQUIRED` |
| 503 | `DEPENDENCY_UNAVAILABLE` |
| 500 | `INTERNAL_ERROR` |

Unexpected implementation detail, stack/schema names, credentials and tokens never appear in a Problem response.

## Shared representations

### AddressRealization

- host: `{"kind":"HOST","value":"192.0.2.10"}`
- prefix: `{"kind":"PREFIX","value":"192.0.2.0/24"}`

Validation/canonicalization:
- both IPv4 and IPv6 are supported;
- HOST accepts one IP literal only and rejects a CIDR suffix;
- PREFIX accepts CIDR only and requires all host bits already zero;
- a prefix with host bits set is `400 INVALID_INPUT`, never silently masked;
- IPv4 output uses canonical dotted-decimal text;
- IPv6 output uses canonical compressed lowercase text;
- IPv4-mapped IPv6 remains IPv6 and is not silently converted to IPv4;
- canonicalization must not broaden/narrow the represented address set.

### PortRange

`{"from":443,"to":443}`, inclusive bounds, `0 <= from <= to <= 65535`.

### TrafficClause

`{"ipProtocol":6,"sourcePorts":[],"destinationPorts":[{"from":443,"to":443}]}`.

- `ipProtocol` is required integer 0..255; the canonical boundary accepts no protocol-name aliases;
- TCP = 6 and UDP = 17 are the only port-bearing protocols in this MVP representation;
- for TCP/UDP, empty source/destination port arrays mean all ports on that side;
- for every other ipProtocol, both port arrays must be empty;
- attempting to provide ports for another protocol -> `422 UNSUPPORTED_TRAFFIC_SEMANTICS`;
- each range is inclusive and satisfies `0 <= from <= to <= 65535`;
- each input port list is normalized by sorting then merging overlapping/directly adjacent ranges;
- output always returns that canonical normalized range list;
- semantics requiring absent protocol-specific fields are rejected/unsupported, never approximated.

## Resource Description

### Site

`SiteView = {siteRef, name, description?}`.

- **Idempotent-create** `POST /v1/sites`
  - body: `{name, description?}`;
  - `201` SiteView.
- `GET /v1/sites/{siteRef}` -> SiteView.

Site records are immutable in the selected MVP.

### ResponsibilityGroup

`ResponsibilityGroupView = {groupRef, displayName, externalReference?}`.

- **Idempotent-create** `POST /v1/responsibility-groups`
  - body: `{displayName, externalReference?}`;
  - `201` ResponsibilityGroupView.
- `GET /v1/responsibility-groups/{groupRef}` -> ResponsibilityGroupView.

ResponsibilityGroup records are immutable in the selected MVP and carry no authorization semantics.

### Resource

`ResourceView` contains:

- `resourceRef`, `displayName`;
- `siteRef: string|null`;
- `endpointCount`;
- current `responsibilities: {owner:null|{assignmentRef,groupRef,effectiveFrom}, administrator:null|{assignmentRef,groupRef,effectiveFrom}}`.

Operations:

- **Idempotent-create** `POST /v1/resources`
  - body: `{displayName, siteRef?}`; supplied SiteRef must resolve;
  - `201` ResourceView + Resource ETag.
- `GET /v1/resources/{resourceRef}` -> ResourceView + Resource ETag.
- `GET /v1/resources/{resourceRef}/endpoints?cursor=&limit=`
  - returns `{items:[EndpointView],nextCursor:null|string}`;
  - `EndpointView={endpointRef,currentAddress:AddressRealization|null}`.
- `GET /v1/resources/{resourceRef}/history?cursor=&limit=`
  - returns `{items:[ResourceHistoryFact], nextCursor:null|string}`;
  - `limit` default 50, valid 1–200;
  - ResourceHistoryFact is one of:
    - `{kind:"ADDRESS", endpointRef, address:AddressRealization, effectiveFrom, effectiveTo:null|string, changedBySubject}`;
    - `{kind:"SITE", siteRef:null|string, effectiveFrom, effectiveTo:null|string}`;
    - `{kind:"RESPONSIBILITY", assignmentRef, role, groupRef, effectiveFrom, effectiveTo:null|string}`.
- **Idempotent-create + If-Match Resource** `POST /v1/resources/{resourceRef}/endpoints`
  - body: `{}`;
  - `201` `{endpointRef, currentAddress:null}` + new Resource ETag.
- `GET /v1/resources/{resourceRef}/endpoints/{endpointRef}`
  - returns `{endpointRef, currentAddress}`; `404` if endpoint does not belong to Resource.
- **If-Match Resource** `PUT /v1/resources/{resourceRef}/endpoints/{endpointRef}/address`
  - body is AddressRealization;
  - `200` endpoint view + new Resource ETag.
- **If-Match Resource** `DELETE /v1/resources/{resourceRef}/endpoints/{endpointRef}/address`
  - clears current address while preserving history;
  - `200` endpoint view with `currentAddress:null` + new Resource ETag.
- **If-Match Resource** `PUT /v1/resources/{resourceRef}/site`
  - body: `{siteRef:string|null}`; null clears current Site;
  - `200` ResourceView + new Resource ETag.
- **If-Match Resource** `PUT /v1/resources/{resourceRef}/responsibilities/{role}`
  - `role` is `OWNER|ADMINISTRATOR`;
  - body: `{groupRef}`;
  - supplied Group must resolve;
  - setting a different group closes the prior current assignment for that role and opens the new one atomically;
  - setting the already-current group is a semantic no-op with unchanged ETag;
  - `200` ResourceView + resulting Resource ETag.
- **If-Match Resource** `DELETE /v1/resources/{resourceRef}/responsibilities/{role}`
  - clears the current assignment for the role while preserving history;
  - clearing an already-empty role is a semantic no-op with unchanged ETag;
  - `200` ResourceView + resulting Resource ETag.

No Resource rename operation is part of the selected MVP.

## Application Communication

### Application / Component

`ApplicationView = {applicationRef, name, componentCount}`.

`ComponentView = {componentRef, applicationRef, name}`.

- **Idempotent-create** `POST /v1/applications`
  - body: `{name}`;
  - `201` ApplicationView + Application ETag.
- `GET /v1/applications/{applicationRef}` -> ApplicationView + Application ETag.
- `GET /v1/applications/{applicationRef}/components?cursor=&limit=`
  - returns `{items:[ComponentView],nextCursor:null|string}`.
- **Idempotent-create + If-Match Application** `POST /v1/applications/{applicationRef}/components`
  - body: `{name}`;
  - `201` ComponentView + new Application ETag.

Application/Component names are immutable in selected MVP.

### Interaction

`InteractionView = {interactionRef, sourceComponentRef, destinationComponentRef, purpose:null|string, revisionCount}`.

- **Idempotent-create** `POST /v1/interactions`
  - body: `{sourceComponentRef,destinationComponentRef,purpose?}`;
  - both ComponentRefs must resolve;
  - source and destination MAY belong to different Applications;
  - no Application aggregate is mutated;
  - `201` InteractionView + Interaction ETag.
- `GET /v1/interactions/{interactionRef}` -> InteractionView + Interaction ETag.
- `GET /v1/interactions/{interactionRef}/revisions?cursor=&limit=`
  - returns `{items:[{revisionRef,createdAt,createdBySubject}],nextCursor:null|string}`.
- **Idempotent-create + If-Match Interaction** `POST /v1/interactions/{interactionRef}/revisions`
  - body: `{trafficClauses:[TrafficClause,...]}`, non-empty;
  - `201` InteractionRevisionView + new Interaction ETag.
- `GET /v1/interaction-revisions/{revisionRef}` -> InteractionRevisionView.

`InteractionRevisionView = {revisionRef, interactionRef, trafficClauses, createdAt, createdBySubject}`.

Published Interaction subject/purpose and published revisions are immutable. A new traffic meaning is a new revision; a different source/destination subject is a different Interaction.

No blanket same-Application validation is permitted.

## Application Deployment

`DeploymentView = {deploymentRef, componentRef, resourceRef, createdAt}`.

- **Idempotent-create** `POST /v1/deployments`
  - body: `{componentRef, resourceRef}`;
  - both references must resolve;
  - `201` DeploymentView.
- `GET /v1/deployments/{deploymentRef}` -> DeploymentView.

No update/move/retire/delete operation and no independent deployment label are part of the selected MVP.

## Business Connectivity

`ResponsibleOrganization = {externalReference?:string, displayName:string}`.

`ProcessView = {processRef, name, description:null|string, responsibleOrganization:null|ResponsibleOrganization, needCount}`.

`NeedSummary = {needRef, processRef, interactionRef, participantComponentRef, businessBasis, status:"ACTIVE"|"RETIRED", createdAt, createdBySubject, retiredAt:null|string}`.

- **Idempotent-create** `POST /v1/processes`
  - body: `{name, description?, responsibleOrganization?}`;
  - `201` ProcessView + BusinessProcess ETag.
- `GET /v1/processes/{processRef}` -> ProcessView + BusinessProcess ETag.
- `GET /v1/processes/{processRef}/needs?cursor=&limit=`
  - returns `{items:[NeedSummary],nextCursor:null|string}`.
- **If-Match BusinessProcess** `PUT /v1/processes/{processRef}/responsible-organization`
  - body: `{responsibleOrganization:ResponsibleOrganization|null}`;
  - `200` ProcessView + new BusinessProcess ETag.
- **Idempotent-create + If-Match BusinessProcess** `POST /v1/processes/{processRef}/needs`
  - body: `{interactionRef, participantComponentRef, businessBasis}`;
  - InteractionRef must resolve;
  - participantComponentRef must equal that Interaction's sourceComponentRef or destinationComponentRef;
  - `201` NeedSummary + new BusinessProcess ETag.
- `GET /v1/needs/{needRef}` -> NeedSummary.
- **If-Match BusinessProcess** `POST /v1/processes/{processRef}/needs/{needRef}/retire`
  - body: `{}`;
  - need must belong to Process and be ACTIVE;
  - `200` retired NeedSummary + new BusinessProcess ETag.

Process description and Need business basis are immutable in the selected MVP after creation. Criticality/importance fields are intentionally absent.

## Access Policy

### AccessSubject

External representations identify the semantic access using:
`{sourceDeploymentRef, destinationDeploymentRef, interactionRevisionRef}`.

`needRef` is submission/business justification and is not part of semantic current-access identity.

### AccessRequest

`AccessRequestView` contains:
- `requestRef`;
- `subject:{sourceDeploymentRef,destinationDeploymentRef,interactionRevisionRef}`;
- `initialNeedRef`;
- `status:"PENDING"|"ALLOWED"|"DENIED"`;
- `submitterSubject`, `submittedAt`;
- when final: `externalDecisionRef:null|string`, `decidedBySubject`, `decidedAt`.

- **Idempotent-create** `POST /v1/access-requests`
  - body: `{sourceDeploymentRef,destinationDeploymentRef,interactionRevisionRef,needRef}`;
  - Need must be current and match the Interaction at the submission snapshot;
  - `201` pending AccessRequestView + AccessRequest ETag.
- `GET /v1/access-requests/{requestRef}` -> AccessRequestView + AccessRequest ETag.
- **Idempotent-create + If-Match AccessRequest** `POST /v1/access-requests/{requestRef}/decision`
  - body: `{result:"ALLOWED"|"DENIED", externalDecisionRef?}`;
  - `200` `{request:AccessRequestView, policyRule:PolicyRuleView|null}` + resulting AccessRequest ETag;
  - DENIED returns `policyRule:null`;
  - ALLOWED resolves/creates the one PolicyRule for AccessSubject, appends authorization evidence and attaches the request's initial Need if not already associated;
  - repeated ALLOWED for the same AccessSubject does not create a duplicate Rule and does not reset that Rule's operational state/effective window;
  - conflicting finalization of the same request -> `409 DECISION_ALREADY_FINAL`.

### PolicyRule representations

`EffectiveWindow = null | {effectiveFrom?:timestamp, effectiveUntil?:timestamp}`.

If non-null, at least one bound is required and when both exist `effectiveFrom < effectiveUntil`.

`AuthorizationEvidenceView = {accessRequestRef, submittedBySubject, submittedAt, initialNeedRef, externalDecisionRef:null|string, decidedBySubject, decidedAt}`.

`JustificationView = {needRef, processRef, interactionRef, participantComponentRef, businessBasis, needStatus:"ACTIVE"|"RETIRED", needCreatedAt, needCreatedBySubject, attachedAt, attachedBySubject, sourceAccessRequestRef:null|string}`.

`PolicyRuleView` contains:
- `policyRuleRef`;
- `subject:{sourceDeploymentRef,destinationDeploymentRef,interactionRevisionRef}`;
- `effectState:"ACTIVE"|"INACTIVE"`;
- `effectiveWindow:EffectiveWindow`;
- `authorizationEvidenceCount`;
- `justificationCount`;
- `currentJustificationCount`;
- `reconciliationFlags:["NO_CURRENT_BUSINESS_JUSTIFICATION"]|[]`;
- `createdAt`.

Ordering is deterministic:
- authorization evidence by `decidedAt`, then requestRef;
- justifications by `attachedAt`, then needRef.

Operations:

- `GET /v1/policy-rules/{policyRuleRef}`
  - resolves current Need status from Business Connectivity;
  - returns PolicyRuleView + PolicyRule ETag.

- `GET /v1/policy-rules/{policyRuleRef}/authorization-evidence?cursor=&limit=`
  - permission: `policy.read`;
  - returns `{items:[AuthorizationEvidenceView],nextCursor:null|string}`.

- `GET /v1/policy-rules/{policyRuleRef}/justifications?cursor=&limit=`
  - permission: `policy.read`;
  - resolves current Need status from Business Connectivity in one read snapshot;
  - returns `{items:[JustificationView],nextCursor:null|string}`.

- `GET /v1/policy-rules/{policyRuleRef}/history?cursor=&limit=`
  - permission: `policy.read`;
  - returns `{items:[PolicyRuleOperationalHistoryEvent], nextCursor:null|string}`;
  - `limit` default 50, valid 1–200;
  - `PolicyRuleOperationalHistoryEvent = {version, kind:"CREATED"|"OPERATIONAL_CHANGED", effectState, effectiveWindow, changedBySubject, changedAt}`;
  - first Rule creation produces `CREATED` with ACTIVE/unbounded state;
  - actual ACTIVE/INACTIVE or effectiveWindow changes produce `OPERATIONAL_CHANGED`;
  - semantic no-op operational requests produce no history event.

- **If-Match PolicyRule** `PUT /v1/policy-rules/{policyRuleRef}/operational`
  - body: `{effectState:"ACTIVE"|"INACTIVE", effectiveWindow:EffectiveWindow}`;
  - same state + same normalized window is a semantic no-op with unchanged ETag/history;
  - otherwise updates operational state/window atomically and returns updated PolicyRuleView + new ETag.

- **Idempotent-create + If-Match PolicyRule** `POST /v1/policy-rules/{policyRuleRef}/justifications`
  - body: `{needRef}`;
  - Need must be current at the mutation snapshot, its Interaction must match the Rule's Interaction, and participantComponentRef must be one of that Interaction's source/destination Components;
  - attaches business justification without changing permission or Rule identity;
  - attaching an already-associated Need is a semantic idempotent replay/result and does not create duplicate association/history;
  - `200` updated PolicyRuleView + resulting ETag.

No justification detach/delete operation exists in the MVP. Need retirement is owned by Business Connectivity and remains visible through `needStatus`.

A Rule with zero current Need justifications remains a Rule; it exposes reconciliation flag `NO_CURRENT_BUSINESS_JUSTIFICATION` and is not automatically deactivated.

## Current Policy Materialization

`POST /v1/policy-materializations`

- requires `policy.export`;
- read-only, no Idempotency-Key/If-Match;
- body is either:
  - `{}` — select all current PolicyRules; or
  - `{policyRuleRefs:[...]}` — explicit non-empty unique Rule subset; there is no domain count limit beyond the configured HTTP request-body safety bound;
- duplicate refs or an explicit empty list -> `400 INVALID_INPUT`;
- unknown RuleRef -> `422 REFERENCE_INVALID`;
- backend establishes `evaluationAt` from the coherent database read snapshot;
- computation success returns HTTP 200 for both COMPLETE and UNRESOLVED.
- server must complete the materialization preflight and determine COMPLETE/UNRESOLVED before committing the HTTP 200 response;
- dependency/runtime failure during preflight returns the normal 503/500 Problem response before any materialization body is committed;
- after successful preflight, rows/nonEffective/issues may be streamed from the same database snapshot;
- a transport/client cancellation after response commitment produces an incomplete HTTP body, which is not a valid successful export artifact.

Before resolving technical realization, each selected Rule is evaluated:
- INACTIVE -> non-effective, no output row and no realization completeness obligation;
- ACTIVE but outside effectiveWindow -> non-effective, same treatment;
- ACTIVE and inside window -> effective and must be resolved;
- zero current Need justifications does **not** make the Rule non-effective; it produces reconciliation flag `NO_CURRENT_BUSINESS_JUSTIFICATION`.

Response:
- `status:"COMPLETE"|"UNRESOLVED"`;
- `evaluationAt`;
- `selection:{mode:"ALL"|"EXPLICIT",selectedRuleCount}`;
- `ruleProvenance:[MaterializedRuleProvenance]`;
- `nonEffective:[{policyRuleRef, reason:"INACTIVE"|"OUTSIDE_EFFECTIVE_WINDOW"}]`;
- `rows:[NormalizedPolicyRow]`;
- `issues:[MaterializationIssue]`.

`MaterializedRuleProvenance` is emitted once per selected PolicyRule and contains:
- `policyRuleRef`;
- `subject:{sourceDeploymentRef,destinationDeploymentRef,interactionRevisionRef}`;
- `effectState`, `effectiveWindow`;
- `effectiveAtEvaluation:boolean`;
- all `authorizationEvidence:[AuthorizationEvidenceView,...]`;
- all `justifications:[JustificationView,...]` with current/retired Need status and participantComponentRef;
- `reconciliationFlags`.

This provenance is part of the export result itself and is available to a caller with `policy.export`; it does not require a second `policy.read` permission. It is emitted once per Rule to avoid repeating unbounded audit data in every technical row.

`NormalizedPolicyRow` contains:
- `policyRuleRef`;
- `interactionRevisionRef`;
- source: `{deploymentRef,resourceRef,endpointRef,address:AddressRealization,addressEffectiveFrom,addressChangedBySubject}`;
- destination: same shape;
- `ipProtocol`, `sourcePorts:[PortRange]`, `destinationPorts:[PortRange]`.

Independent PolicyRule provenance is never merged away even when two rows have equal technical effect.

`MaterializationIssue = {policyRuleRef, code, detail}`, where code is one of:
- `SOURCE_REALIZATION_MISSING`;
- `DESTINATION_REALIZATION_MISSING`;
- `REFERENCE_UNRESOLVABLE`.

Rules:
- COMPLETE requires no issue for any selected **effective** Rule;
- UNRESOLVED requires at least one issue;
- diagnostic rows returned with UNRESOLVED are not a successful export artifact;
- INACTIVE/out-of-window Rules never create realization issues;
- missing current Need alone never creates a MaterializationIssue;
- dependency/runtime failure preventing evaluation is `503 DEPENDENCY_UNAVAILABLE`, not UNRESOLVED;
- historical caller-selected `asOf` is not supported.

## Pagination and growing collections

All ordinary growing collection reads use the same page envelope:
`{items:[...],nextCursor:null|string}`.

Contract:
- `limit` default 50;
- valid `limit` range 1–200;
- cursor is opaque, query-specific and forward-only;
- malformed cursor or a cursor reused for a different route/parent/query -> `400 INVALID_INPUT`;
- each ordinary page is a coherent current read for that request; no cross-request historical/snapshot guarantee is promised across pages;
- no silent truncation;
- parent/current entity views expose scalar counts rather than unbounded child arrays.

Paginated surfaces:
- Resource endpoints;
- Resource history;
- Application Components;
- Interaction revisions;
- BusinessProcess Needs;
- PolicyRule AuthorizationEvidence;
- PolicyRule justifications;
- PolicyRule operational history.

Policy materialization is the export exception: `ruleProvenance`, `rows`, `nonEffective` and `issues` may be large and are emitted from one coherent snapshot in one HTTP response. Implementation may stream arrays/nested provenance arrays incrementally after preflight. Each Rule's complete permission/business provenance appears once in `ruleProvenance`; technical rows correlate by PolicyRuleRef. Paginated PolicyRule endpoints remain an independent read/audit surface, not a prerequisite for understanding an exported result.
