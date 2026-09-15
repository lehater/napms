# HTTP API contract — Web UI boundary

Status: `accepted through I16B Connectivity Decision Runtime and Workflow`.

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

## Scoped Connectivity Inventory

I16A adds the resource-centric owner workspace API.

The API is a read/application composition. It does not create a Connectivity aggregate or duplicate Requirement/Decision/Rule truth.

### GET /api/v1/connectivity/scopes

Purpose: discover Responsibility Scopes the authenticated actor may use as local workspace context through `ReadScopedConnectivity`.

Query:
- `asOf` — required offset-aware RFC 3339 instant.

Success:

```json
{
  "asOf": "2026-09-09T12:00:00+00:00",
  "scopes": [{"scope": "payments-prod"}],
  "ambiguousScopes": []
}
```

Rules:
- actor identity comes from the authenticated session;
- the same explicit `asOf` is used by Authority Management;
- ambiguous scopes are fail-closed and are not selectable;
- unavailable authority dependency -> `503 ScopedConnectivityUnavailable`.

### GET /api/v1/connectivity

Purpose: return the resource-centric Scoped Connectivity Inventory for one selected Responsibility Scope.

Query:
- `scope` — required selected Responsibility Scope;
- `asOf` — required offset-aware RFC 3339 instant;
- `page` — Resource page, default 1;
- `pageSize` — bounded Resource page size, default 50, maximum 100;
- optional bounded `search`.

Top-level paging is over local Resources. Resource groups are not split across top-level pages.

Success:

```json
{
  "scope": "payments-prod",
  "asOf": "2026-09-09T12:00:00+00:00",
  "items": [
    {
      "resource": {
        "resourceReference": "resource-local",
        "realizationState": "Resolved",
        "endpoints": [
          {
            "endpointReference": "resource-local:endpoint",
            "technicalAddress": "10.10.10.10"
          }
        ]
      },
      "componentsKnown": true,
      "components": [
        {
          "componentDeploymentId": "uuid",
          "displayName": "Checkout Frontend",
          "relationshipsKnown": true,
          "relationships": [
            {
              "semanticIdentity": {
                "sourceComponentDeploymentId": "uuid",
                "destinationComponentDeploymentId": "uuid",
                "dcsContractRevisionId": "uuid"
              },
              "direction": "Outgoing",
              "remoteComponent": {
                "componentDeploymentId": "uuid",
                "displayName": "Orders API"
              },
              "dcsDisplayName": "HTTPS Orders",
              "accessSummary": "tcp 443",
              "remoteResourcesKnown": true,
              "remoteResources": [
                {
                  "resourceReference": "resource-remote",
                  "realizationState": "Resolved",
                  "endpoints": []
                }
              ],
              "need": {
                "current": "Required",
                "historicalOnly": false,
                "coverage": "Covered"
              },
              "decision": {
                "state": "Unknown"
              },
              "policy": {
                "ruleExists": "Yes",
                "operationalState": "Active",
                "effectiveAtAsOf": "Yes"
              }
            }
          ]
        }
      ]
    }
  ],
  "page": 1,
  "pageSize": 50,
  "hasMore": false,
  "partial": true
}
```

The overview exposes only the accepted coarse contract:
- no Requirement ID/justification/history/provenance;
- no Decision ID/reason/evidence/provenance;
- no Rule ID/governance scope/window/provenance/audit;
- protected details remain behind their independent read authorities.

`Decision.state` uses:
- `Allowed`;
- `NotAllowed`;
- `NoFinalDecision`;
- `Unknown`.

Only Allowed/NotAllowed are Connectivity Decision business outcomes. `NoFinalDecision` and `Unknown` are read/application results.

The runtime obtains this dimension from the durable Connectivity Decision bounded context. Authoritative absence is `NoFinalDecision`; ambiguous effective truth is `Unknown`. If Decision enrichment alone is unavailable, the base inventory may remain available with Decision `Unknown` and `partial=true`; protected Decision detail is never inferred from the coarse summary.

Authority mappings:
- selected scope denied -> `403 AuthorityDenied`;
- selected scope unknown/ambiguous -> `409 AuthorityUnknown`;
- base inventory dependency unavailable -> `503 ScopedConnectivityUnavailable`;
- enrichment uncertainty that can be isolated to one dimension -> `200` with that dimension `Unknown` and `partial=true`.

One logical `asOf` is used for scope authority, Resource Scope Affiliation, Resource realization, DeploymentResourceBinding, Requirement currentness/coverage, Decision and Rule effectiveness.

## Connectivity Decision

I16B exposes direct authorized final-Decision operations. These are use-case APIs, not Decision-table CRUD, and they introduce no Pending/approval lifecycle.

### GET /api/v1/connectivity-decisions/scopes

Discovers unambiguous effective `DecideConnectivity` scopes for the authenticated actor at runtime time.

Success returns `scopes` plus fail-closed `ambiguousScopes`.

### GET /api/v1/connectivity-decisions/interactions

Query:
- `scope` required;
- `page`, `pageSize`;
- optional bounded `search`.

