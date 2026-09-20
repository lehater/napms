# Backend HTTP/JSON contract

Status: ACCEPTED candidate after Coding-Agent Challenge 01

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
- server-owned identity, version, provenance and timestamps cannot be supplied by clients.

### Correlation

A client may send `X-Correlation-Id` containing 1–64 characters from `[A-Za-z0-9._-]`. Invalid supplied values are `400 INVALID_INPUT`. If absent, the server generates one. Every response returns the effective `X-Correlation-Id`.

### Optimistic concurrency

An HTTP `ETag` is an opaque quoted token representing the current version of the aggregate named below. Clients never parse it.

Every mutation explicitly marked **If-Match** requires the current aggregate ETag:
- missing header -> `428 PRECONDITION_REQUIRED`;
- stale/non-matching ETag -> `409 STALE_VERSION`;
- success returns the new aggregate ETag.

Nested Resource mutations use the Resource ETag.  
Nested Application mutations use the Application ETag.  
Nested Business Process / Connectivity Need mutations use the BusinessProcess ETag.  
AccessRequest decision uses the AccessRequest ETag.  
PolicyRule effect mutation uses the PolicyRule ETag.

### Idempotency

`Idempotency-Key` is required for every operation explicitly marked **Idempotent-create**. It is an opaque non-empty value up to 128 UTF-8 bytes without control characters.

Scope is `authenticated-principal + operation + key`.

- first committed request stores request fingerprint and committed semantic result;
- same key + same fingerprint returns the original HTTP status/body/Location and current correlation header;
- same key + different fingerprint -> `409 IDEMPOTENCY_CONFLICT`;
- a key whose commit outcome is still unknown never fabricates success.

Idempotency is required for state-creating POSTs and the permission-decision command because ALLOWED can create a PolicyRule. Read-only policy materialization does not use an idempotency key.

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
| 422 | `REFERENCE_INVALID`, `NEED_NOT_CURRENT`, `INTERACTION_MISMATCH`, `UNSUPPORTED_TRAFFIC_SEMANTICS`, `VALIDATION_REJECTED` |
| 428 | `PRECONDITION_REQUIRED` |
| 503 | `DEPENDENCY_UNAVAILABLE` |
| 500 | `INTERNAL_ERROR` |

Unexpected implementation detail, stack/schema names, credentials and tokens never appear in a Problem response.

## Shared representations

### AddressRealization

- host: `{"kind":"HOST","value":"192.0.2.10"}`
- prefix: `{"kind":"PREFIX","value":"192.0.2.0/24"}`

The backend returns normalized address/prefix text.

### PortRange

`{"from":443,"to":443}`, inclusive bounds, `0 <= from <= to <= 65535`.

### TrafficClause

`{"protocol":"TCP","sourcePorts":[],"destinationPorts":[{"from":443,"to":443}]}`.

- `protocol` is a normalized protocol name or numeric protocol identifier;
- empty source/destination port arrays mean unrestricted ports for that side where ports are applicable;
- port ranges are rejected for protocols whose accepted semantics do not use ports;
- protocol-specific semantics that cannot be represented by this contract are rejected with `UNSUPPORTED_TRAFFIC_SEMANTICS`, never approximated.

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
- `endpoints: [{endpointRef, currentAddress: AddressRealization|null}]`;
- current `responsibilities: [{assignmentRef, role: OWNER|ADMINISTRATOR, groupRef, effectiveFrom}]`.

Operations:

- **Idempotent-create** `POST /v1/resources`
  - body: `{displayName, siteRef?}`; supplied SiteRef must resolve;
  - `201` ResourceView + Resource ETag.
