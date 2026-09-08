# HTTP API contract — I8 first Web UI boundary

Status: `accepted I8 minimum use-case contract`.

Date: 2026-09-08.

## Purpose

Define the smallest HTTP JSON surface required by the accepted first Web UI journey without turning NAPMS into database CRUD or redefining Domain/Application semantics.

The HTTP adapter translates public transport DTOs to existing/new application use cases. Domain/Application do not import HTTP/framework types.

## Trust boundary

Trusted runtime facts:
- `actor_id` comes only from the authenticated server-side session;
- command `effective_time` comes from the runtime clock;
- correlation/request ID comes from the runtime after validation/generation.

Untrusted request data:
- login/password credentials before authentication;
- requested governance scope;
- source/destination Component Deployment IDs;
- DCS revision ID;
- filters/pagination.

Neither `actorId` nor command `effectiveTime` is accepted from proposal request JSON.

## Public conventions

- base path: `/api/v1`;
- JSON fields: camelCase;
- timestamps: RFC 3339 offset-aware strings;
- UUIDs: canonical string representation;
- correlation header: `X-Correlation-ID`;
- expected semantic outcomes retain stable symbolic codes;
- framework/vendor exception names and raw dependency payloads are never public.

## Authentication/session operations

### POST /api/v1/session

Purpose: authenticate local/test login + password and create an authenticated session.

Request:

```json
{
  "login": "local-user",
  "password": "..."
}
```

Success: `200`.

```json
{
  "actor": {
    "actorId": "actor-1",
    "login": "local-user"
  }
}
```

Failure: generic `401 AuthenticationFailed`; response does not reveal whether login or password was wrong.

### GET /api/v1/session

Purpose: bootstrap/restore the current browser session.

Success: `200` with the authenticated actor DTO.

Unauthenticated/expired: `401`.

### DELETE /api/v1/session

Purpose: invalidate the current session.

Success: `204`.

## Proposal composition support

These are use-case-oriented query operations, not ACC/Authority CRUD.

### GET /api/v1/access-rule-proposals/scopes

Purpose: discover governance scopes in which the authenticated actor currently has unambiguous `ProposeConnectivity` authority.

The runtime supplies the effective time.

Success: `200`.

```json
{
  "scopes": [
    { "scope": "scope-a" }
  ]
}
```

A scope with ambiguous effective authority is not presented as permitted. The application query may report an `AuthorityUnknown` condition rather than silently treating ambiguity as permission.

### GET /api/v1/access-rule-proposals/interactions

Purpose: discover structurally valid proposal identities after a governance scope is selected.

Query:
- `scope` — required;
- `page` — optional, default 1;
- `pageSize` — optional bounded page size.

Before returning catalogue data, backend re-checks `ProposeConnectivity` for the authenticated actor, selected scope and runtime effective time.

Success: `200`.

```json
{
  "items": [
    {
      "sourceComponentDeploymentId": "uuid",
      "destinationComponentDeploymentId": "uuid",
      "dcsContractRevisionId": "uuid"
    }
  ],
  "page": 1,
  "pageSize": 50,
  "hasMore": false
}
```

The first I8 catalogue model has no accepted human-readable deployment/application names. The API must not invent them. UI may display shortened identifiers until catalogue naming semantics are added explicitly.

## Submit proposal

### POST /api/v1/access-rule-proposals

Purpose: execute the existing `SubmitAccessRuleProposal -> MaterializeAllowedAccessRule` use case.

Request:

```json
{
  "authorityScope": "scope-a",
  "sourceComponentDeploymentId": "uuid",
  "destinationComponentDeploymentId": "uuid",
  "dcsContractRevisionId": "uuid"
}
```

The HTTP adapter adds trusted `actor_id` from session and trusted `effective_time` from runtime clock.

### Materialized

HTTP `201`.

```json
{
  "outcome": "Materialized",
  "rule": {
    "ruleId": "uuid",
    "semanticIdentity": {
      "sourceComponentDeploymentId": "uuid",
      "destinationComponentDeploymentId": "uuid",
      "dcsContractRevisionId": "uuid"
    },
    "governanceScope": "scope-a",
    "operationalState": "Active",
    "effectiveWindow": null,
    "decisionReference": "decision-ref-or-null"
  }
}
```

### Resolved

HTTP `200` with the same Rule DTO and `outcome = "Resolved"`.

Repeated Allowed materialization is shown as the same authoritative Rule, not as another persistent request.

### NotAllowed

HTTP `200`.

```json
{
  "outcome": "NotAllowed",
  "rule": null
}
```

`NotAllowed` is a normal business result and never becomes `403`.

## Error envelope and transport mapping

Public errors use:

```json
{
  "error": {
    "code": "AuthorityDenied",
    "message": "Safe presentation message",
    "correlationId": "..."
  }
}
```

Minimum mapping for the first slice:

| Application/runtime result | HTTP | Public code |
|---|---:|---|
| unauthenticated/expired session | 401 | `AuthenticationRequired` |
| failed login | 401 | `AuthenticationFailed` |
| `AuthorityDenied` | 403 | `AuthorityDenied` |
| `AuthorityUnknown` | 409 | `AuthorityUnknown` |
| `InteractionInvalid` | 422 | `InteractionInvalid` |
| `InteractionUnknown` | 409 | `InteractionUnknown` |
| `DecisionUnknown` | 503 | `DecisionUnknown` |
| `DecisionSubjectMismatch` | 502 | `DecisionSubjectMismatch` |
| persistence execution unavailable | 503 | `PersistenceUnavailable` |
| persistence commit outcome uncertain | 503 | `PersistenceOutcomeUnknown` |
| malformed request/UUID/schema | 400/422 | transport validation code |
| unexpected defect | 500 | `InternalError` |

The semantic code remains the stable identity; HTTP status is transport behavior.

## Health/readiness

Outside the versioned business API:

- `GET /health/live` — process is alive; no dependency traversal;
- `GET /health/ready` — runtime is configured and required PostgreSQL dependencies are reachable enough to admit requests.

Health responses contain no DSN/secret/raw dependency payload.

## Correlation

For every request:
1. accept `X-Correlation-ID` only after bounded safe validation, otherwise generate one;
2. echo it as `X-Correlation-ID` in the response;
3. attach it to the one structured completion event;
4. include it in safe public error envelopes.

Correlation identity never replaces Rule/domain identity.

## Deferred HTTP surfaces

Not part of the first vertical slice:
- approval/review routes;
- persistent Access Request CRUD;
- generic ACC/RC/Authority administration;
- Access Rule list/details until an admitted read-authority use case is defined;
- Active/Inactive and EffectiveWindow mutation routes until the corresponding UI slice is taken;
- Effective Desired Policy and Normalized Policy routes until UI-3;
- CSV/XLSX;
- device/provider execution.
