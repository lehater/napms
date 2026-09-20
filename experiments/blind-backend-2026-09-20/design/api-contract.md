# Backend HTTP/JSON contract

Status: ACCEPTED candidate

Protocol: HTTPS + JSON, UTF-8.  
Version prefix: `/v1`.  
Authentication: OIDC bearer token.  
Time: RFC 3339 UTC timestamps.  
Identifiers: opaque strings; clients must not parse them.  
Errors: `application/problem+json` with stable `code`, human `detail`, optional `fieldErrors`, and `correlationId`.

Mutation requests support `Idempotency-Key` where retry could otherwise duplicate an operation. Mutable aggregate updates require `If-Match` with current version/ETag.

## Resource Description

- `POST /v1/resources` — create Resource.
- `GET /v1/resources/{resourceRef}` — current Resource including current endpoints/site/responsibilities.
- `GET /v1/resources/{resourceRef}/history` — bounded history.
- `POST /v1/resources/{resourceRef}/endpoints` — add logical endpoint.
- `PUT /v1/resources/{resourceRef}/endpoints/{endpointRef}/address` — set HostAddress or Prefix.
- `DELETE /v1/resources/{resourceRef}/endpoints/{endpointRef}/address` — clear current address.
- `PUT /v1/resources/{resourceRef}/site`
- `POST /v1/resources/{resourceRef}/responsibilities`
- `DELETE /v1/resources/{resourceRef}/responsibilities/{assignmentRef}`

Address representation:
`{"kind":"HOST","value":"192.0.2.10"}` or `{"kind":"PREFIX","value":"192.0.2.0/24"}`.

## Application Communication

- `POST /v1/applications`
- `POST /v1/applications/{applicationRef}/components`
- `POST /v1/applications/{applicationRef}/interactions`
- `POST /v1/interactions/{interactionRef}/revisions` — publish immutable traffic revision.
- `GET /v1/interactions/{interactionRef}`
- `GET /v1/interaction-revisions/{revisionRef}`

Traffic clause:
`{"protocol":"TCP|UDP|ICMP|OTHER","destinationPorts":[{"from":443,"to":443}]}`; non-port protocol uses an empty port list when semantically valid.

## Application Deployment

- `POST /v1/deployments` with `componentRef`, `resourceRef`, label.
- `GET /v1/deployments/{deploymentRef}`
- `POST /v1/deployments/{deploymentRef}/retire`

## Business Connectivity

- `POST /v1/processes`
- `GET /v1/processes/{processRef}`
- `POST /v1/processes/{processRef}/needs` with `interactionRef`, business basis and optional explicit criticality fields.
- `GET /v1/needs/{needRef}`
- `POST /v1/needs/{needRef}/retire`

## Access Policy

- `POST /v1/access-requests`
  - body: sourceDeploymentRef, destinationDeploymentRef, interactionRevisionRef, needRef.
  - success: 201 with requestRef, PENDING status.
- `POST /v1/access-requests/{requestRef}/decision`
  - body: `result: ALLOWED|DENIED`, optional externalDecisionRef.
  - ALLOWED success returns request + policyRuleRef; DENIED returns final denied request.
- `GET /v1/access-requests/{requestRef}`
- `GET /v1/policy-rules/{policyRuleRef}`
- `PUT /v1/policy-rules/{policyRuleRef}/effect` with `ACTIVE|INACTIVE`.

## Policy Materialization

- `POST /v1/policy-materializations`
  - permission: `policy.export`;
  - body: `{"asOf":"..."}`.
  - response status field: `COMPLETE|UNRESOLVED`.
  - `COMPLETE` rows contain:
    - policyRuleRef, accessRequestRef, needRef, decisionRef/provenance;
    - interactionRevisionRef;
    - source/destination deploymentRef and resourceRef;
    - source/destination AddressRealization preserving HOST/PREFIX;
    - protocol and destination port/range semantics;
    - realization provenance/effective timestamps.
  - `UNRESOLVED` contains explicit issues per affected PolicyRule and may include diagnostic rows; clients must not treat diagnostic rows as complete policy.

## Stable failure codes

- `AUTHENTICATION_REQUIRED`
- `FORBIDDEN`
- `INVALID_INPUT`
- `NOT_FOUND`
- `REFERENCE_INVALID`
- `NEED_NOT_CURRENT`
- `INTERACTION_MISMATCH`
- `STALE_VERSION`
- `DECISION_ALREADY_FINAL`
- `IDEMPOTENCY_CONFLICT`
- `MATERIALIZATION_UNRESOLVED`
- `DEPENDENCY_UNAVAILABLE`
- `INTERNAL_ERROR`

4xx denotes caller/domain/admission outcomes; 409 is used for stale/conflicting/finalized/idempotency conflicts; 422 for semantic validation; 503 for required dependency unavailability; 500 for unexpected failure.

## Collection semantics

Any list/history endpoint must use opaque cursor pagination with server-bounded page size. Exact default/max values are implementation configuration unless an accepted capacity target later requires a contract value.
