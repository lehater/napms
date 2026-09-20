# Backend component design

Status: ACCEPTED after Source Corpus amendment 02

## Design intent

Expose implementation-facing responsibilities and narrow ports so a coding agent can realize the accepted design without reassigning semantic ownership. Private helpers, concrete collections, query plans and local algorithms remain implementation freedoms.

## Shared contract values

Infrastructure-neutral values crossing module boundaries:
- opaque refs: ResourceRef, EndpointRef, SiteRef, ResponsibilityGroupRef, ApplicationRef, ComponentRef, InteractionRef, InteractionRevisionRef, DeploymentRef, ProcessRef, NeedRef, AccessRequestRef, PolicyRuleRef;
- Principal(subject, permissions);
- AggregateVersion;
- AccessSubject(sourceDeploymentRef,destinationDeploymentRef,interactionRevisionRef);
- AddressRealization = HostAddress | Prefix;
- TrafficClause(protocol, sourcePortRanges, destinationPortRanges);
- EffectiveWindow(effectiveFrom?,effectiveUntil?);
- NeedStatus = ACTIVE | RETIRED;
- MaterializationStatus = COMPLETE | UNRESOLVED;
- MaterializationIssueCode;
- ReconciliationFlag = NO_CURRENT_BUSINESS_JUSTIFICATION.

These are owner-published contract values, not one shared mutable domain model.

## Runtime/platform components

### StartupConfigLoader

Reads/validates the exact Operability Design `NAPMS_*` environment contract once before listener creation and returns immutable RuntimeConfig.

Forbidden: configuration files/CLI precedence, runtime reload, environment reads from domain/application code, hidden defaults for required timeout/retry values.

### ApiServer

Responsibilities:
- route HTTP;
- establish/validate correlation id;
- authenticate caller;
- authorize exact operation permission;
- strictly decode Interface DTOs;
- enforce Idempotency-Key and If-Match presence/shape;
- invoke application service;
- map accepted result/error to exact status/body/Location/ETag/Problem.

Dependencies: Authenticator, Authorizer, ETagCodec, CorrelationContext, application services, ProblemMapper.

Forbidden: direct repositories/SQL, automatic DTO-to-domain binding, caller-controlled principal/permission, fallback semantics not present in Interface Design.

### Authenticator

Result:
- Authenticated(Principal);
- InvalidCredential -> 401;
- IdentityDependencyUnavailable -> 503.

OIDC metadata/JWKS fetch/cache mechanics obey Security + Operability max-attempt/max-stale/fail-closed semantics.

### Authorizer

`require(principal, permission)` checks only the exact configured permission string. No implicit permission hierarchy; Resource responsibility and Business Process organization never grant application authorization.

### ETagCodec

Opaque HTTP ETag <-> AggregateVersion mapping. Numeric/internal version is not externally meaningful.

### ConsistencyRunner

Application-owned transaction abstraction implemented by PostgreSQL infrastructure:

- `runWrite(owner, operation)`: one transaction-bound owner write set + declared peer read ports in the same database snapshot;
- `runReadSnapshot(operation)`: all declared read ports on one coherent read-only snapshot + evaluationAt.

Rules:
- only declared semantic owner tables may be written;
- DB transaction types do not leak inward;
- request cancellation/deadline propagates;
- no automatic mutation retry.

### IdempotentCommandGuard / IdempotencyPort

Input:
- principal subject;
- HTTP method;
- canonical route template;
- normalized target/path key;
- Idempotency-Key;
- deterministic canonical accepted-body fingerprint.

Decision:
- REPLAY -> original committed semantic result/status/body/Location/ETag;
- CONFLICT -> same scoped key, different fingerprint;
- NEW -> command may continue to If-Match/domain mutation;
- UNKNOWN/TIMEOUT -> never fabricate success.

Normative ordering for operations also requiring If-Match:
1. auth + strict target/body validation;
2. idempotency lookup;
3. REPLAY/CONFLICT ends processing;
4. only NEW validates current aggregate version.

The guard is transaction-bound for NEW commands so idempotency evidence commits atomically with owner state.

### Clock / IdGenerator

Narrow injectable abstractions only where accepted behavior needs current time/new opaque identity.

## Resource Description module

Public services:
- ResourceCommandService
- ResourceQueryService
- SiteService
- ResponsibilityGroupService

