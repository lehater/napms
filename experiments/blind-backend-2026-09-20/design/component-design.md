# Backend component design

Status: ACCEPTED candidate after Coding-Agent Challenge 01

## Design intent

Provide coding-agent-visible public component and dependency contracts. Private helpers, concrete collections and local algorithms remain implementation freedoms.

## Boundary values

Public cross-module values are immutable and infrastructure-neutral:

- opaque refs: ResourceRef, EndpointRef, SiteRef, ResponsibilityGroupRef, ApplicationRef, ComponentRef, InteractionRef, InteractionRevisionRef, DeploymentRef, ProcessRef, NeedRef, AccessRequestRef, PolicyRuleRef;
- Principal(subject, permissions);
- AddressRealization = HostAddress | Prefix;
- TrafficClause(protocol, sourcePortRanges, destinationPortRanges);
- AggregateVersion;
- MaterializationStatus = COMPLETE | UNRESOLVED;
- MaterializationIssueCode;
- accepted application error categories.

These are owner-published contract values, not a shared mutable “common domain” model.

## Runtime/platform components

### StartupConfigLoader

Responsibility: read and validate the exact Operability Design `NAPMS_*` startup environment contract once before listener creation.

Output: immutable RuntimeConfig.

Forbidden:
- reading environment variables from domain/application components;
- config files/CLI override precedence;
- runtime reload;
- hidden numeric defaults for required keys.

### ApiServer

Responsibility:
- route HTTP;
- establish/validate correlation id;
- authenticate;
- enforce the Security Architecture operation permission;
- strictly decode the exact Interface DTO;
- enforce required Idempotency-Key and If-Match headers;
- invoke one application entry point;
- map accepted result/error to exact HTTP status/body/headers.

Dependencies: Authenticator, Authorizer, ETagCodec, CorrelationContext, application entry points, ProblemMapper.

Forbidden:
- direct SQL/repositories;
- domain-object deserialization from arbitrary JSON;
- caller-controlled principal/permission;
- inventing fallback status/error semantics.

### Authenticator

Responsibility: validate bearer token against configured OIDC trust.

Result is exactly one of:
- Authenticated(Principal);
- InvalidCredential -> Interface 401;
- IdentityDependencyUnavailable -> Interface 503.

The adapter owns bounded metadata/JWKS fetch/cache mechanics but must obey Operability/Security retry, max-stale and fail-closed semantics.

### Authorizer

`require(Principal, Permission)` succeeds only for the exact required permission string. No permission implication, Resource responsibility or Process organization inference is allowed.

### ETagCodec

Maps AggregateVersion <-> opaque quoted HTTP ETag.

Only exact token equality is meaningful. API/application code does not expose numeric version as external concurrency semantics.

### ConsistencyRunner

Application-owned abstraction implemented by relational infrastructure.

Contracts:

- `runWrite(operation)`: supplies one transaction-bound semantic-owner repository set plus declared peer read ports bound to the same database snapshot;
- `runReadSnapshot(operation)`: supplies all declared owner read ports in one coherent read-only snapshot plus `evaluationAt`.

Rules:
- only the declared semantic owner may be written;
- transaction/connection framework types do not leak into domain/public application contracts;
- cancellation/deadline propagates from request context;
- no automatic mutation retry.

### IdempotentCommandGuard / IdempotencyPort

Used only for Interface-marked Idempotent-create operations.

Input:
- principal subject;
- stable operation id;
- Idempotency-Key;
- deterministic canonical request fingerprint.

Transaction-bound decision:

- NEW -> command may create state; committed semantic result/HTTP reconstruction data are finalized atomically with owner state;
- REPLAY -> return the previously committed semantic result without re-running domain mutation;
- CONFLICT -> same key/different fingerprint;
- UNKNOWN/timeout -> never fabricate success.

Concurrent identical keys are serialized by persistence uniqueness/transaction semantics; after a competing transaction resolves, a loser re-reads the committed record or reports bounded dependency/timeout failure.

The guard does not make non-idempotent commands retryable and is not a generic workflow engine.

### Clock / IdGenerator

Narrow abstractions only where accepted behavior needs current time/new opaque identity.

## Resource Description module

Public application components:
- ResourceCommandService
- ResourceQueryService
- SiteService
- ResponsibilityGroupService

Owner ports:
- ResourceRepository: load/save one Resource aggregate under expected Resource version.
- SiteRepository: register/read immutable Site.
- ResponsibilityGroupRepository: register/read immutable group.
- ResourceHistoryReader: bounded address/Site/responsibility history.

Public peer read port `ResourceResolutionPort`:
- `resolveResource(ResourceRef)`;
- `currentEndpointAddresses(ResourceRef)` -> endpointRef, AddressRealization, effectiveFrom, provenance for every current addressed endpoint.

No peer receives persistence rows or Resource mutation methods.

## Application Communication module

Public components:
- ApplicationCommandService
- ApplicationQueryService
- InteractionRevisionQueryService

Owner ports:
- ApplicationRepository: load/save Application aggregate under expected Application version.
- InteractionRevisionReader: immutable exact-revision lookup.

Public peer read port `CommunicationResolutionPort`:
- `resolveComponent(ComponentRef)` -> ApplicationRef + ComponentRef;
- `resolveInteraction(InteractionRef)` -> ApplicationRef + source/destination ComponentRefs;
- `resolveInteractionRevision(InteractionRevisionRef)` -> InteractionRef, source/destination ComponentRefs, immutable TrafficClauses, createdAt/provenance.

