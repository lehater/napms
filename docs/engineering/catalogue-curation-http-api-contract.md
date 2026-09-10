# I27 Catalogue Curation HTTP API contract

Status: `accepted / implemented through I28 J01 pilot corrections`.

Date: 2026-09-10.

Owner requirement: `docs/requirements/catalogue-curation.md`.

Base HTTP conventions: `docs/engineering/http-api-contract.md`.

Relevant decisions:
- `docs/decisions/ADR-011-i27-external-correlation-reference-input.md`;
- I27 catalogue authority/lifecycle/idempotency decisions referenced by the active plan.

## Purpose and precedence

This artifact owns the I27 public transport contract for `/api/v1/catalogues/**`, including I28 corrections that expose already accepted catalogue lifecycle and presentation behavior needed by the Application workspace.

It extends the shared session, correlation, error-envelope and framework-boundary rules in `http-api-contract.md`. If a catalogue-specific statement here conflicts with an older generic/deferred statement in the base contract, this artifact is authoritative for the catalogue surface.

The API is task-oriented. It is not a generic table/CMDB CRUD API.

## Trust boundary

Server-owned for every catalogue mutation:
- authenticated `actor_id` from the session;
- command/effective action time from the runtime clock;
- authority action/scope selected by the owning catalogue adapter;
- generated catalogue identity/reference where NAPMS owns that identity;
- generated provenance reference;
- idempotency outcome persisted by the owning catalogue.

Mutation requests must not supply:
- `actorId`;
- authority reference;
- catalogue mutation authority scope;
- provenance reference;
- server-generated Application/Component/Deployment/DCS/Resource/fact identity for create operations.

Every catalogue mutation requires a non-empty `Idempotency-Key` header. Equivalent retry resolves the authoritative prior result; reuse for a different command/input is `409 CatalogueIdempotencyConflict`.

## Authority

Mutation admission is independent of catalogue visibility, Resource Responsibility and `ReadScopedConnectivity`.

Selected catalogue mutation actions:
- Application Communication Catalogue: `CurateApplicationCatalogue` at server-selected catalogue scope `application-catalogue`;
- Resource Catalogue: `CurateResourceCatalogue` at server-selected catalogue scope `resource-catalogue`.

The caller cannot substitute either scope in request JSON/query parameters.

Current catalogue-read visibility baseline preserves the accepted authenticated catalogue visibility model. Read permission does not imply either mutation action.

## Application Communication Catalogue reads

### GET /api/v1/catalogues/applications

Paged/searchable Application catalogue discovery.

Query:
- `page`, `pageSize`;
- optional `search`;
- optional lifecycle controls admitted by the implementation contract.

Returned stable IDs remain available as secondary technical identity; presentation uses display labels where present.

### GET /api/v1/catalogues/applications/{applicationId}

Returns the owner-composed Application tree used by lightweight catalogue consumers:

```text
Application
  -> Components
      -> Component Deployments
          -> effective Deployment Resource Bindings
          -> DCS revision summaries
```

The HTTP adapter does not reconstruct this hierarchy from unrelated endpoints.

### GET /api/v1/catalogues/application-workspace/{applicationId}

Returns the Application-workspace projection over the same ACC-owned hierarchy. It includes lifecycle/version fields required for optimistic maintenance and expands each DCS revision with decoded vendor-neutral `trafficAlternatives`:

```json
{
  "protocol": "tcp",
  "sourcePorts": {"kind": "Any"},
  "destinationPorts": {
    "kind": "Ranges",
    "ranges": [{"first": 443, "last": 443}]
  },
  "serviceReference": "https"
}
```

Raw `projection_payload` bytes are never exposed to the Web client. If a stored payload cannot be decoded, the adapter does not invent traffic semantics; the revision remains identifiable with an empty alternatives collection so the UI can present that semantics are unavailable.

Query:
- optional offset-aware `asOf`;
- optional `includeRetiredComponents`;
- optional `includeRetiredDeployments`.

### GET /api/v1/catalogues/application-participants

Backend discovery for normal cross-entity DCS authoring.

Only fully Active `Application -> Component -> Component Deployment` chains are selectable.