Owner ports:
- ResourceRepository: load/save one Resource aggregate by expected Resource version, including endpoint/Site/responsibility current state and history append;
- SiteRepository: register/read immutable Site;
- ResponsibilityGroupRepository: register/read immutable group;
- ResourceHistoryReader: cursor-bounded address/Site/responsibility history.

Public `ResourceResolutionPort`:
- `resolveResource(ResourceRef)`;
- `currentEndpointAddresses(ResourceRef)` -> all current addressed endpoints with address/effectiveFrom/provenance.

Responsibility set/clear is a Resource aggregate operation and enforces at most one current OWNER and ADMINISTRATOR.

## Application Communication module

Public services:
- ApplicationCommandService
- ApplicationQueryService
- InteractionCommandService
- InteractionQueryService

Owner ports:
- `ApplicationRepository`: load/save Application under expected Application version for Component creation;
- `InteractionRepository`: insert Interaction; load/save Interaction under expected Interaction version for revision publication;
- `InteractionRevisionReader`: immutable exact-revision lookup.

Interaction creation collaboration:
- Authorizer(`application.write`);
- IdempotentCommandGuard;
- two read-only `resolveComponent` calls;
- insert one independent Interaction aggregate;
- no Application row/version is mutated.

Revision publication collaboration:
- Authorizer(`application.write`);
- IdempotentCommandGuard before NEW-command Interaction ETag validation;
- InteractionRepository under expected Interaction version;
- append immutable revision/TrafficClauses.

Public `CommunicationResolutionPort`:
- `resolveComponent(ComponentRef)` -> ComponentRef + owning ApplicationRef;
- `resolveInteraction(InteractionRef)` -> source/destination ComponentRefs;
- `resolveInteractionRevision(InteractionRevisionRef)` -> InteractionRef, source/destination ComponentRefs, immutable TrafficClauses, createdAt/provenance.

No public contract assumes source/destination Components share an Application.

## Application Deployment module

Public services:
- DeploymentCommandService
- DeploymentQueryService

Owner port:
- DeploymentRepository: insert/read immutable ComponentDeployment.

Public `DeploymentResolutionPort`:
- `resolveDeployment(DeploymentRef)` -> ComponentRef, ResourceRef, createdAt.

## Business Connectivity module

Public services:
- BusinessProcessCommandService
- BusinessConnectivityQueryService

Owner port:
- BusinessProcessRepository: load/save Process under expected BusinessProcess version.

Public `ConnectivityNeedResolutionPort`:
- `resolveCurrentNeed(NeedRef)` -> ProcessRef, InteractionRef, businessProcessVersion, businessBasis, createdAt/provenance or explicit NOT_CURRENT;
- `resolveNeed(NeedRef)` -> ProcessRef, InteractionRef, businessBasis, ACTIVE|RETIRED, createdAt/retiredAt/provenance;
- `resolveNeeds(set<NeedRef>)` -> same current/historical facts in caller-supplied snapshot.

Access Policy stores NeedRef associations only; it never persists copied Need status/currentness.

## Access Policy module

Public services:
- AccessRequestCommandService
- PermissionDecisionCommandService
- PolicyRuleCommandService
- AccessPolicyQueryService

Owner ports:

### AccessRequestRepository
- insert immutable pending request;
- load under expected AccessRequest version;
- finalize exactly once.

### PolicyRuleRepository
- `resolveOrCreateBySubject(AccessSubject)` -> stable PolicyRuleRef; new Rule initializes ACTIVE/unbounded;
- load Rule under expected PolicyRule version;
- append AuthorizationEvidence uniquely by AccessRequestRef;
- append JustificationAssociation uniquely by NeedRef;
- update operational state/window;
- read operational/evidence/association history.

Unique AccessSubject convergence is enforced in persistence; repository never creates two stable Rules for equal subject.

### AccessPolicyReadPort
For one snapshot:
- `readRule(PolicyRuleRef)`;
- `readAllRules()`;
- `readRules(set<PolicyRuleRef>)`.

Returned owner facts include:
- PolicyRuleRef + AccessSubject;
- effectState/effectiveWindow/version;
- all AuthorizationEvidence;
- all JustificationAssociation refs/provenance.

It does **not** claim current/retired Need status.

### SubmitAccessRequest collaboration

Inside Access Policy `runWrite`:
- Authorizer(`access.request`);
- IdempotentCommandGuard;
- ConnectivityNeedResolutionPort.resolveCurrentNeed;
- CommunicationResolutionPort;
- DeploymentResolutionPort;
- AccessRequestRepository.