- `GET /v1/resources/{resourceRef}` -> ResourceView + Resource ETag.
- `GET /v1/resources/{resourceRef}/history?cursor=&limit=`
  - returns `{items:[ResourceHistoryFact], nextCursor:null|string}`;
  - `limit` default 50, valid 1–200;
  - ResourceHistoryFact is one of:
    - `{kind:"ADDRESS", endpointRef, address:AddressRealization, effectiveFrom, effectiveTo:null|string, provenance}`;
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
- **Idempotent-create + If-Match Resource** `POST /v1/resources/{resourceRef}/responsibilities`
  - body: `{role:"OWNER"|"ADMINISTRATOR", groupRef}`;
  - `201` current responsibility assignment + new Resource ETag.
- **If-Match Resource** `DELETE /v1/resources/{resourceRef}/responsibilities/{assignmentRef}`
  - ends the current assignment; already-ended or foreign assignment -> `422 VALIDATION_REJECTED`;
  - `200` ResourceView + new Resource ETag.

No Resource rename operation is part of the selected MVP.

## Application Communication

### Application

`ApplicationView = {applicationRef, name, components:[ComponentView], interactions:[InteractionSummary]}`.

`ComponentView = {componentRef, applicationRef, name}`.

`InteractionSummary = {interactionRef, applicationRef, sourceComponentRef, destinationComponentRef, purpose:null|string, revisionRefs:[...]}`.

- **Idempotent-create** `POST /v1/applications`
  - body: `{name}`;
  - `201` ApplicationView + Application ETag.
- `GET /v1/applications/{applicationRef}` -> ApplicationView + Application ETag.
- **Idempotent-create + If-Match Application** `POST /v1/applications/{applicationRef}/components`
  - body: `{name}`;
  - `201` ComponentView + new Application ETag.
- **Idempotent-create + If-Match Application** `POST /v1/applications/{applicationRef}/interactions`
  - body: `{sourceComponentRef, destinationComponentRef, purpose?}`;
  - both Components must belong to the named Application;
  - `201` InteractionSummary + new Application ETag.
- `GET /v1/interactions/{interactionRef}` -> InteractionSummary.
- **Idempotent-create + If-Match Application** `POST /v1/applications/{applicationRef}/interactions/{interactionRef}/revisions`
  - body: `{trafficClauses:[TrafficClause,...]}`, non-empty;
  - `201` InteractionRevisionView + new Application ETag.
- `GET /v1/interaction-revisions/{revisionRef}` -> InteractionRevisionView.

`InteractionRevisionView = {revisionRef, interactionRef, trafficClauses, createdAt, provenance}`.

Published revisions are immutable.

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

`ProcessView = {processRef, name, description:null|string, responsibleOrganization:null|ResponsibleOrganization, needs:[NeedSummary]}`.

`NeedSummary = {needRef, processRef, interactionRef, businessBasis, status:"ACTIVE"|"RETIRED", createdAt, retiredAt:null|string}`.

- **Idempotent-create** `POST /v1/processes`
  - body: `{name, description?, responsibleOrganization?}`;
  - `201` ProcessView + BusinessProcess ETag.
- `GET /v1/processes/{processRef}` -> ProcessView + BusinessProcess ETag.
- **If-Match BusinessProcess** `PUT /v1/processes/{processRef}/responsible-organization`
  - body: `{responsibleOrganization:ResponsibleOrganization|null}`;
  - `200` ProcessView + new BusinessProcess ETag.
- **Idempotent-create + If-Match BusinessProcess** `POST /v1/processes/{processRef}/needs`
  - body: `{interactionRef, businessBasis}`;
  - InteractionRef must resolve;
  - `201` NeedSummary + new BusinessProcess ETag.
- `GET /v1/needs/{needRef}` -> NeedSummary.
- **If-Match BusinessProcess** `POST /v1/processes/{processRef}/needs/{needRef}/retire`
  - body: `{}`;
  - need must belong to Process and be ACTIVE;
  - `200` retired NeedSummary + new BusinessProcess ETag.

Process description and Need business basis are immutable in the selected MVP after creation. Criticality/importance fields are intentionally absent.

## Access Policy

