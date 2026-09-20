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
- TrafficClause(ipProtocol:uint8, canonicalSourcePortRanges, canonicalDestinationPortRanges);
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
- enforce configured HTTP request-body byte limit, then strictly decode Interface DTOs;
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

OIDC adapter contract:
- enforces HTTPS-only configured issuer/discovery/jwks_uri with downgrade rejection, then validates exact configured allowed algorithms, issuer, audience, exp/nbf skew, sub and permission-claim shape from Security Architecture;
- exposes `initializeValidationMaterial()` used before listener start;
- owns one single-flight bounded metadata/JWKS refresh path shared by initialization/readiness/protected validation;
- preserves max-stale/fail-closed 401-vs-503 semantics from Operability/Security.

### Authorizer

`require(principal, permission)` checks only the exact configured permission string. No implicit permission hierarchy; Resource responsibility and Business Process organization never grant application authorization.

### ETagCodec

Opaque HTTP ETag <-> AggregateVersion mapping. Numeric/internal version is not externally meaningful.

### ConsistencyRunner

Application-owned transaction abstraction implemented by PostgreSQL infrastructure:

- `runWrite(owner, operation)`: PostgreSQL READ COMMITTED, one transaction-bound owner write set + declared transaction-bound peer read ports;
- `runReadSnapshot(operation)`: PostgreSQL read-only REPEATABLE READ (or stronger); its first database statement establishes the snapshot and returns database `transaction_timestamp()` as evaluationAt; all declared read ports share that exact snapshot/time.

Rules:
- only declared semantic owner tables may be written;
- DB transaction types do not leak inward;
- request cancellation/deadline propagates;
- no automatic mutation retry;
- transaction-bound peer ports may acquire read locks only when an accepted consistency contract requires them; this does not grant peer write ownership.

### IdempotentCommandGuard / IdempotencyPort

Input:
- principal subject;
- HTTP method;
- canonical route template;
- normalized target/path key;
- Idempotency-Key;
- deterministic canonical accepted-body fingerprint.

Decision:
- REPLAY -> exact persisted committed response status + canonical JSON body bytes + Location + ETag; current mutable state is never used to reconstruct replay;
- CONFLICT -> same scoped key, different fingerprint;
- NEW -> command may continue to If-Match/domain mutation;
- UNKNOWN/TIMEOUT -> never fabricate success.

Normative ordering for operations also requiring If-Match:
1. auth + strict target/body validation;
2. idempotency lookup;
3. REPLAY/CONFLICT ends processing;
4. only NEW validates current aggregate version.

The guard is transaction-bound for NEW commands so exact replay bytes/metadata commit atomically with owner state. Committed idempotency records are not expired by this MVP.

### Clock / IdGenerator

Narrow injectable abstractions only where accepted behavior needs current time/new opaque identity. CurrentPolicyMaterializer does not use the application Clock for evaluationAt; that timestamp comes from ConsistencyRunner's database transaction snapshot.

### MigrationRunner / SchemaVerifier

The binary has two runtime modes:

- `migrate`: MigrationRunner acquires one exclusive PostgreSQL advisory lock, verifies applied migration ids/checksums, applies pending migrations transactionally in order, and records id+checksum atomically.
- `serve`: SchemaVerifier performs read-only exact expected-set/checksum validation; it never applies DDL/migrations.

No listener is opened in migrate mode. Serve refuses to open a listener when schema state is pending/missing/unknown/checksum-mismatched.

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
- ResourceEndpointReader: cursor-page EndpointView facts for one Resource;
- ResourceHistoryReader: cursor-bounded address/Site/responsibility history.

Public `ResourceResolutionPort`:
- `resolveResource(ResourceRef)`;
- `currentEndpointAddresses(ResourceRef)` -> all current addressed endpoints with address/effectiveFrom/changedBySubject.

Responsibility set/clear is a Resource aggregate operation and enforces at most one current OWNER and ADMINISTRATOR.

## Application Communication module

Public services:
- ApplicationCommandService
- ApplicationQueryService
- InteractionCommandService
- InteractionQueryService

Owner ports:
- `ApplicationRepository`: load/save Application under expected Application version for Component creation;
- `ApplicationComponentReader`: cursor-page Components for one Application;
- `InteractionRepository`: insert Interaction; load/save Interaction under expected Interaction version for revision publication;
- `InteractionRevisionReader`: exact immutable revision lookup + cursor-page revision summaries for one Interaction.

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
- `resolveInteractionRevision(InteractionRevisionRef)` -> InteractionRef, source/destination ComponentRefs, immutable TrafficClauses, createdAt, createdBySubject.

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

Owner ports:
- BusinessProcessRepository: load/save Process under expected BusinessProcess version;
- BusinessProcessNeedReader: cursor-page Need summaries for one Process.