### PermissionDecision collaboration

Inside one Access Policy write transaction:
- Authorizer(`access.decide`);
- IdempotentCommandGuard before NEW-command request-version check;
- AccessRequestRepository;
- PolicyRuleRepository.resolveOrCreateBySubject;
- append authorization evidence;
- append initial Need justification if absent.

ALLOWED finalization + Rule/evidence/association + idempotency evidence are atomic.

### PolicyRule operational collaboration

- Authorizer(`access.manage`);
- PolicyRuleRepository under expected version;
- same normalized state/window -> no-op, unchanged version/history.

### Additional justification collaboration

Inside one Access Policy write transaction:
- Authorizer(`access.manage`);
- IdempotentCommandGuard before NEW-command Rule-version check;
- ConnectivityNeedResolutionPort.resolveCurrentNeed;
- CommunicationResolutionPort to verify Need Interaction vs Rule revision Interaction;
- PolicyRuleRepository append unique Need association;
- new association increments Rule version; already-associated Need is no-op/replay.

No justification delete/detach component exists in MVP.

## Policy Materialization component

### CurrentPolicyMaterializer

Responsibilities within `runReadSnapshot`:

Dependencies:
- AccessPolicyReadPort;
- ConnectivityNeedResolutionPort.resolveNeeds;
- CommunicationResolutionPort;
- DeploymentResolutionPort;
- ResourceResolutionPort.

Algorithmic contract:
1. obtain all Rules or exact selected Rule set;
2. evaluate INACTIVE/effectiveWindow before technical realization requirements;
3. resolve every associated Need through Business Connectivity and derive current/retired status;
4. add `NO_CURRENT_BUSINESS_JUSTIFICATION` when current Need count is zero, without altering effectiveness;
5. for every effective Rule resolve exact revision/deployments/resources/current endpoints;
6. produce stable realization issues only for effective Rules;
7. expand source endpoint × destination endpoint × TrafficClause exactly;
8. preserve Rule identity, all authorization evidence, all justification/currentness, reconciliation flags and technical provenance;
9. COMPLETE iff all selected effective Rules are resolvable; otherwise UNRESOLVED;
10. propagate dependency/runtime failure rather than convert it to UNRESOLVED.

No write repository or durable materialization state exists.

## Persistence adapters

One adapter set per semantic owner plus relational ConsistencyRunner/IdempotencyPort.

Forbidden:
- generic repository across semantic owners;
- peer table mutation;
- persistence rows through public ports;
- copied Business Connectivity currentness in Access Policy;
- child-specific concurrency versions contradicting aggregate ownership;
- application-level mutation retry to resolve uniqueness/conflict.

## HTTP mapping boundary

Dedicated codecs/mappers own:
- strict DTO decoding/null/unknown-field rules;
- canonical idempotency target/fingerprint derivation;
- replay-before-If-Match orchestration;
- AggregateVersion/ETag;
- Problem/status mapping;
- Resource history cursor;
- AccessSubject/evidence/justification views;
- COMPLETE/UNRESOLVED/nonEffective/reconciliation representations.

## Composition root

Constructs:
1. StartupConfigLoader -> RuntimeConfig;
2. PostgreSQL pool;
3. owner adapters + ConsistencyRunner;
4. IdempotencyPort;
5. OIDC Authenticator + Authorizer;
6. application services/peer ports;
7. CurrentPolicyMaterializer;
8. ApiServer;
9. observability/health/shutdown adapters.

No service locator reaches domain/application code.

## Structural verification obligations

- domain packages cannot import HTTP/PostgreSQL/OIDC/telemetry/config;
- API handlers cannot import concrete repositories;
- owner adapters cannot mutate peer schemas;
- Access Policy code cannot persist/cache Need currentness as authoritative data;
- CurrentPolicyMaterializer has no write dependency;
- only Resource/Application/Interaction/BusinessProcess/AccessRequest/PolicyRule aggregates expose mutable versions;
- environment reads occur only at startup config/bootstrap;
- public HTTP DTOs do not appear in domain packages;
- resolve-or-create Rule uniqueness is owned by Access Policy persistence, not a generic global service.

## Implementation freedoms

Private Go type/function/file names, internal collections, SQL query/index strategy, exact upsert/locking implementation preserving one Rule per AccessSubject, JSON/OIDC/logging libraries, DI wiring, cursor encoding, test helpers and local refactoring remain free.