Query:
- `page`, `pageSize`;
- optional `search`.

The normal Web path uses this endpoint instead of asking a user to paste deployment UUIDs.

## Application Communication Catalogue mutations

### POST /api/v1/catalogues/applications

Creates a first-class Application. Request contains presentation data only; Application identity/provenance are server-owned.

### POST /api/v1/catalogues/applications/{applicationId}/components

Creates a Component under an Active Application. Parent identity comes from the route.

### POST /api/v1/catalogues/components/{componentId}/deployments

Creates a Component Deployment under an Active Component/ancestor Application chain.

### POST /api/v1/catalogues/applications/{applicationId}/rename
### POST /api/v1/catalogues/components/{componentId}/rename
### POST /api/v1/catalogues/deployments/{deploymentId}/rename

Rename presentation metadata without changing stable catalogue identity. Requests carry current `expectedVersion`; stale edits return `409 CatalogueConcurrencyConflict`. Application and Component require non-empty display names. Component Deployment may clear its optional display name by sending `null`.

Example:

```json
{
  "displayName": "Orders API",
  "expectedVersion": 2
}
```

### POST /api/v1/catalogues/applications/{applicationId}/retire
### POST /api/v1/catalogues/components/{componentId}/retire
### POST /api/v1/catalogues/deployments/{deploymentId}/retire

Retire stable catalogue identities; no hard delete is exposed. Request:

```json
{
  "expectedVersion": 2
}
```

Retirement follows the accepted leaf-to-parent constraints: active Component Deployments block Component retirement and active Components block Application retirement. Such attempts return `409 CatalogueRetirementBlocked`. Historical bindings, DCS revisions and downstream references are preserved.

### POST /api/v1/catalogues/dcs-revisions

Creates one immutable DCS revision from ACC-owned communication semantics.

Request contains:
- source/destination Component Deployment IDs selected through backend discovery;
- optional display label;
- one-or-more vendor-neutral traffic alternatives (protocol, source/destination port constraints, optional service reference).

The request never accepts raw projection bytes or ACL/vendor syntax. Correcting communication semantics creates another DCS revision; an existing revision is never edited in place.

### POST /api/v1/catalogues/deployments/{deploymentId}/resource-bindings

Creates a temporal Deployment Resource Binding to an Active Resource selected through Resource discovery.

Request contains Resource reference plus validity input; binding identity/provenance are server-owned.

### POST /api/v1/catalogues/deployment-resource-bindings/{bindingReference}/end

Ends an effective binding without deleting history.

Request:

```json
{
  "validTo": "2026-09-10T12:00:00+00:00",
  "expectedVersion": 1
}
```

The normal Web action uses the selected binding reference/version from the current detail projection; the user does not type them.

## Resource Catalogue reads

### GET /api/v1/catalogues/resources

Lightweight authenticated Resource discovery used by cross-entity forms such as Deployment Resource Binding.

This endpoint remains deliberately small so discovery consumers do not depend on Resources-workspace diagnostics.

### GET /api/v1/catalogues/resource-workspace

Owner-specific Resources workspace projection.

Query:
- `page`, `pageSize`;
- optional `search`;
- optional `responsibilityScope`;
- optional offset-aware `asOf`; when omitted the runtime clock supplies one logical instant;
- optional `includeRetired`.

`responsibilityScope` filters by an effective `Resource Scope Affiliation` at the same `asOf`. It is business data filtering and does not establish catalogue mutation authority.

Search may match Resource reference/display name and current Responsibility party reference/display/contact data.

Each item includes current-fact diagnostics:

```json
{
  "currentFacts": {
    "hasRealization": true,
    "hasScopeAffiliation": true,
    "hasResponsibility": true,
    "hasContact": false
  }
}
```

These are read projections at `asOf`; they are not Resource aggregate state.

### GET /api/v1/catalogues/resources/{resourceReference}

Returns the Resource plus current/effective owner facts at one logical `asOf`:
- realizations/endpoints;
- Resource Scope Affiliations;
- Resource Responsibilities/contact assignments.

## Resource Catalogue mutations

### POST /api/v1/catalogues/resources

