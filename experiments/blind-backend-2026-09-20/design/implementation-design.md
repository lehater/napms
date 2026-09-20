# Backend implementation design

Status: ACCEPTED candidate after Coding-Agent Challenge 01

## Implementation target

Greenfield realization of the blind backend design only. Existing NAPMS production code is not an input and must not be copied or used to settle semantics.

## Selected realization stack

- Language: Go, current supported stable toolchain at implementation start.
- Runtime: one stateless HTTP process using Go standard HTTP/context facilities; no application framework is required.
- Database: PostgreSQL.
- Database access: explicit bound SQL through a PostgreSQL driver/pool; no ORM.
- JSON: strict decoder that can reject unknown fields as required by Interface Design.
- Authentication: maintained OIDC/JWT validation library or small adapter capable of the accepted issuer/audience/signature/time and bounded JWKS cache/fetch semantics.
- IDs: server-generated opaque UUID values; UUID structure is not semantic.
- Timestamps: PostgreSQL/Go UTC instants with RFC 3339 at HTTP boundary.

Rationale: this stack directly satisfies modular-monolith, explicit dependency, cancellation/context and snapshot-transaction contracts with minimal framework semantics. PostgreSQL provides the required transactional snapshot and constraint model.

A library may be substituted only when all accepted external/transaction/security/operability behavior remains unchanged.

## Repository/module layout contract

Suggested top-level realization:

- `cmd/napms/` — process bootstrap/composition only.
- `internal/resource/` — Resource Description domain/application ports/services.
- `internal/applicationcommunication/`
- `internal/applicationdeployment/`
- `internal/businessconnectivity/`
- `internal/accesspolicy/`
- `internal/policymaterialization/`
- `internal/platform/httpapi/` — strict DTO/router/ETag/idempotency/problem mapping.
- `internal/platform/security/` — OIDC authentication + permission authorizer.
- `internal/platform/postgres/` — pool, transaction runner, migrations and owner adapters.
- `internal/platform/observability/` — structured evidence/metrics/correlation.
- `internal/platform/config/` — startup-only `NAPMS_*` environment parsing/validation.
- `migrations/` — ordered SQL grouped/named by owning module.

Equivalent names are allowed if dependency/ownership boundaries remain mechanically recognizable.

## Runtime configuration realization

Implement the Operability Design keys exactly:

- `NAPMS_LISTEN_ADDR`
- `NAPMS_DATABASE_DSN`
- `NAPMS_OIDC_ISSUER`
- `NAPMS_OIDC_AUDIENCE`
- `NAPMS_OIDC_PERMISSION_CLAIM`
- `NAPMS_DB_STATEMENT_TIMEOUT`
- `NAPMS_HTTP_REQUEST_TIMEOUT`
- `NAPMS_OIDC_HTTP_TIMEOUT`
- `NAPMS_OIDC_FETCH_MAX_ATTEMPTS`
- `NAPMS_OIDC_FETCH_BACKOFF`
- `NAPMS_JWKS_MAX_STALE`
- `NAPMS_SHUTDOWN_GRACE`
- optional `NAPMS_LOG_LEVEL`.

Requirements:
- parse/validate once before opening the listener;
- reject unknown `NAPMS_*` names;
- no config files/flags/runtime reload/feature flags;
- no hidden numeric defaults for required timeout/retry keys;
- DSN value is secret/redacted;
- OIDC adapter must surface “invalid token” separately from “cannot establish validity because key dependency is unavailable”.

## Slice order

### I1 — Runtime skeleton and owner boundaries

Create module/package skeleton, composition root, strict startup configuration, PostgreSQL pool/migration runner, correlation context, health probes, shutdown handling and architecture dependency checks. No product behavior beyond startup/health.

Completion:
- fresh DB migration;
- valid config starts and invalid/missing/unknown config fails before listen;
- live/ready and graceful shutdown contracts executable;
- forbidden dependency checks executable.

### I2 — Resource Description

Implement immutable Site and ResponsibilityGroup registration/read; Resource/Endpoint, Site assignment, address history and responsibility history; Resource-version optimistic concurrency; accepted HTTP representations.

Completion:
- T-RES-*;
- Site-history preservation;
- Resource stale-concurrency/ETag;
- idempotent creates;
- resource permission matrix;
- persistence integration.

### I3 — Application Communication

Implement Application/Component/Interaction/immutable InteractionRevision, exact traffic normalization and Application-version child concurrency.

