# Backend implementation design

Status: ACCEPTED candidate

## Implementation target

Greenfield realization of the frozen blind backend design only. Existing NAPMS production code is not an input and must not be copied or used to settle semantics.

## Selected realization stack

- Language: Go, current supported stable toolchain at implementation start.
- Runtime: one stateless HTTP process using Go standard HTTP/context facilities; no application framework is required.
- Database: PostgreSQL.
- Database access: explicit SQL through a PostgreSQL driver/pool; no ORM.
- JSON: standard Go JSON facilities or a drop-in serializer that preserves the same contract.
- Authentication: a maintained OIDC/JWT validation library capable of issuer/audience/signature/time validation; library identity/version is a dependency-selection freedom subject to supply-chain verification.
- IDs: server-generated opaque UUID values; UUID structure is not semantic.
- Timestamps: PostgreSQL/Go UTC instants with RFC 3339 at HTTP boundary.

Rationale: this stack directly satisfies modular-monolith, explicit dependency, cancellation/context and snapshot-transaction contracts with minimal framework semantics. PostgreSQL provides the required transactional snapshot and constraint model. Framework/library substitutions are allowed only when they preserve all accepted contracts.

## Repository/module layout contract

Suggested top-level realization:

- `cmd/napms/` — process bootstrap/composition only.
- `internal/resource/` — domain + application ports/services.
- `internal/applicationcommunication/`
- `internal/applicationdeployment/`
- `internal/businessconnectivity/`
- `internal/accesspolicy/`
- `internal/policymaterialization/`
- `internal/platform/httpapi/` — DTO/router/problem mapping.
- `internal/platform/security/` — OIDC authentication + permission authorizer.
- `internal/platform/postgres/` — pool, transaction runner, migrations and owner adapters.
- `internal/platform/observability/` — structured logs/metrics/correlation.
- `migrations/` — ordered SQL, grouped/named by owning module.

Equivalent names are allowed if dependency/ownership boundaries remain mechanically recognizable.

## Slice order

### I1 — Runtime skeleton and owner boundaries
Create module/package skeleton, composition root, typed configuration, PostgreSQL pool/migration runner, correlation context, health probes, and architecture dependency checks. No product behavior beyond startup/health.

Completion: fresh DB migration + process startup/readiness test green; forbidden dependency checks executable.

### I2 — Resource Description
Implement Site, ResponsibilityGroup, Resource, Endpoint, address/responsibility history; owner repository/HTTP contract.

Completion: T-RES-* + stale concurrency + resource authorization matrix + persistence integration green.

### I3 — Application Communication
Implement Application/Component/Interaction/immutable InteractionRevision + traffic normalization.

Completion: T-TRAFFIC-REVISION/property tests + HTTP/persistence contracts green.

### I4 — Application Deployment and Business Connectivity
Implement immutable ComponentDeployment registration/read; Process/ResponsibleOrganization/Need lifecycle.

Completion: deployment reference validation, Need lifecycle/history, relevant auth/API tests green.

### I5 — Access Policy
Implement request submission shared-snapshot validation, permission decision finality, PolicyRule state, idempotency/concurrency/provenance.

Completion: T-REQUEST-*, T-DECISION-*, T-RULE-*, T-IDEMPOTENCY and auth separation green.

### I6 — Current Policy Materialization
Implement read-only shared-snapshot CurrentPolicyMaterializer and normalized output mapping.

Completion: COMPLETE/UNRESOLVED, exact expansion/provenance, independent-effect preservation and concurrent snapshot tests green.

### I7 — Full external API/security/operability closure
Finish all endpoint representations/problem mapping, OIDC edge cases, permission matrix, diagnostic events/metrics/timeouts/cancellation/redaction.

Completion: V4/V5/V7 contracts green.

### I8 — End-to-end/fresh-start closure
Run all migrations on empty PostgreSQL and execute complete + negative sibling journeys using only public HTTP and configured OIDC test issuer/stub.

Completion: V8 and all verification/test-design obligations green; no manual DB state fabrication.

## PostgreSQL realization constraints

- separate logical schemas or unambiguous table ownership prefixes per domain owner; exact schema naming is local.
- owner-local FK/check/unique constraints are required where Data Design states them.
- no FK across independently owned module schemas.
- effective temporal rows use `timestamptz`; address value can use validated text or PostgreSQL network type while retaining HOST/PREFIX distinction.
- Interaction protocol is normalized to a stable protocol identifier; API name aliases map at the adapter boundary.
- transaction runner sets required isolation explicitly; materialization uses REPEATABLE READ or stronger.
- prepared/bound parameters only.
- migration table records exact applied migration identity/checksum if the chosen runner supports it; changed already-applied migration content is an error.

## Completion criteria

IMPLEMENTATION is complete only when:

1. all documented HTTP operations and authorization mappings exist;
2. every domain invariant and application consistency rule is enforced at its owner;
3. PostgreSQL schema/migrations realize Data Design with no cross-owner write coupling;
4. CurrentPolicyMaterializer cannot return COMPLETE with unresolved active-rule input;
5. OIDC authentication/fail-closed permissions/secrets rules hold;
6. required logging/metrics/health/cancellation semantics are observable;
7. architecture/component dependency checks pass;
8. every Test Design contract has executable evidence at the proper level;
9. full fresh-database end-to-end acceptance journey and negative siblings pass;
10. no implementation-only convention has become a new product/domain/API/security semantic decision.

## Explicit coding-agent freedoms

Private function/type names, helper decomposition, exact Go file names, SQL/index/query optimization preserving accepted plans, choice among maintained OIDC/JWT libraries, exact migration runner, logger/metrics library, test framework/helpers, UUID library, composition wiring syntax and refactorings that preserve public component contracts.

If implementation discovers an expected behavior not decidable from the closure, it must stop that slice and report the missing upstream decision rather than select a convention.
