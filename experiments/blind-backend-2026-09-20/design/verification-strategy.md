# Backend verification strategy

Status: ACCEPTED after Source Corpus amendments 01–02

## Purpose

Prove that implementation realizes the accepted blind backend design and that IMPLEMENTATION can proceed without inventing material product/domain/architecture/interface/data/security/operability semantics.

Verification treats accepted artifacts as truth; implementation structure is never used to reinterpret them.

## V1 — Pure domain behavior

Evidence: deterministic unit/property/state-machine tests against public domain operations/value contracts.

Objectives:

### Resource Description
- Resource/Endpoint identity survives address change/clear.
- Missing current address is explicit.
- Site change/clear preserves history.
- At most one current OWNER and one current ADMINISTRATOR exist.
- Replacing/clearing responsibility closes prior history.
- Setting the already-current responsibility is a no-op.
- Site and ResponsibilityGroup are immutable in MVP.

### Application Communication
- Component belongs to one Application.
- Interaction is directed and may reference Components from different Applications.
- No same-Application invariant exists.
- Interaction subject is immutable.
- InteractionRevision is immutable; changing traffic semantics creates a new revision.
- Unsupported traffic semantics reject rather than widen.

### Business Connectivity
- Need is business justification, not permission.
- Need participantComponentRef must be one of its Interaction participants; source-side and destination-side Needs for the same Interaction remain independently representable.
- Need retirement is terminal and preserves history.
- Need currentness is independent from Access Policy state.

### Access Policy
- AccessSubject equality is exactly source Deployment + destination Deployment + exact InteractionRevision.
- NeedRef and technical Resource/address are not part of AccessSubject.
- AccessRequest subject/initial Need/provenance are immutable.
- one request finalizes once.
- PolicyRule first creation is ACTIVE/unbounded.
- operational state/window changes preserve Rule identity and authorization evidence.
- same normalized state/window is a no-op.
- authorization evidence is append-only and unique per AccessRequest.
- justification association is append-only and unique per Need.
- zero current Need does not change Rule operational state.

## V2 — Application orchestration

Evidence: public application-service contract tests using controlled owner ports.

Objectives:
- idempotency replay/conflict is resolved before NEW-command If-Match evaluation;
- Component creation mutates Application aggregate; Interaction creation mutates neither referenced Application;
- revision publication uses Interaction version;
- SubmitAccessRequest validates current Need, exact revision and Deployment direction in one snapshot;
- ALLOWED request finalization atomically resolves/creates one Rule by AccessSubject, appends evidence and initial justification;
- concurrent ALLOWED requests for equal AccessSubject converge on one Rule; each new AuthorizationEvidence on an existing Rule advances the Rule aggregate version exactly once;
- a later ALLOWED request for existing Rule does not reset state/window or append operational history, but does advance Rule version for the changed evidence/association set;
- additional Need attachment requires current matching Need + valid participantComponentRef, adds no permission evidence and changes no operational state;
- Need retirement is reflected on later Rule read/materialization without Access Policy mutation;
- zero current Need derives NO_CURRENT_BUSINESS_JUSTIFICATION, not automatic revocation;
- materialization selection supports all Rules or explicit Rule subset;
- INACTIVE/out-of-window selected Rule is excluded before technical realization checks;
- effective Rule missing required realization -> UNRESOLVED;
- dependency failure -> error, not UNRESOLVED;
- independent Rule provenance is never merged.

## V3 — PostgreSQL persistence/transaction integration

Evidence: tests against real supported PostgreSQL from a freshly migrated empty database.

Objectives:

### Ownership/constraints
- no cross-owner FK/write coupling;
- no `interaction.application_ref` or same-Application database constraint;
- Interaction source/destination Components may belong to different Applications;
- Application version guards Component creation only;
- Interaction version guards revision publication only;
- Resource version guards endpoint/address/Site/responsibility mutation;
- one open current OWNER and ADMINISTRATOR at most;
- address/Site/responsibility temporal intervals are valid/non-overlapping;
- BusinessProcess version guards organization/Need mutation.

### Access Policy
- unique AccessSubject constraint permits exactly one PolicyRule per subject;
- concurrent ALLOWED requests converge to that Rule;
- authorization evidence AccessRequest uniqueness enforced and evidence append participates in whole-Rule version serialization;
- Rule+Need association uniqueness enforced;
- Need status is not copied as authoritative state into Access Policy;
- ALLOWED request decision + Rule/evidence/initial justification commit atomically;
- operational history only records actual operational/window transitions;
- justification-only mutation increments Rule version but not operational history.

### Idempotency
- scope includes principal + method + route + normalized target + key;
- same-target same-key/same-fingerprint replays exact committed result;
- same scoped key/different fingerprint conflicts;
- same key on different target is independent;
- replay works even when original pre-mutation ETag is now stale;
- state and idempotency record commit atomically;
- concurrent identical commands create at most one authoritative state.

### Snapshot
- request/justification Need validation and Access Policy write observe one snapshot;
- materialization including Need currentness and Resource realization observes one coherent snapshot.

## V4 — HTTP/API contract

Evidence: black-box HTTP tests against composed backend + PostgreSQL + controlled identity provider.