Creates a stable Resource identity. Display name is presentation metadata; Resource identity/provenance are generated by NAPMS.

### POST /api/v1/catalogues/resources/{resourceReference}/realizations

Creates the first/non-overlapping authoritative Resource realization version from technical addresses and validity.

### POST /api/v1/catalogues/resource-realizations/{factReference}/replacement

Atomically ends the selected current realization and creates its successor.

Request:

```json
{
  "technicalAddresses": ["203.0.113.20"],
  "validFrom": "2026-09-10T12:00:00+00:00",
  "validTo": null,
  "expectedVersion": 1
}
```

History/provenance of the replaced fact is retained.

### POST /api/v1/catalogues/resources/{resourceReference}/scope-affiliations

Creates a temporal Resource Scope Affiliation.

`responsibilityScope` is an external business correlation reference under ADR-011. NAPMS does not create the referenced scope and does not derive catalogue authority from the value.

### POST /api/v1/catalogues/resource-scope-affiliations/{affiliationReference}/end

Ends the selected affiliation using `validTo` + `expectedVersion`; no hard delete.

### POST /api/v1/catalogues/resources/{resourceReference}/responsibilities

Creates a temporal Resource Responsibility assignment.

Accepted party kinds:
- `Person`;
- `Team`.

Accepted roles:
- `ServiceOwner`;
- `TechnicalOwner`;
- `OperationsContact`;
- `BusinessOwner`.

`partyReference` is an external correlation reference under ADR-011. The assignment does not grant NAPMS authority.

### POST /api/v1/catalogues/resource-responsibilities/{assignmentReference}/end

Ends the selected responsibility using `validTo` + `expectedVersion`; creation provenance remains intact and end provenance is recorded separately.

## Temporal and concurrency rules

For temporal facts/relations:
- timestamps are RFC 3339 and offset-aware;
- validity uses `[validFrom, validTo)` semantics;
- creation and explicit end/replacement keep separate provenance;
- current authoritative overlap is rejected according to the owning domain rule;
- normal maintenance is create/end/replace, not destructive delete.

Versioned mutations use optimistic concurrency through `expectedVersion`. Stale version is `409 CatalogueConcurrencyConflict`.

## Error mapping

Catalogue endpoints use the shared public error envelope.

Minimum stable catalogue mappings:

| Condition | HTTP | Public code |
|---|---:|---|
| unauthenticated session | 401 | `AuthenticationRequired` |
| catalogue mutation denied | 403 | `CatalogueAuthorityDenied` |
| catalogue authority ambiguous/unknown | 409 | `CatalogueAuthorityUnknown` |
| subject not found | 404 | `CatalogueSubjectNotFound` |
| inactive parent/Resource | 409 | `CatalogueParentInactive` / `CatalogueResourceInactive` |
| blocked parent retirement | 409 | `CatalogueRetirementBlocked` |
| invalid input/domain invariant | 422 | `CatalogueInputInvalid` / `CatalogueValidationError` |
| invalid temporal interval/time | 422 | catalogue time/interval validation code |
| temporal overlap | 409 | `CatalogueOverlapConflict` |
| optimistic version conflict | 409 | `CatalogueConcurrencyConflict` |
| idempotency key conflict | 409 | `CatalogueIdempotencyConflict` |
| known persistence execution failure | 503 | catalogue unavailable code |
| ambiguous commit acknowledgement | 503 | `CataloguePersistenceOutcomeUnknown` |

Known pre-commit SQL failure and ambiguous commit acknowledgement are intentionally distinct application/adapter outcomes.

## Acceptance contract

The catalogue acceptance path must prove without pre-seeding the newly curated business objects:

```text
create Resources
  -> realization + scope affiliation + responsibility
create Application -> Components -> Deployments
  -> rename/correct structure without changing identity
  -> bind Deployments to Resources
  -> create immutable DCS
  -> reopen and inspect its traffic semantics
  -> observe the new relationship in scoped Connectivity
  -> declare an existing Connectivity Requirement/Need for that interaction
  -> observe Required state
```

A separate security acceptance must prove that authenticated catalogue read access does not grant `CurateApplicationCatalogue` or `CurateResourceCatalogue` mutation authority.