## Application Deployment module

Public components:
- DeploymentCommandService
- DeploymentQueryService

Owner port:
- DeploymentRepository: insert/read immutable ComponentDeployment.

Public peer read port `DeploymentResolutionPort`:
- `resolveDeployment(DeploymentRef)` -> ComponentRef, ResourceRef, createdAt.

Registration consumes CommunicationResolutionPort and ResourceResolutionPort; it stores only stable refs.

## Business Connectivity module

Public components:
- BusinessProcessCommandService
- BusinessConnectivityQueryService

Owner port:
- BusinessProcessRepository: load/save Process aggregate under expected BusinessProcess version.

Public peer read port `ConnectivityNeedResolutionPort`:
- `resolveCurrentNeed(NeedRef)` -> ProcessRef, InteractionRef, businessProcessVersion, createdAt/provenance;
- returns explicit NOT_CURRENT for RETIRED Need;
- historical resolution is query-only for explanation.

Need creation consumes CommunicationResolutionPort to validate InteractionRef.

## Access Policy module

Public components:
- AccessRequestCommandService
- PermissionDecisionCommandService
- PolicyRuleCommandService
- AccessPolicyQueryService

Owner ports:
- AccessRequestRepository
- PolicyRuleRepository
- AccessPolicyHistoryReader
- transaction-bound IdempotencyPort

### SubmitAccessRequest collaboration

Inside one `ConsistencyRunner.runWrite` transaction:
- Authorizer(`access.request`);
- IdempotentCommandGuard;
- ConnectivityNeedResolutionPort;
- CommunicationResolutionPort;
- DeploymentResolutionPort;
- AccessRequestRepository.

The stored request includes the validated BusinessProcess version and exact immutable refs.

### Permission decision collaboration

Inside one write transaction:
- Authorizer(`access.decide`);
- IdempotentCommandGuard;
- AccessRequestRepository under expected AccessRequest version;
- PolicyRuleRepository.

ALLOWED decision + first Rule are one atomic result.

### Policy effect collaboration

- Authorizer(`access.manage`);
- PolicyRuleRepository under expected PolicyRule version;
- same-state command is a no-op with unchanged version/history.

Public peer read port `EffectivePolicyReadPort`:
- iterate current ACTIVE Rule subjects/provenance in the supplied read snapshot.

## Current Policy Materialization component

### CurrentPolicyMaterializer

Responsibility: compose owner facts into current vendor-neutral policy without owning source truth.

Dependencies inside `ConsistencyRunner.runReadSnapshot`:
- EffectivePolicyReadPort;
- CommunicationResolutionPort;
- DeploymentResolutionPort;
- ResourceResolutionPort.

Contract:
- resolve every ACTIVE Rule in the same snapshot;
- produce SOURCE_REALIZATION_MISSING / DESTINATION_REALIZATION_MISSING / REFERENCE_UNRESOLVABLE exactly as accepted;
- expand source endpoint × destination endpoint × TrafficClause;
- preserve HOST/PREFIX and exact port semantics;
- preserve independent Rule/Need/decision/revision/deployment/resource/endpoint provenance;
- return COMPLETE iff no issue exists;
- return UNRESOLVED as a normal application result when issues exist;
- propagate actual dependency/runtime failure rather than converting it to UNRESOLVED.

No write repository and no durable materialization state exist in the MVP.

## Persistence adapters

Each semantic owner has its own adapter set. A relational ConsistencyRunner coordinates transaction/snapshot lifetime and supplies transaction-bound adapters.

Forbidden:
- generic repository over arbitrary entities;
- SQL from domain/application services;
- peer schema mutation;
- persistence row types crossing public module ports;
- child-level concurrency versions that contradict owner aggregate versioning.

## HTTP mapping boundary

Dedicated mappers/codecs implement:
- strict JSON DTO <-> application value mapping;
- AddressRealization/TrafficClause validation;
- parent aggregate If-Match semantics;
- Idempotency-Key scope/fingerprint;
- AggregateVersion <-> opaque ETag;
- exact Problem code/status mapping;
- COMPLETE/UNRESOLVED result mapping;
- Resource history pagination cursor.

Private framework/request objects never cross into domain code.

## Composition

Runtime composition constructs:

1. StartupConfigLoader -> immutable RuntimeConfig;
2. PostgreSQL pool/data source;
3. owner repositories/read adapters + ConsistencyRunner;
4. IdempotencyPort;
5. OIDC Authenticator + Authorizer;
6. application services/public peer ports;
7. ApiServer;
8. observability/health/shutdown adapters.

No service locator is accessible from domain/application code.

## Structural verification obligations

- domain packages cannot import HTTP/runtime/PostgreSQL/OIDC/telemetry/config packages;
- API handlers cannot import concrete repositories;
- one owner adapter cannot mutate peer tables;
- peer read ports return owner facts rather than persistence rows;
- Policy Materialization has no write dependency;
- only Resource/Application/BusinessProcess/AccessRequest/PolicyRule repositories expose optimistic version mutation;
- environment reads occur only in StartupConfigLoader/bootstrap;
- public HTTP DTOs do not appear in domain packages.

## Implementation freedoms

Private function/type names, internal collections, SQL query/index tuning, JSON/OIDC/logging libraries, DI wiring syntax, opaque pagination encoding, safe internal caching that preserves snapshot/cache-age contracts, and local refactoring remain free.