Objectives:
- strict JSON rejects unknown/server-owned fields and invalid null/missing distinctions;
- every route uses exact accepted DTO/status/Location/ETag semantics;
- correlation id validation/generation/echo is exact;
- missing required If-Match -> 428; stale NEW command -> 409;
- exact idempotent replay occurs before stale ETag failure;
- Resource responsibility routes are role-addressed and preserve singular current role;
- cross-Application `POST /v1/interactions` succeeds;
- Interaction revision publication requires Interaction ETag, not Application ETag;
- Rule current response exposes bounded scalar counts + reconciliation flag; full authorization evidence and participant-attributed justifications are available through separate cursor-paged policy.read endpoints;
- Rule operational history endpoint exposes CREATED/OPERATIONAL_CHANGED events with actor/time/state/window, cursor-bounded, and no-op/evidence-only/justification-only changes create no operational event;
- Rule operational endpoint covers ACTIVE/INACTIVE + effectiveWindow;
- justification attachment is independently authorized/idempotent;
- policy materialization accepts all/subset selection;
- COMPLETE and UNRESOLVED are HTTP 200 application outcomes;
- INACTIVE/out-of-window Rules appear in nonEffective and produce no realization issue;
- missing current Need alone yields reconciliation flag, not MaterializationIssue;
- dependency failure -> 503;
- stable Problem mapping is exact.

## V5 — Security

Evidence: black-box permission matrix, OIDC fault injection and persistence-boundary tests.

Objectives:
- invalid credential -> 401, including permission claim wrong type/non-string elements;
- missing permission claim -> authenticated principal with empty permission set and therefore 403 on protected operation;
- inability to establish token validity due unusable key dependency -> 503;
- request/decide/manage/read/export permissions remain independent;
- Resource Owner/Admin, Process organization and Need existence never grant application authorization;
- operational/window change and Need attachment both require access.manage;
- subset export requires policy.export;
- current caller is re-authorized before idempotent replay;
- replay cannot be used to bypass current caller permission;
- caller cannot inject actor/permission/server-owned provenance;
- secrets/tokens/stacks/schema absent from public errors and representative logs;
- hostile text/network values never change SQL query shape.

## V6 — Architecture/component structure

Evidence: deterministic import/source/schema ownership checks.

Objectives:
- domain packages do not import HTTP/PostgreSQL/OIDC/telemetry/config;
- API does not import concrete repositories;
- owner adapters do not mutate peer schemas;
- ApplicationRepository does not own Interaction;
- InteractionRepository does not mutate Application rows during Interaction creation;
- Access Policy persistence does not store authoritative Need currentness;
- CurrentPolicyMaterializer has no write dependency;
- environment reads occur only at startup config/bootstrap;
- optimistic versions exist only on accepted aggregate owners:
  Resource, Application, Interaction, BusinessProcess, AccessRequest, PolicyRule;
- public peer ports expose owner facts, not persistence rows.

## V7 — Operability/configuration

Evidence: composed runtime tests with captured logs/metrics and fault injection.

Objectives:
- required startup env keys validate before listener;
- unknown NAPMS_* key fails startup;
- no config file/CLI/runtime reload path changes accepted configuration;
- OIDC retries/cache age are bounded exactly by config;
- no automatic database mutation retry;
- correlationId propagates through required events;
- required command/decision/materialization/dependency/shutdown evidence is observable without secrets;
- live is dependency-independent;
- ready reflects database + usable OIDC key material;
- request timeout/client cancellation reaches database/materialization;
- graceful shutdown drains then cancels at configured grace;
- committed state is never falsely reported rolled back.

## V8 — Fresh-start end-to-end

Evidence: empty PostgreSQL -> all migrations -> backend start with explicit config -> public HTTP only.

Positive journey intentionally exercises cross-Application communication:

1. create source/destination Resources, Endpoints and current addresses;
2. create Application A + source Component;
3. create Application B + destination Component;
4. create one directed Interaction from A.Component -> B.Component and publish immutable revision;
5. create source/destination ComponentDeployments;
6. create BusinessProcess + active source-participant Need for Interaction; optionally create destination-participant Need independently;
7. submit AccessRequest with request-only principal;
8. record ALLOWED with separate decide-only principal;
9. verify one ACTIVE/unbounded PolicyRule with authorization evidence + Need justification;
10. materialize with export-only principal -> HTTP 200 COMPLETE with exact rows/provenance.

Extended positive:
11. attach a second current Need from the other participant side with manage-only principal -> same PolicyRule, extra independently attributed justification;
12. set effective window outside now -> materialization COMPLETE with Rule in nonEffective and no technical row;
13. reactivate/effective window at now -> rows return without new permission decision.

Negative siblings:
- DENIED;
- reversed deployment direction;
- retired Need at submission/attachment;
- stale/missing ETag;
- idempotency conflict/different-target same key/replay after stale original ETag;
- missing realization for effective Rule -> HTTP 200 UNRESOLVED;
- missing realization for non-effective Rule -> COMPLETE with no issue;
- retire every attached Need -> Rule remains operationally unchanged and carries NO_CURRENT_BUSINESS_JUSTIFICATION;
- invalid OIDC token vs unavailable validation keys;
- cancellation/shutdown/config failure.

## Non-gates

No numeric latency/throughput/HA/RPO/RTO threshold is a correctness gate because none is accepted in source input. Measurements may be diagnostic only.