Public `ConnectivityNeedResolutionPort`:
- `lockAndResolveCurrentNeed(NeedRef)` — valid only inside transaction-bound Access Policy write validation; acquires owner-side PostgreSQL FOR SHARE-equivalent row lock blocking Need retirement/update until transaction end, then returns ProcessRef, InteractionRef, participantComponentRef, businessProcessVersion, businessBasis, createdAt, createdBySubject or explicit NOT_CURRENT;
- `resolveNeed(NeedRef)` -> ProcessRef, InteractionRef, participantComponentRef, businessBasis, ACTIVE|RETIRED, createdAt, createdBySubject, retiredAt;
- `resolveNeeds(set<NeedRef>)` -> same current/historical facts including participantComponentRef in caller-supplied read snapshot.

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
- append AuthorizationEvidence uniquely by AccessRequestRef and advance PolicyRule aggregate version exactly once when adding new evidence to an existing Rule;
- append JustificationAssociation uniquely by NeedRef;
- update operational state/window;
- read operational/evidence/association history;
- page operational history for the public PolicyRule history query.

Unique AccessSubject convergence is enforced in persistence; repository never creates two stable Rules for equal subject.

### AccessPolicyReadPort

Bounded read contracts:

- `readRuleCore(PolicyRuleRef)` -> RuleRef, AccessSubject, effectState/effectiveWindow/version, authorizationEvidenceCount, justificationCount;
- `pageAllRuleCores(cursor,limit)`;
- `readRuleCores(set<PolicyRuleRef>)` for explicit materialization selection, internally chunked as needed; Interface imposes no semantic rule-count cap beyond request-body bytes;
- `pageAuthorizationEvidence(PolicyRuleRef,cursor,limit)` -> AccessRequestRef + submittedBySubject/submittedAt/initialNeedRef + decision provenance;
- `pageJustificationAssociations(PolicyRuleRef,cursor,limit)`;
- `pageOperationalHistory(PolicyRuleRef,cursor,limit)`.

Rule core never embeds unbounded child collections. Justification associations contain NeedRefs/attachment provenance only and do **not** claim current/retired Need status.

For CurrentPolicyMaterializer, `pageAllRuleCores`, `pageAuthorizationEvidence` and `pageJustificationAssociations` are iterated inside the one shared read snapshot. Export emits complete per-Rule permission/business provenance once per selected Rule; normalized technical rows reference PolicyRuleRef rather than repeating those unbounded audit arrays.

### SubmitAccessRequest collaboration

Inside Access Policy `runWrite`:
- Authorizer(`access.request`);
- IdempotentCommandGuard;
- ConnectivityNeedResolutionPort.lockAndResolveCurrentNeed;
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

ALLOWED finalization + Rule/evidence/association + idempotency evidence are atomic. New Rule starts version 1. Existing Rule is row-serialized; adding new AuthorizationEvidence advances Rule version once, preserves operational state/window and adds no operational-history row.

### PolicyRule operational collaboration

- Authorizer(`access.manage`);
- PolicyRuleRepository under expected version;
- same normalized state/window -> no-op, unchanged version/history.

### Additional justification collaboration

Inside one Access Policy write transaction:
- Authorizer(`access.manage`);
- IdempotentCommandGuard before NEW-command Rule-version check;
- ConnectivityNeedResolutionPort.lockAndResolveCurrentNeed;
- CommunicationResolutionPort to verify Need Interaction vs Rule revision Interaction and participantComponentRef membership;
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

Within one `runReadSnapshot` transaction/snapshot:

**Preflight**
1. obtain selected Rule cores: page all cores for ALL mode or chunk the explicit Rule set supplied within the configured request-body bound;
2. evaluate INACTIVE/effectiveWindow;
3. for every selected Rule, page AuthorizationEvidence and justification associations; batch-resolve every referenced Need and build complete per-Rule export provenance; any unresolved accepted provenance reference yields REFERENCE_UNRESOLVABLE even if the Rule is non-effective;
4. only for selected effective Rules, resolve exact revision/deployment/resource/current-address technical facts using bounded reads;
5. determine nonEffective entries, stable MaterializationIssues and final COMPLETE/UNRESOLVED;
6. complete every required dependency read before any HTTP response is committed;
7. retain only compact preflight state needed to start emission, not the full normalized row set or full audit arrays.

**Emit**
8. repeat deterministic bounded traversal in the same snapshot;
9. stream nonEffective/issues/rows for the preflight-determined result;
10. emit complete MaterializedRuleProvenance once per selected Rule, then rows correlate by RuleRef and preserve explicit technical actor/time facts; paginated policy.read remains an additional audit surface.

Dependency/runtime failure in preflight propagates before response commitment. Transport/cancellation failure after commit aborts the stream; no valid complete export is fabricated.

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
- Resource endpoints/history, Application components, Interaction revisions, Process Needs and all PolicyRule child-history cursors;
- AccessSubject/evidence/justification views;
- COMPLETE/UNRESOLVED/nonEffective/reconciliation representations.

## Composition root

### migrate mode
1. StartupConfigLoader in migrate profile;
2. PostgreSQL pool;
3. MigrationRunner;
4. exit success/failure; no OIDC/application services/listener.

### serve mode
1. StartupConfigLoader in serve profile;
2. PostgreSQL pool;
3. SchemaVerifier exact migration-set/checksum check;
4. OIDC Authenticator initial validation-material acquisition;
5. owner adapters + ConsistencyRunner;
6. IdempotencyPort;
7. Authorizer;
8. application services/peer ports;
9. CurrentPolicyMaterializer;
10. ApiServer;
11. observability/health/shutdown adapters.

Any schema/OIDC initialization failure aborts before listener creation.

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
