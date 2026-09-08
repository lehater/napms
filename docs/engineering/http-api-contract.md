# HTTP API contract — Web UI boundary

Status: `accepted through I10 Policy Operations Workspace`.

Date: 2026-09-09.

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

Neither `actorId` nor command `effectiveTime` is accepted from proposal or Rule-mutation request JSON. Rule mutation also never accepts caller-supplied governance scope; the authoritative Rule owns it.

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
  ],
  "ambiguousScopes": [
    { "scope": "scope-b" }
  ]
}
```

A scope with ambiguous effective authority is not presented as permitted. It is returned separately in `ambiguousScopes` so the UI can surface a fail-closed authority condition without granting access.

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

## Access Rule workspace

### GET /api/v1/access-rules

Purpose: list authoritative Access Rules visible through explicit `ReadAccessRule` authority.

Query:
- `page` — optional, default 1;
- `pageSize` — optional bounded page size.

The runtime supplies actor identity and effective time. Authority Management discovers unambiguous effective `ReadAccessRule` scopes. Only Rules whose stored `RuleGovernanceScope` is in that permitted set are returned.

Success: `200`.

```json
{
  "items": [
    {
      "ruleId": "uuid",
      "semanticIdentity": {
        "sourceComponentDeploymentId": "uuid",
        "destinationComponentDeploymentId": "uuid",
        "dcsContractRevisionId": "uuid"
      },
      "governanceScope": "scope-a",
      "operationalState": "Active",
      "effectiveWindow": null,
      "decisionReference": "decision-ref"
    }
  ],
  "page": 1,
  "pageSize": 50,
  "hasMore": false,
  "ambiguousScopes": []
}
```

Ambiguous scopes are fail-closed and never contribute Rule rows.

### GET /api/v1/access-rules/{ruleId}

Purpose: inspect one authoritative Rule.

Backend loads the Rule and evaluates `ReadAccessRule` against its stored governance scope before returning Rule data. It separately evaluates `SetRuleOperationalState` to expose action admission.

Success: `200` with:
- complete Rule identity/state/effective-window/decision data;
- proposal provenance;
- operational-state and EffectiveWindow business history;
- `capabilities.setOperationalState = Permitted | Denied | Unknown`.

Read permission does not imply mutation permission.

### PATCH /api/v1/access-rules/{ruleId}/operational-state

Purpose: execute the existing `SetRuleOperationalState` application command.

Request:

```json
{
  "targetState": "Inactive"
}
```

The request does not accept `actorId`, governance scope or effective time. Backend uses authenticated session actor, runtime time and the Rule's stored governance scope.

Outcomes:
- `Updated` -> `200` with updated Rule;
- `AlreadyInRequestedState` -> `200`, no accepted transition/audit;
- Rule not found -> `404 RuleNotFound`;
- authority denied -> `403 AuthorityDenied`;
- authority unknown -> `409 AuthorityUnknown`;
- persistence failure/uncertain commit -> existing `503` mappings.

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
| incomplete/stale/correlation-failed export snapshot | 409 | `SnapshotIncomplete` |
| normalized export invariant/codec failure | 500 | `NormalizationFailed` |
| unexpected defect | 500 | `InternalError` |

The semantic code remains the stable identity; HTTP status is transport behavior.

## EffectiveWindow mutation

### PATCH /api/v1/access-rules/{ruleId}/effective-window

Purpose: execute the existing `SetRuleEffectiveWindow` application command.

Request to set/change:

```json
{
  "window": {
    "start": "2026-09-10T08:00:00+00:00",
    "end": "2026-09-10T18:00:00+00:00"
  }
}
```

Request to clear:

```json
{
  "window": null
}
```

Rules:
- start/end must be offset-aware;
- `start < end`;
- backend supplies authenticated actor and mutation effective time;
- backend loads the Rule and uses its stored governance scope for `SetRuleEffectiveWindow`;
- request JSON cannot supply trusted actor, mutation time or governance scope;
- `Updated` and `AlreadyInRequestedWindow` return `200`;
- denied/unknown/not-found/persistence outcomes use existing safe mappings.

## Policy view scope discovery

### GET /api/v1/policy-views/scopes

Purpose: discover governance scopes with unambiguous effective `ReadEffectiveDesiredPolicy` authority for the authenticated actor at runtime time.

Success:

```json
{
  "scopes": [{"scope": "scope-a"}],
  "ambiguousScopes": [{"scope": "scope-b"}]
}
```

Ambiguous scopes remain fail-closed and are never presented as permitted.

## Effective Desired Policy JSON

### GET /api/v1/effective-desired-policy

Query:
- `scope` — required RuleGovernanceScope;
- `asOf` — required offset-aware RFC 3339 instant.

Purpose: execute the existing authorized `SelectEffectiveDesiredPolicy` application query.

Success:

```json
{
  "scope": "scope-a",
  "asOf": "2026-09-10T12:00:00+00:00",
  "authorityReference": "authority-ref",
  "rules": []
}
```

An authorized empty selection is `200` with `rules: []`. Denied/unknown authority returns no policy data.

## Normalized policy JSON

### GET /api/v1/normalized-policy

Purpose: execute the accepted authorized effective-policy -> coherent snapshot -> normalized vendor-neutral export chain.

Query:
- `scope` — one Rule Governance Scope;
- `asOf` — required RFC 3339 timestamp with explicit timezone offset.

Authenticated session identity supplies `actor_id` for `ReadEffectiveDesiredPolicy`.

Success: `200`.

```json
{
  "scope": "scope-a",
  "asOf": "2026-09-08T12:00:00+00:00",
  "authorityReference": "authority-ref",
  "rows": [
    {
      "ruleId": "uuid",
      "semanticIdentity": {
        "sourceComponentDeploymentId": "uuid",
        "destinationComponentDeploymentId": "uuid",
        "dcsContractRevisionId": "uuid"
      },
      "decisionReference": "decision-ref-or-null",
      "governanceScope": "scope-a",
      "operationalState": "Active",
      "effectiveWindow": null,
      "snapshotAsOf": "2026-09-08T12:00:00+00:00",
      "readAuthorityReference": "authority-ref",
      "source": {
        "resourceReference": "resource-ref",
        "endpointReference": "endpoint-ref",
        "technicalAddress": "198.51.100.10",
        "factReference": "fact-ref",
        "validityReference": "validity-ref",
        "provenanceReference": "provenance-ref"
      },
      "destination": {
        "resourceReference": "resource-ref",
        "endpointReference": "endpoint-ref",
        "technicalAddress": "203.0.113.20",
        "factReference": "fact-ref",
        "validityReference": "validity-ref",
        "provenanceReference": "provenance-ref"
      },
      "traffic": {
        "protocol": "tcp",
        "sourcePorts": {"kind": "Any"},
        "destinationPorts": {
          "kind": "Ranges",
          "ranges": [{"first": 443, "last": 443}]
        },
        "serviceReference": "https"
      },
      "applicationCommunicationCatalogue": {
        "factReference": "acc-fact",
        "validityReference": "acc-validity",
        "provenanceReference": "acc-provenance"
      }
    }
  ]
}
```

Rules:
- `Any`, `NotApplicable` and `Ranges` remain distinct JSON values;
- ranges remain inclusive ranges and are never expanded into individual ports;
- Rule/decision/Authority/ACC/RC provenance required by the normalized row is preserved;
- an authorized empty effective policy returns `200` with `rows: []`;
- incomplete/stale/mismatched snapshot data returns no partial rows and fails closed as `409 SnapshotIncomplete` with safe structured diagnostics;
- normalization invariant/codec failure returns no rows and a generic `500 NormalizationFailed`.

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

## Selected HTTP adapter

The I8 HTTP adapter uses FastAPI as an outer transport framework. FastAPI/Pydantic types remain confined to `napms.runtime`; Domain/Application stay framework-independent.

For the explicitly bounded `local-dev` runtime, the concrete Connectivity Decision adapter returns `Allowed` for every proposal that has already passed Authority and ACC structural validation, with decision reference `local-dev:allowed`. This is a test/development seam only; it does not model approval/policy logic and is rejected outside `local-dev` composition.

## Deferred HTTP surfaces

Not part of the first vertical slice:
- approval/review routes;
- persistent Access Request CRUD;
- generic ACC/RC/Authority administration;

- CSV/XLSX;
- device/provider execution.