### AccessRequest

`AccessRequestView` contains:

- `requestRef`;
- `sourceDeploymentRef`, `destinationDeploymentRef`;
- `interactionRevisionRef`, `needRef`;
- `status:"PENDING"|"ALLOWED"|"DENIED"`;
- `submitterSubject`, `submittedAt`;
- when final: `decisionRef:null|string`, `decidedBySubject`, `decidedAt`.

- **Idempotent-create** `POST /v1/access-requests`
  - body: `{sourceDeploymentRef, destinationDeploymentRef, interactionRevisionRef, needRef}`;
  - `201` pending AccessRequestView + AccessRequest ETag.
- `GET /v1/access-requests/{requestRef}` -> AccessRequestView + AccessRequest ETag.
- **Idempotent-create + If-Match AccessRequest** `POST /v1/access-requests/{requestRef}/decision`
  - body: `{result:"ALLOWED"|"DENIED", externalDecisionRef?}`;
  - `200` `{request:AccessRequestView, policyRule:PolicyRuleView|null}` + new AccessRequest ETag;
  - ALLOWED returns the established/resolved PolicyRule; DENIED returns null;
  - conflicting second final decision -> `409 DECISION_ALREADY_FINAL`; exact idempotent replay is handled by Idempotency-Key.

### PolicyRule

`PolicyRuleView` contains:

- `policyRuleRef`, `accessRequestRef`;
- `sourceDeploymentRef`, `destinationDeploymentRef`;
- `interactionRevisionRef`, `needRef`, `decisionRef:null|string`;
- `effectState:"ACTIVE"|"INACTIVE"`;
- `createdAt`.

- `GET /v1/policy-rules/{policyRuleRef}` -> PolicyRuleView + PolicyRule ETag.
- **If-Match PolicyRule** `PUT /v1/policy-rules/{policyRuleRef}/effect`
  - body: `{effectState:"ACTIVE"|"INACTIVE"}`;
  - setting the already-current state is a semantic no-op and returns `200` with the unchanged ETag;
  - otherwise returns updated PolicyRuleView + new ETag.

## Current Policy Materialization

`POST /v1/policy-materializations`

- no request body;
- requires `policy.export`;
- read-only, no Idempotency-Key/If-Match;
- backend establishes `evaluationAt` from the coherent database read snapshot;
- always `200` when computation itself succeeds.

Response:

- `status:"COMPLETE"|"UNRESOLVED"`;
- `evaluationAt`;
- `rows:[NormalizedPolicyRow]`;
- `issues:[MaterializationIssue]`.

`NormalizedPolicyRow` contains:

- `policyRuleRef`, `accessRequestRef`, `needRef`;
- `decisionRef:null|string`, `interactionRevisionRef`;
- source: `{deploymentRef, resourceRef, endpointRef, address:AddressRealization, realizationEffectiveFrom, realizationProvenance}`;
- destination: same shape;
- `protocol`, `sourcePorts:[PortRange]`, `destinationPorts:[PortRange]`.

Independent Rule provenance is never merged away even when two rows have equal technical effect.

`MaterializationIssue = {policyRuleRef, code, detail}`, where code is one of:

- `SOURCE_REALIZATION_MISSING`;
- `DESTINATION_REALIZATION_MISSING`;
- `REFERENCE_UNRESOLVABLE`.

Rules:

- `COMPLETE` requires `issues=[]` and complete rows for every current ACTIVE Rule;
- `UNRESOLVED` requires at least one issue;
- rows returned with `UNRESOLVED` are diagnostic only and are never a successful export artifact;
- dependency/runtime failure that prevents evaluation is `503 DEPENDENCY_UNAVAILABLE`, not `UNRESOLVED`;
- historical caller-selected `asOf` is not supported.

## Pagination

The only selected-MVP paginated surface is Resource history. Cursors are opaque, stable only for forward traversal of that query, and cannot be interpreted by clients.
