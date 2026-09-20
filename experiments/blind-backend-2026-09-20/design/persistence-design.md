# Backend persistence design

Status: ACCEPTED candidate after Coding-Agent Challenge 01

## Ownership

One physical ACID relational database; logical table/schema ownership follows domain modules. No module may mutate another module's tables.

Cross-owner references are stored as opaque IDs and checked through public owner services on command submission. Database foreign keys do not cross owner schemas.

## Resource Description tables

- `site(site_ref PK, name, description nullable, created_at)`
- `responsibility_group(group_ref PK, display_name, external_reference nullable, created_at)`
- `resource(resource_ref PK, display_name, version, created_at)`
- `resource_site_history(resource_ref, effective_from, effective_to nullable, site_ref nullable, PK(resource_ref,effective_from))`
- `resource_endpoint(endpoint_ref PK, resource_ref, created_at)`
- `resource_endpoint_address_history(endpoint_ref, effective_from, effective_to nullable, kind, value, changed_by_subject, PK(endpoint_ref,effective_from))`
- `resource_responsibility_history(assignment_ref PK, resource_ref, role, group_ref, effective_from, effective_to nullable)`

Owner-local FKs:
- endpoint -> resource;
- site-history.site_ref -> site when non-null;
- responsibility.group_ref -> responsibility_group;
- Site/Group references never become authorization relations.

Required constraints:
- non-empty trimmed names/display names;
- address `kind` is HOST or PREFIX and value validates/normalizes accordingly before persistence;
- one open-ended Site-history row per Resource; registration creates an initial row, including `site_ref = null` when no Site is assigned;
- Site intervals for one Resource do not overlap;
- at most one open-ended current address row per Endpoint and address intervals do not overlap;
- each responsibility assignment has one interval and can be ended once;
- for each Resource/role there is at most one open-ended current assignment;
- replacing a current OWNER or ADMINISTRATOR closes the prior row and opens the new row in one Resource-version transaction;
- setting the same current group or clearing an already-empty role is a no-op;
- Resource `version` is the only optimistic-concurrency version for Resource, endpoint/address, Site-assignment and responsibility mutations.

Site and ResponsibilityGroup are immutable after registration in the selected MVP and need no optimistic-concurrency version.

## Application Communication tables

### Application aggregate

- `application(application_ref PK, name, version, created_at)`
- `component(component_ref PK, application_ref, name, created_at)`

Owner-local FK: Component -> Application.

Required constraints:
- Application/Component names are non-empty after trimming;
- Component belongs to exactly one Application;
- Application `version` guards Component creation only;
- Application/Component subject fields are immutable in selected MVP.

### Interaction aggregate

- `interaction(interaction_ref PK, source_component_ref, destination_component_ref, purpose nullable, version, created_at)`
- `interaction_revision(revision_ref PK, interaction_ref, revision_no, created_at, created_by_subject)`
- `interaction_traffic_clause(revision_ref, ordinal, protocol, source_port_from nullable, source_port_to nullable, destination_port_from nullable, destination_port_to nullable, PK(revision_ref,ordinal))`

Owner-local FKs may reference Component because Application and Interaction live inside the same Application Communication owner:
- source_component_ref -> component;
- destination_component_ref -> component;
- revision -> interaction.

There is deliberately **no** interaction.application_ref column and no constraint requiring source/destination Components to share an Application.

Required constraints:
- source and destination ComponentRefs both exist;
- revision number is unique within Interaction;
- every published revision has at least one TrafficClause;
- port bounds satisfy `0 <= from <= to <= 65535`;
- null port bounds mean unrestricted/non-applicable only according to accepted TrafficClause semantics;
- published revision rows/clauses are append-only;
- Interaction source/destination/purpose are immutable after creation;
- Interaction `version` guards revision publication only.

Creating Interaction performs validation + Interaction insert without updating either referenced Application row/version.

## Application Deployment

- `component_deployment(deployment_ref PK, component_ref, resource_ref, created_at)`

No address, label, mutable relocation, retirement or independent version columns are present. Cross-owner ComponentRef/ResourceRef remain opaque values without cross-schema FK.

## Business Connectivity

- `business_process(process_ref PK, name, description nullable, organization_external_reference nullable, organization_display_name nullable, version, created_at)`
- `connectivity_need(need_ref PK, process_ref, interaction_ref, participant_component_ref, business_basis, status, created_at, created_by_subject, retired_at nullable)`

Owner-local FK: Need -> BusinessProcess.