The backend re-checks `DecideConnectivity` for the selected scope/time before returning ACC-backed exact directed interaction subjects.

### POST /api/v1/connectivity-decisions

Records one final immutable `Allowed | NotAllowed` Decision.

Request supplies:
- `authorityScope`;
- exact Source/Destination Component Deployment IDs;
- immutable DCS revision ID;
- final outcome;
- `validFrom` and optional `validUntil`;
- non-empty reason code/text;
- optional evidence references;
- optional `supersedesDecisionId`.

The request cannot establish actor ID, decision action time or authority provenance. Those are resolved by the authenticated runtime.

Outcomes:
- `Recorded` -> 201;
- idempotently equivalent current Decision `Resolved` -> 200;
- authority denied -> 403;
- authority unknown/ambiguous -> 409;
- invalid subject -> 422;
- unknown subject -> 409;
- current ambiguity, required/invalid supersession or concurrent current conflict -> 409;
- persistence unavailable/commit-outcome unknown -> safe 503 class.

A differing current Decision must be explicitly superseded; an existing Decision is never edited in place.

### GET /api/v1/connectivity-decisions

Returns a paged list only from unambiguous effective `ReadConnectivityDecision` scopes. Ambiguous read scopes are reported separately and do not grant visibility.

### GET /api/v1/connectivity-decisions/{decisionId}

Returns the authoritative Decision plus read-authority reference when independently admitted by `ReadConnectivityDecision` for the Decision's stored governance scope.

Decision detail may expose final outcome, exact subject, reason, evidence, validity, deciding provenance and supersession history. These protected details are not implied by `ReadScopedConnectivity`.

## Connectivity Requirements

I13 adds a dedicated use-case API. Connectivity Requirement existence is not connectivity authorization and has no implicit Access Policy side effect.

### GET /api/v1/connectivity-requirements/scopes

Discovers unambiguous effective `DeclareConnectivityRequirement` scopes for the authenticated actor at runtime time.

Success:
```json
{
  "scopes": [{"scope": "scope-a"}],
  "ambiguousScopes": []
}
```

### GET /api/v1/connectivity-requirements/interactions

Query:
- `scope` required;
- `page`, `pageSize`;
- optional bounded `search`.

The backend evaluates `DeclareConnectivityRequirement` for the requested scope/time before returning ACC-backed exact interactions.

Returned identity remains Source Deployment + Destination Deployment + immutable DCS revision. Optional I12 catalogue presentation metadata may accompany each item.

### POST /api/v1/connectivity-requirements

Request:
```json
{
  "authorityScope": "scope-a",
  "dependentComponentDeploymentId": "uuid",
  "sourceComponentDeploymentId": "uuid",
  "destinationComponentDeploymentId": "uuid",
  "dcsContractRevisionId": "uuid",
  "applicability": {"kind": "Ongoing"},
  "justification": "Orders are required for checkout."
}
```

Absolute applicability:
```json
{
  "kind": "AbsoluteWindow",
  "start": "2026-09-10T08:00:00+00:00",
  "end": "2026-09-10T18:00:00+00:00"
}
```

Request JSON cannot supply actor ID, effective business action time, Requirement ID, lifecycle state, version, authority reference or catalogue provenance.

Outcomes:
- `Declared` -> 201;
- `Resolved` existing Active semantic need -> 200;
- authority denied -> 403;
- authority unknown -> 409;
- invalid interaction/dependent/input -> 422;
- interaction unknown -> 409;
- persistence/commit uncertainty -> existing safe 503 class.

Declaration does not call Connectivity Decision and does not create an Access Rule.

### GET /api/v1/connectivity-requirements

Authorized paged workspace list.

The backend discovers effective `ReadConnectivityRequirement` scopes and returns only Requirements from unambiguous permitted stored governance scopes.

### GET /api/v1/connectivity-requirements/{requirementId}

Loads the authoritative Requirement then checks `ReadConnectivityRequirement` against its stored governance scope.

Success may expose independent capabilities:
- `setApplicability`;
- `setJustification`;
- `retire`;

each as `Permitted | Denied | Unknown`. Read authority does not imply mutation authority.

### PATCH /api/v1/connectivity-requirements/{requirementId}/applicability

Request:
```json
{"applicability": {"kind": "Ongoing"}}
```

or the AbsoluteWindow shape above.

Backend supplies session actor/runtime time and evaluates `SetConnectivityRequirementApplicability` against the stored Requirement governance scope.

### PATCH /api/v1/connectivity-requirements/{requirementId}/justification

Request:
```json
{"justification": "Updated business reason."}
```

Backend evaluates `SetConnectivityRequirementJustification` against stored scope.

### POST /api/v1/connectivity-requirements/{requirementId}/retirement

No business fields are accepted from the client.

Backend evaluates `RetireConnectivityRequirement` against stored scope and performs only `Active -> Retired`.

### Requirement DTO

Minimum authoritative fields:
- `requirementId`;
- `governanceScope`;
- `dependentComponentDeploymentId`;
- exact `requiredInteraction`;
- `applicability`;
- `justification`;
- `lifecycleState`;
- declaration provenance;
- accepted applicability/justification/lifecycle histories;
- aggregate `version`;
- optional catalogue presentation block.

