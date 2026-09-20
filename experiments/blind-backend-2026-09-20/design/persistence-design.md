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
- `resource_endpoint_address_history(endpoint_ref, effective_from, effective_to nullable, kind, value, provenance, PK(endpoint_ref,effective_from))`
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
- Resource `version` is the only optimistic-concurrency version for Resource, endpoint/address, Site-assignment and responsibility mutations.

Site and ResponsibilityGroup are immutable after registration in the selected MVP and need no optimistic-concurrency version.

## Application Communication tables

- `application(application_ref PK, name, version, created_at)`
- `component(component_ref PK, application_ref, name, created_at)`
- `interaction(interaction_ref PK, application_ref, source_component_ref, destination_component_ref, purpose nullable, created_at)`
- `interaction_revision(revision_ref PK, interaction_ref, revision_no, created_at, provenance)`
- `interaction_traffic_clause(revision_ref, ordinal, protocol, source_port_from nullable, source_port_to nullable, destination_port_from nullable, destination_port_to nullable, PK(revision_ref,ordinal))`

Owner-local FKs ensure Component and Interaction children belong to Application and revisions belong to Interaction.

Required constraints:
- Application/Component names are non-empty after trimming;
- revision number is unique within Interaction;
- every published revision has at least one TrafficClause;
- port bounds satisfy `0 <= from <= to <= 65535`;
- null port bounds mean unrestricted/non-applicable only according to accepted TrafficClause semantics; unknown semantics cannot be stored as unrestricted;
- published revision rows/clauses are append-only;
- Application `version` is the only optimistic-concurrency version for Component/Interaction/revision creation.

## Application Deployment

- `component_deployment(deployment_ref PK, component_ref, resource_ref, created_at)`

No address, label, mutable relocation, retirement or independent version columns are present. Cross-owner ComponentRef/ResourceRef remain opaque values without cross-schema FK.

## Business Connectivity

- `business_process(process_ref PK, name, description nullable, organization_external_reference nullable, organization_display_name nullable, version, created_at)`
- `connectivity_need(need_ref PK, process_ref, interaction_ref, business_basis, status, created_at, retired_at nullable)`

Owner-local FK: Need -> BusinessProcess.

Required constraints:
- Process name and Need business basis are non-empty after trimming;
- organization display name is non-empty whenever organization attribution is present;
- Need status is ACTIVE or RETIRED;
- ACTIVE requires `retired_at IS NULL`; RETIRED requires `retired_at IS NOT NULL`;
- RETIRED is terminal in the selected MVP;
- BusinessProcess `version` guards organization change, Need creation and Need retirement.

Organization fields are descriptive business attribution only. Criticality/importance columns are absent until Product Requirements defines that extension.

## Access Policy

- `access_request(request_ref PK, source_deployment_ref, destination_deployment_ref, interaction_revision_ref, need_ref, validated_business_process_version, submitter_subject, submitted_at, decision_result nullable, decision_ref nullable, decided_by_subject nullable, decided_at nullable, version)`
- `policy_rule(rule_ref PK, access_request_ref UNIQUE, source_deployment_ref, destination_deployment_ref, interaction_revision_ref, need_ref, decision_ref nullable, effect_state, version, created_at)`
- `policy_rule_state_history(rule_ref, version, effect_state, changed_by_subject, changed_at, PK(rule_ref,version))`

Required constraints:
- AccessRequest subject/provenance columns are immutable after insert;
- `decision_result` is null, ALLOWED or DENIED;
- decision fields change from all-null to one complete final decision at most once and are immutable afterward;
- ALLOWED decision and first PolicyRule insert commit in the same transaction;
- one AccessRequest has at most one PolicyRule through `access_request_ref UNIQUE`;
- PolicyRule effect is ACTIVE or INACTIVE;
- PolicyRule subject/provenance columns are immutable;
- PolicyRule history receives one row for initial ACTIVE state and every actual later effect-state transition;
- semantic no-op SetRuleEffect does not increment version or append history.

## API idempotency

`idempotency_record(principal_subject, operation, key, request_fingerprint, response_status, response_body_or_result_ref, location nullable, committed_at, PK(principal_subject,operation,key))`.

Rules:
- key lexical validation is enforced at the HTTP boundary;
- fingerprint is deterministic over the accepted operation and canonical request body;
- same key + same fingerprint returns the original committed semantic result;
- same key + different fingerprint -> conflict;
- idempotency record and authoritative state created by that command commit atomically;
- in-progress/unknown commit handling never fabricates success.

## Transactions

- every mutation writes only one semantic owner's tables;
- Resource nested changes use one Resource-version transaction;
- Application child/revision creation uses one Application-version transaction;
- BusinessProcess child changes use one BusinessProcess-version transaction;
- SubmitAccessRequest performs peer validation reads plus the Access Policy insert in one database transaction snapshot; peer schemas are read-only;
- decision recording plus first PolicyRule insertion is one Access Policy transaction;
- optimistic mutation uses `WHERE version = expected`; zero updated rows -> STALE_VERSION;
- policy materialization opens one read-only REPEATABLE READ transaction and every owner read port shares that snapshot; backend assigns `evaluationAt` for that current snapshot.

## Migrations

- schema is created/evolved only by ordered versioned migrations;
- the migration runner records immutable applied migration identity; changing already-applied migration content is an error when checksum support is available;
- migration failure leaves the database at the last fully committed migration;
- destructive/irreversible future migration requires Change Transition Design; none is part of initial greenfield schema.

## Retention/data lifecycle

Domain history required by accepted semantics is authoritative and is not automatically expired. No personal-data retention/deletion requirement is present in the source corpus; privacy/retention policy remains DEFERRED until an applicable external/product obligation appears.