Required constraints:
- Process name and Need business basis are non-empty after trimming;
- interaction_ref and participant_component_ref are immutable cross-owner opaque references validated through Application Communication at Need creation;
- participant_component_ref must be one of the referenced Interaction participants at creation; no cross-owner FK is introduced;
- organization display name is non-empty whenever organization attribution is present;
- Need status is ACTIVE or RETIRED;
- ACTIVE requires `retired_at IS NULL`; RETIRED requires `retired_at IS NOT NULL`;
- RETIRED is terminal in the selected MVP;
- BusinessProcess `version` guards organization change, Need creation and Need retirement.

Organization fields are descriptive business attribution only. Criticality/importance columns are absent until Product Requirements defines that extension.

## Access Policy

### AccessRequest

`access_request(
  request_ref PK,
  source_deployment_ref,
  destination_deployment_ref,
  interaction_revision_ref,
  initial_need_ref,
  validated_business_process_version,
  submitter_subject,
  submitted_at,
  decision_result nullable,
  external_decision_ref nullable,
  decided_by_subject nullable,
  decided_at nullable,
  version
)`

Required constraints:
- semantic request subject + initial_need_ref + submission provenance are immutable;
- decision fields transition once from all-null to a complete ALLOWED or DENIED decision;
- decision fields are immutable after finalization;
- `decision_result` is null/ALLOWED/DENIED.

### PolicyRule

`policy_rule(
  rule_ref PK,
  source_deployment_ref,
  destination_deployment_ref,
  interaction_revision_ref,
  effect_state,
  effective_from nullable,
  effective_until nullable,
  version,
  created_at,
  UNIQUE(source_deployment_ref,destination_deployment_ref,interaction_revision_ref)
)`

Required constraints:
- unique tuple is the physical realization of blind-derived AccessSubject identity;
- effect_state is ACTIVE or INACTIVE;
- when both window bounds exist, `effective_from < effective_until`;
- subject columns and created_at are immutable;
- first Rule creation starts ACTIVE with null/unbounded window;
- later allowed evidence never resets operational columns.

### Authorization evidence

`policy_rule_authorization_evidence(
  rule_ref,
  access_request_ref UNIQUE,
  external_decision_ref nullable,
  decided_by_subject,
  decided_at,
  PK(rule_ref,access_request_ref)
)`

Owner-local FK to PolicyRule. AccessRequestRef remains an Access Policy-owned reference and may use owner-local FK.

Every row corresponds to one ALLOWED AccessRequest for the exact Rule AccessSubject. Evidence is append-only.

### Business justification associations

`policy_rule_justification(
  rule_ref,
  need_ref,
  attached_at,
  attached_by_subject,
  source_access_request_ref nullable,
  PK(rule_ref,need_ref)
)`

NeedRef is a cross-owner opaque reference: no database FK into Business Connectivity. Association is append-only in MVP. Need current/retired status is resolved dynamically through Business Connectivity owner reads.

### Operational history

`policy_rule_operational_history(
  rule_ref,
  version,
  effect_state,
  effective_from nullable,
  effective_until nullable,
  changed_by_subject,
  changed_at,
  PK(rule_ref,version)
)`

Initial Rule creation records version 1 ACTIVE/unbounded with changed_by_subject equal to the authenticated deciding principal and changed_at equal to creation/decision transaction time. Every actual state/window change increments Rule version and appends one row with authenticated managing principal/time. Same normalized state/window is a no-op. The API derives history kind CREATED for the initial row and OPERATIONAL_CHANGED for later rows.

### ALLOWED resolution/concurrency

Finalizing an ALLOWED AccessRequest performs in one transaction:

1. lock/update AccessRequest final decision under expected request version;
2. resolve/lock-or-create PolicyRule by unique AccessSubject;
3. when absent, insert Rule at version 1 with ACTIVE/unbounded state, initial operational-history CREATED row, first AuthorizationEvidence and initial Need association;
4. when Rule already exists, append the new AuthorizationEvidence, insert initial Need association if absent, preserve operational state/window, and increment PolicyRule version exactly once for this ALLOWED transaction;
5. an existing Rule increments version because its aggregate evidence/association set changed even when the Need association already existed;
6. no operational-history row is added for evidence/justification-only change;
7. commit request, Rule aggregate mutation and idempotency evidence atomically.

Concurrent ALLOWED requests for the same AccessSubject converge through the unique AccessSubject constraint plus PolicyRule row serialization. The transaction may use insert-on-conflict/select-for-update or an equivalent PostgreSQL strategy; this is not an application-level mutation retry. At most one Rule identity survives, and each newly appended AuthorizationEvidence advances Rule version once.

Justification attachment under expected PolicyRule version:
- validates current Need in the same transaction snapshot;
- inserts association if absent;
- if association already exists, returns semantic no-op without version/history change;
- otherwise increments PolicyRule version only if the accepted implementation treats association-set change as Rule aggregate mutation; if so, no operational-history row is added because operational state did not change.
Justification attachment increments PolicyRule version so concurrent Rule-management commands cannot silently cross; operational history remains unchanged for association-only mutation. AuthorizationEvidence append follows the same whole-aggregate version rule.