Aggregate version is concurrency metadata, not domain identity/lifecycle and not caller authority.

## Requirement-to-Policy Alignment

I14 adds read-only Requirement-centric coverage queries. Alignment is recomputed and has no persistence/API mutation surface.

### GET /api/v1/connectivity-requirements/alignment

Query:
- `asOf` — required offset-aware RFC 3339 instant;
- `page`, `pageSize`.

Returns statuses for the same authorized Requirement page admitted by `ReadConnectivityRequirement`.

Success:
```json
{
  "asOf": "2026-09-09T12:00:00+00:00",
  "items": [
    {
      "requirementId": "uuid",
      "status": "Covered",
      "semanticIdentity": {
        "sourceComponentDeploymentId": "uuid",
        "destinationComponentDeploymentId": "uuid",
        "dcsContractRevisionId": "uuid"
      }
    }
  ],
  "page": 1,
  "pageSize": 50,
  "hasMore": false,
  "ambiguousScopes": []
}
```

Status vocabulary:
- `Covered`;
- `Uncovered`;
- `NotCurrent`;
- `Unknown`.

`Denied` is not an I14 alignment status.

Rules:
- one explicit `asOf` is used for Requirement applicability and Access Rule effective contribution;
- exact semantic identity equality is required;
- Requirement/Rule governance scopes need not match;
- Requirement read authority admits the derived status;
- response exposes no Rule ID, Rule scope, decision/proposal provenance, Rule state/window or Rule audit;
- ambiguous Requirement read scopes remain fail-closed;
- AP persistence/dependency uncertainty returns per-item `Unknown`, not false `Uncovered`.

### GET /api/v1/connectivity-requirements/{requirementId}/alignment

Query:
- `asOf` — required offset-aware RFC 3339 instant.

Loads/authorizes the Requirement, then derives exact effective-policy coverage.

Success:
```json
{
  "requirementId": "uuid",
  "asOf": "2026-09-09T12:00:00+00:00",
  "status": "Uncovered",
  "semanticIdentity": {
    "sourceComponentDeploymentId": "uuid",
    "destinationComponentDeploymentId": "uuid",
    "dcsContractRevisionId": "uuid"
  },
  "requirementReadAuthorityReference": "authority-ref"
}
```

Mappings:
- Requirement not found -> 404;
- Requirement read denied -> 403;
- Requirement read unknown -> 409;
- invalid/naive `asOf` -> 422 `InvalidAsOf`;
- Requirement-side alignment dependency unavailable -> 503 `AlignmentUnavailable`;
- Access Policy coverage uncertainty after authorized Requirement read -> 200 with `status = Unknown`.

No Rule-level evidence is included in the first I14 slice.

## Catalogue presentation metadata

I12 adds optional presentation enrichment to responses that are already authorized by their enclosing use case. It does not add a generic catalogue read endpoint.

Presentation block:

```json
{
  "catalogue": {
    "sourceDisplayName": "Checkout Web",
    "destinationDisplayName": "Orders API",
    "dcsDisplayName": "HTTPS Orders",
    "trafficAlternatives": [
      {
        "protocol": "tcp",
        "sourcePorts": {"kind": "Any"},
        "destinationPorts": {
          "kind": "Ranges",
          "ranges": [{"first": 443, "last": 443}]
        },
        "serviceReference": "https"
      }
    ],
    "dcsProvenanceReference": "..."
  }
}
```

Rules:
- all display-name fields are nullable;
- stable semantic IDs remain present outside the presentation block;
- missing labels or presentation decode failure do not redefine/deny an otherwise authorized Rule/policy read;
- DCS presentation is used only when the exact revision subject matches the requested Source/Destination identity;
- the block may appear on proposal interaction options, Rule DTOs, Effective Desired Policy Rules and normalized rows.

### Proposal interaction search

`GET /api/v1/access-rule-proposals/interactions` additionally accepts optional `search` (maximum 256 characters).

Search is applied server-side after the existing `ProposeConnectivity` authority gate and may match:
- Source Component Deployment display name or UUID;
- Destination Component Deployment display name or UUID;
- DCS display name or revision UUID.

Search does not broaden the set of structurally valid directed interactions.

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

Purpose: discover governance scopes with unambiguous effective `ReadEffectiveDesiredPolicy` authority for the authenticated actor at the same explicit `asOf` used by policy views.

Query:
- `asOf` — required offset-aware RFC 3339 instant.

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

The I8 HTTP adapter uses FastAPI as an outer transport framework. FastAPI/Pydantic types remain confined to presentation adapters and `napms.platform.http`; Domain/Application stay framework-independent.

Normal local composition uses the durable PostgreSQL-backed Connectivity Decision runtime. Access Policy consumes it through its own exact subject/scope/time projection. Explicit injected Decision-port fakes remain a focused test seam only and are not selected by the normal product composition.

## Deferred HTTP surfaces

Not part of the first vertical slice:
- approval/review routes;
- persistent Access Request CRUD;
- generic ACC/RC/Authority administration;

- CSV/XLSX;
- device/provider execution.