Completion:
- T-TRAFFIC-REVISION/property tests;
- nested If-Match behavior;
- idempotent creates;
- HTTP/persistence contracts.

### I4 — Application Deployment and Business Connectivity

Implement immutable ComponentDeployment registration/read; Process/ResponsibleOrganization; Need creation/terminal retirement with BusinessProcess-version concurrency.

Completion:
- deployment reference validation;
- no deployment label/move/retire API;
- Need lifecycle/history/currentness;
- process-child ETag/idempotency;
- relevant authorization/API tests.

### I5 — Access Policy

Implement request submission shared-snapshot validation, request ETag, permission decision finality, atomic ALLOWED->PolicyRule creation, PolicyRule state, idempotency/concurrency/provenance.

Completion:
- T-REQUEST-*;
- T-DECISION-*;
- T-RULE-*;
- T-IDEMPOTENCY;
- request/decide/manage permission separation.

### I6 — Current Policy Materialization

Implement read-only shared-snapshot CurrentPolicyMaterializer and the exact Interface Design response.

Completion:
- both COMPLETE and UNRESOLVED return HTTP 200 application results;
- exact normalized row shape/traffic/address expansion/provenance;
- stable MaterializationIssue codes;
- dependency failure remains HTTP 503 rather than UNRESOLVED;
- concurrent snapshot tests.

### I7 — Security and operability closure

Implement the already-accepted API error/header semantics, all authorization mappings, OIDC cache/fetch rules, diagnostic evidence, metrics, timeouts/cancellation, config non-reload and secret redaction.

This slice contains no new external/domain semantics.

Completion: V4/V5/V7 and configuration/security test contracts green.

### I8 — End-to-end/fresh-start closure

Run all migrations on empty PostgreSQL and execute complete + negative sibling journeys using only public HTTP and configured OIDC test infrastructure.

Completion: V8 and all Test Design obligations green; no manual DB state fabrication.

## PostgreSQL realization constraints

- separate logical schemas or unambiguous table ownership prefixes per semantic owner; exact names are local;
- owner-local FK/check/unique/exclusion constraints implement Persistence Design;
- no FK across independently owned module schemas;
- effective temporal rows use `timestamptz`;
- address storage may use validated text or PostgreSQL network types only if HOST/PREFIX distinction and canonical output are preserved;
- protocol storage uses a stable normalized identifier; accepted API aliases map at the adapter boundary;
- Resource/Application/BusinessProcess/AccessRequest/PolicyRule optimistic versions follow Persistence Design exactly; no duplicate child version semantics;
- transaction runner sets isolation explicitly; current materialization uses REPEATABLE READ or stronger;
- prepared/bound parameters only;
- migration identity is immutable; changed applied migration content is rejected where runner checksum support exists.

## Completion criteria

IMPLEMENTATION is complete only when:

1. every HTTP operation, request/response shape, status/header rule and authorization mapping in Interface/Security Design exists;
2. required Idempotency-Key and If-Match semantics are applied exactly to the declared operations;
3. every domain invariant and application consistency rule is enforced at its owner;
4. PostgreSQL schema/migrations realize Persistence Design including Resource Site/address/responsibility history and aggregate-version ownership;
5. CurrentPolicyMaterializer cannot return COMPLETE with unresolved active-rule input and never converts dependency failure into application UNRESOLVED;
6. normalized rows preserve exact traffic semantics and independent provenance;
7. OIDC authentication/cache/fail-closed dependency distinctions hold;
8. startup configuration, no-reload, retry/timeout, logging/metrics/health/cancellation/shutdown/redaction semantics are observable;
9. architecture/component dependency checks pass;
10. every Test Design contract has executable evidence at the proper level;
11. full fresh-database end-to-end acceptance journey and negative siblings pass;
12. no implementation convention introduces a new product/domain/API/data/security/operability semantic decision.

## Explicit coding-agent freedoms

Private function/type names, helper decomposition, exact Go filenames, SQL/index/query optimization preserving accepted contracts, choice among maintained libraries that satisfy those contracts, migration-runner implementation, logger/metrics library, test framework/helpers, UUID library, composition wiring syntax and local refactorings.

The following are **not** coding freedoms: endpoint DTO/status/header semantics, permission mapping, aggregate concurrency owner, idempotency scope, transaction boundaries, OIDC failure classification, configuration precedence/reload/retry semantics, logging safety or materialization COMPLETE/UNRESOLVED meaning.

If implementation discovers an expected behavior not decidable from the closure, it must stop that slice and report the missing upstream decision rather than select a convention.