## API idempotency

`idempotency_record(
  principal_subject,
  http_method,
  route_template,
  target_key,
  key,
  request_fingerprint,
  response_status,
  response_body_or_result_ref,
  location nullable,
  response_etag nullable,
  committed_at,
  PK(principal_subject,http_method,route_template,target_key,key)
)`.

Definitions:
- `target_key` is the deterministic canonical concatenation/hash of normalized path-parameter values for that route; it prevents the same client key on different target Resources/Processes/Rules from colliding;
- request fingerprint covers canonical method/route/target plus normalized accepted JSON body;
- correlation id and If-Match are excluded from fingerprint.

Rules:
- authentication/authorization and strict body/target validation occur before idempotency lookup;
- for an existing same-key/same-fingerprint committed record, original status/body/Location/ETag replay occurs before current If-Match evaluation;
- same scoped key + different fingerprint -> IDEMPOTENCY_CONFLICT;
- NEW commands then evaluate If-Match and execute;
- idempotency row and authoritative mutation commit atomically;
- concurrent identical keys serialize through PK uniqueness/locking;
- if the competing first transaction commits, the waiter reads/replays its committed result;
- if the competing first transaction rolls back, the waiter may become NEW and only then evaluates If-Match/mutates;
- lock/wait is bounded by request + DB statement timeout;
- if the result cannot be established before timeout or because DB availability fails, return DEPENDENCY_UNAVAILABLE / HTTP 503;
- in-progress/unknown commit handling never fabricates success and never returns conflict solely because the identical command is still in progress.

## Transactions

### Isolation modes

**Owner write transaction**
- PostgreSQL `READ COMMITTED`;
- optimistic owner version/row locks enforce lost-update semantics;
- used for ordinary Resource/Application/Interaction/BusinessProcess/AccessRequest/PolicyRule owner mutations unless mutable peer-currentness validation below is required.

**Access Policy write with current-Need validation**
- also PostgreSQL `READ COMMITTED`;
- Business Connectivity transaction-bound read adapter executes `SELECT ... FOR SHARE` (or PostgreSQL-equivalent row share lock that conflicts with retirement/update) on the target ConnectivityNeed row;
- it verifies status ACTIVE plus Interaction/participant facts;
- the lock is held until the Access Policy transaction commits/rolls back;
- Access Policy writes no Business Connectivity table;
- Need retirement that wins first makes validation observe RETIRED; validation lock that wins first makes retirement wait until request/attachment commit;
- lock wait is bounded by request context and DB statement timeout.

This mode is mandatory for:
- SubmitAccessRequest initial Need;
- AttachPolicyRuleJustification additional Need.

Immutable peer Component/InteractionRevision/Deployment/Resource identity validation does not require peer row locking.

**Composed read snapshot**
- PostgreSQL read-only `REPEATABLE READ` or stronger;
- one snapshot shared by all involved owner read ports for that HTTP request/operation;
- used for composed PolicyRule current view/justification page where Need currentness is joined semantically, and for CurrentPolicyMaterializer;
- policy materialization keeps this snapshot open through both preflight and emit phases.

### Mutation rules

- every mutation writes only one semantic owner's tables;
- Resource nested changes use one Resource-version owner-write transaction;
- Application Component creation uses one Application-version owner-write transaction;
- Interaction creation validates immutable Components then inserts independently; revision publication uses one Interaction-version owner-write transaction;
- BusinessProcess child changes use one BusinessProcess-version owner-write transaction;
- final ALLOWED decision plus unique-subject PolicyRule resolve/create, authorization evidence, initial justification and idempotency result is one Access Policy transaction;
- Rule operational/justification mutation uses one expected PolicyRule version transaction;
- optimistic mutation uses `WHERE version = expected`; zero updated rows -> STALE_VERSION;
- no application-level automatic retry of a failed/unknown mutation.

### Materialization

CurrentPolicyMaterializer opens one read-only REPEATABLE READ transaction. Preflight and emit reuse exactly that snapshot/evaluationAt. Every owner read port, including Business Connectivity current-Need resolution, is bound to it.


## Migrations

- schema is created/evolved only by ordered versioned migrations;
- the migration runner records immutable applied migration identity; changing already-applied migration content is an error when checksum support is available;
- migration failure leaves the database at the last fully committed migration;
- destructive/irreversible future migration requires Change Transition Design; none is part of initial greenfield schema.

## Retention/data lifecycle

Domain history required by accepted semantics is authoritative and is not automatically expired. No personal-data retention/deletion requirement is present in the source corpus; privacy/retention policy remains DEFERRED until an applicable external/product obligation appears.
