# Backend persistence design

Status: ACCEPTED candidate

## Ownership

One physical ACID relational database; logical table/schema ownership follows domain modules. No module may mutate another module's tables.

Cross-owner references are stored as opaque IDs and checked through public owner services on command submission. Database foreign keys do not cross owner schemas.

## Resource tables

- `resource(resource_ref PK, display_name, site_ref nullable, version, created_at)`
- `resource_endpoint(endpoint_ref PK, resource_ref, version, created_at)`
- `resource_endpoint_address_history(endpoint_ref, effective_from, effective_to nullable, kind, value, provenance, PK(endpoint_ref,effective_from))`
- `resource_responsibility_history(assignment_ref PK, resource_ref, role, group_ref, effective_from, effective_to nullable)`
- `site(site_ref PK, name, description nullable)`

Constraint: one open-ended current address row per endpoint; non-overlapping effective intervals per endpoint. Equivalent temporal constraint for responsibility assignment identity.

## Application Communication tables

- `application(application_ref PK, name, version)`
- `component(component_ref PK, application_ref, name)`
- `interaction(interaction_ref PK, application_ref, source_component_ref, destination_component_ref, purpose, version)`
- `interaction_revision(revision_ref PK, interaction_ref, revision_no, created_at, provenance)`
- `interaction_traffic_clause(revision_ref, ordinal, protocol, port_from nullable, port_to nullable, PK(revision_ref,ordinal))`

Published revision rows are append-only.

## Application Deployment

- `component_deployment(deployment_ref PK, component_ref, resource_ref, label, created_at, retired_at nullable, version)`

No address columns are present.

## Business Connectivity

- `business_process(process_ref PK, name, description, organization_ref nullable, version)`
- `connectivity_need(need_ref PK, process_ref, interaction_ref, business_basis, status, created_at, retired_at nullable, version)`
- optional explicit criticality attributes use nullable typed columns only after API/domain acceptance; no computed propagation column.

## Access Policy

- `access_request(request_ref PK, source_deployment_ref, destination_deployment_ref, interaction_revision_ref, need_ref, submitter_subject, submitted_at, decision_result nullable, decision_ref nullable, decided_by_subject nullable, decided_at nullable, version)`
- `policy_rule(rule_ref PK, access_request_ref UNIQUE, source_deployment_ref, destination_deployment_ref, interaction_revision_ref, need_ref, decision_ref, effect_state, version, created_at)`
- `policy_rule_state_history(rule_ref, version, effect_state, changed_by_subject, changed_at, PK(rule_ref,version))`

Decision fields become immutable once non-null. A database constraint/check prevents decision value outside ALLOWED/DENIED.

## API idempotency

`idempotency_record(principal_subject, operation, key, request_fingerprint, response_status, response_body_or_result_ref, committed_at, PK(principal_subject,operation,key))`.

Same key + same fingerprint returns committed result; same key + different fingerprint is conflict. In-progress/unknown commit handling must not fabricate success.

## Transactions

- each command transaction includes aggregate rows/history + idempotency record when applicable;
- decision recording plus first PolicyRule insertion is one transaction;
- optimistic update uses `WHERE version = expected` then increments version;
- policy materialization opens one read-only REPEATABLE READ transaction and all owner read ports share that transaction/snapshot.

## Migrations

- schema is created/evolved only by ordered versioned migrations;
- migration is deterministic and safe to re-run only when explicitly designed idempotent; otherwise migration runner records applied version exactly once;
- destructive/irreversible migration requires future Change Transition Design; none is part of initial greenfield schema.

## Retention/data lifecycle

Domain history required by accepted semantics is authoritative and not automatically expired. No personal-data retention/deletion requirement is present in source corpus; privacy/retention policy is DEFERRED until applicable external/product obligation appears.
