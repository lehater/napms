# Backend component design

Status: ACCEPTED candidate

## Design intent

Provide coding-agent-visible public component and dependency contracts. Private helpers, concrete data structures and local algorithms remain implementation freedoms.

## Shared boundary values

Public cross-module values are immutable and infrastructure-neutral:
- opaque refs: ResourceRef, EndpointRef, SiteRef, ResponsibilityGroupRef, ApplicationRef, ComponentRef, InteractionRef, InteractionRevisionRef, DeploymentRef, ProcessRef, NeedRef, AccessRequestRef, PolicyRuleRef;
- Principal(subject, permissions);
- AddressRealization = HostAddress | Prefix;
- TrafficClause(protocol, sourcePortRanges, destinationPortRanges);
- Version/ETag;
- Problem/Error category values;
- MaterializationStatus = COMPLETE | UNRESOLVED.

These are contract values, not one shared mutable "common domain" module. Each owner publishes the minimum public representation required by consumers.

## Runtime/common components

### ApiServer

Responsibility: route HTTP requests, authenticate caller, decode/validate DTO shape, invoke one application entry point, map result/error to API Contract.

Dependencies: Authenticator, application entry points, ProblemMapper, CorrelationContext.

Forbidden: direct repositories/SQL, peer domain object mutation, authorization derived from DTO fields.

### Authenticator

Responsibility: validate OIDC bearer token and return Principal or authentication failure.

### Authorizer

Responsibility: answer `require(principal, permission)` fail-closed from trusted Principal permissions. It does not interpret Resource ownership or business responsibility.

### ConsistencyRunner

Application-owned abstraction implemented by relational infrastructure.

Contracts:
- `runWrite(operation)`: supplies transaction-bound owner write port(s) plus transaction-bound peer public read ports required by that use case; only declared owner tables may be written.
- `runReadSnapshot(operation)`: supplies transaction-bound read ports sharing one coherent snapshot plus evaluationAt.

The abstraction must not expose database connection/transaction framework types to application/domain code.

### Clock / IdGenerator

Narrow abstractions used only where accepted behavior needs current time/new opaque identity.

## Resource Description module

Public application components:
- ResourceCommandService
- ResourceQueryService
- SiteService
- ResponsibilityGroupService

Owner-internal persistence ports are consumer-shaped:
- ResourceRepository: load/save one Resource aggregate with optimistic version.
- SiteRepository: load/save Site.
- ResponsibilityGroupRepository: load/save group.
- ResourceHistoryReader: bounded owner history queries.

Public peer read port:
- ResourceResolutionPort:
  - resolveResource(ResourceRef)
  - currentEndpointAddresses(ResourceRef)
  - resolveResourceVersion(ResourceRef) where validation provenance requires it.

The public port returns owner-defined facts/provenance, never persistence rows.

## Application Communication module

Public components:
- ApplicationCommandService
- ApplicationQueryService
- InteractionRevisionService

Owner ports:
- ApplicationRepository
- InteractionRevisionReader

Public peer read port:
- CommunicationResolutionPort:
  - resolveComponent(ComponentRef) -> ApplicationRef + ComponentRef;
  - resolveInteractionRevision(InteractionRevisionRef) -> InteractionRef, sourceComponentRef, destinationComponentRef, immutable TrafficClauses, provenance;
  - resolveInteraction(InteractionRef) when Need validation requires it.

Published revisions are returned as immutable values.

## Application Deployment module

Public components:
- DeploymentCommandService
- DeploymentQueryService

Owner port:
- DeploymentRepository

Public peer read port:
- DeploymentResolutionPort:
  - resolveDeployment(DeploymentRef) -> ComponentRef, ResourceRef, provenance/version.

Registration consumes CommunicationResolutionPort and ResourceResolutionPort to validate references; it stores only stable refs.

## Business Connectivity module

Public components:
- BusinessProcessCommandService
- BusinessConnectivityQueryService

Owner port:
- BusinessProcessRepository

Public peer read port:
- ConnectivityNeedResolutionPort:
  - resolveCurrentNeed(NeedRef) -> ProcessRef, InteractionRef, needVersion, provenance;
  - resolveNeedHistorical(NeedRef) for explanation only.

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

Submission collaboration:
- Authorizer(access.request)
- ConnectivityNeedResolutionPort
- CommunicationResolutionPort
- DeploymentResolutionPort
- ConsistencyRunner.runWrite with one shared validation/write snapshot
- owner repositories/idempotency port.

Permission decision collaboration:
- Authorizer(access.decide)
- AccessRequestRepository + PolicyRuleRepository in one transaction.

Policy effect collaboration:
- Authorizer(access.manage)
- PolicyRuleRepository with expected Version.

Public peer read port:
- EffectivePolicyReadPort:
  - listCurrentActiveRules(snapshot cursor/page) -> stable rule subjects/provenance.

## Policy Materialization component

### CurrentPolicyMaterializer

Responsibility: compose owner facts into a complete vendor-neutral current policy result without owning any source truth.

Dependencies inside `ConsistencyRunner.runReadSnapshot`:
- EffectivePolicyReadPort
- CommunicationResolutionPort
- DeploymentResolutionPort
- ResourceResolutionPort

Algorithmic contract:
- resolve every active rule;
- expand address × TrafficClause combinations;
- preserve HOST/PREFIX and source/destination port semantics;
- preserve independent provenance;
- collect explicit unresolved issue per affected rule;
- return COMPLETE only when all active rules are fully resolved.

It has no write repository and no persistent materialization state in MVP.

## Persistence adapters

One adapter set per owner module implements only that module's persistence ports. A small relational ConsistencyRunner coordinates transaction lifetime/snapshot and binds module adapters to it.

Forbidden:
- generic repository returning arbitrary entities;
- direct SQL from application/domain;
- peer schema mutation;
- persistence row classes exposed through public module ports.

## API mapping

Dedicated request/response mappers convert:
- JSON strings -> validated opaque IDs/value objects;
- address/traffic JSON -> domain/application values;
- Version <-> ETag;
- application errors -> stable problem codes;
- Materialization result -> COMPLETE/UNRESOLVED response.

No automatic framework-to-domain object binding for mutable aggregates.

## Composition

Runtime composition constructs:
1. relational pool/data source;
2. owner repository adapters;
3. ConsistencyRunner;
4. OIDC Authenticator + Authorizer;
5. application services wired to narrow peer ports;
6. ApiServer;
7. observability/health adapters.

No service locator is accessible from domain/application code.

## Structural verification obligations

- import/dependency test: domain packages cannot import adapters/api/runtime;
- module test: one owner adapter cannot write/query private peer tables except via ConsistencyRunner-bound public read adapters;
- API test: handlers do not import concrete repositories;
- persistence contract tests for every consumer-shaped repository/read port;
- architectural test ensures Policy Materialization has no write persistence dependency.

## Implementation freedoms

Private function/class names, internal collection choices, SQL query shape/index tuning, JSON library details, DI wiring style at composition root, exact pagination token encoding, internal caching that preserves snapshot/consistency semantics, and local refactoring remain free.
