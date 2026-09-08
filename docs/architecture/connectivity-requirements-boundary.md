# Connectivity Requirements architecture boundary — I13

Status: `accepted I13 WP3 architecture contract`.

Date: 2026-09-09.

## Purpose

Define the executable module/dependency boundary for the first Connectivity Requirements slice.

This document defines dependency direction and cross-context ports. It does not prescribe service count or future deployment topology.

## Module boundary

Target source layout:

```text
src/napms/connectivity_requirements/
    domain/
        model.py
    application/
        ports.py
        declare.py
        read.py
        set_applicability.py
        set_justification.py
        retire.py
        proposal_options.py
    adapters/
        postgres/
        authority_management.py
        application_catalogue.py
```

Dependency direction:

```text
Connectivity Requirements Domain
        ^
        |
Connectivity Requirements Application + consumer-owned Ports
        ^
        |
Adapters / Composition / HTTP
```

Domain/Application do not import FastAPI, psycopg, runtime config, logging or adapter types.

## Cross-context dependencies

I13 uses only:

```text
Authority Management
        |
        v
Connectivity Requirements
        ^
        |
Application Communication Catalogue
```

I13 does **not** depend on:
- Access Policy;
- Connectivity Decision;
- Resource Catalogue;
- Technical Access Evidence;
- Access Policy Realization;
- Network Enforcement Placement.

Requirement-to-Policy Alignment is I14 composition and must not leak into I13.

## Authority consumer ports

Connectivity Requirements owns its action vocabulary:

```text
DeclareConnectivityRequirement
ReadConnectivityRequirement
SetConnectivityRequirementApplicability
SetConnectivityRequirementJustification
RetireConnectivityRequirement
```

Consumer port:

```text
RequirementAuthorityPort.check(
    actorId,
    action,
    scope,
    effectiveTime
) -> Permitted | Denied | Unknown + authorityReference
```

Read/declaration scope discovery uses consumer-owned discovery ports backed by Authority Management's effective-scope query.

Rules:
- Authority Management remains semantic owner of assignment/effective authority;
- Connectivity Requirements owns which domain action it asks about;
- permitted without one provenance/reference fails closed to Unknown;
- caller scope is accepted only for declaration/scope discovery;
- later mutation/detail uses the Requirement's stored governance scope.

## ACC consumer ports

### Exact interaction validation

```text
RequirementInteractionCataloguePort.validate(
    RequiredSemanticInteraction,
    effectiveTime
) -> Valid | Invalid | Unknown + provenanceReference
```

The adapter translates between Connectivity Requirements' local value type and ACC's DirectedInteractionIdentity.

No ACC type enters Connectivity Requirements Domain/Application.

### Interaction discovery

For the future I13 Web declaration form, a separate consumer query port may list/search structurally valid exact interactions.

It can reuse the existing ACC list/search application capability through an adapter, but returns Connectivity Requirements-owned DTOs.

Discovery is an application convenience and does not establish authority by itself; the enclosing CR declaration-composition use case evaluates `DeclareConnectivityRequirement` authority first.

## Persistence port

Connectivity Requirements owns its repository abstraction.

Minimum persistence capabilities:

```text
find_active_by_semantic_key(key)
get_by_id(requirementId)
list_by_governance_scopes(scopes, offset, limit)
add(requirement)
save(requirement, expectedVersion)
commit()
```

Persistence exceptions must distinguish at least:
- execution failure where success is not established;
- commit outcome unknown;
- active semantic uniqueness conflict;
- stale aggregate version conflict.

Business meaning:
- one Active Requirement per active semantic key;
- Retired history does not block a later new lifecycle episode.

Exact SQL/locking mechanics remain adapter choices but must prove these semantics.

## Application use cases

### DeclareConnectivityRequirement

Order:
1. validate request-local value shapes;
2. check declaration authority for requested governance scope/effective time;
3. validate exact interaction through ACC;
4. verify Dependent participates;
5. resolve existing Active Requirement by semantic key;
6. otherwise create;
7. persist/commit;
8. on uniqueness race resolve exact winning Active Requirement.

No Access Policy/Decision side effect.

### SetConnectivityRequirementApplicability

1. load Requirement;
2. check authority against stored scope;
3. reject Retired;
4. same value -> no-op;
5. apply immutable aggregate change with audit;
6. save with expected version;
7. commit.

### SetConnectivityRequirementJustification

Same pattern as applicability with its distinct Authority action.

### RetireConnectivityRequirement

Same pattern with terminal `Active -> Retired`.

### List/Get

List:
- discover unambiguous effective read scopes;
- page over Requirements in those scopes.

Detail:
- load Requirement;
- check read authority against stored scope;
- return no business data on denied/unknown authority.

## Aggregate version

I13 admits an integer authoritative aggregate version as concurrency metadata.

Rules:
- declaration starts at version 1;
- each accepted property/lifecycle mutation increments by one;
- no-op does not increment;
- version is not domain identity and is not business lifecycle state;
- callers do not obtain permission by supplying a version;
- persistence may expose stale-version conflict for safe optimistic concurrency.

## Audit ownership

Business audit entries are aggregate/domain state persisted atomically with accepted mutations.

Runtime request logs remain technical observability only.

## Composition

The greenfield PostgreSQL composition root may wire:
- AM adapter -> Requirement authority/discovery ports;
- ACC adapter -> exact interaction/discovery ports;
- PostgresRequirementRepository.

The existing AM/ACC modules are reused; no peer service boundary is implied.

## Architecture guardrails

- no Connectivity Requirements -> Access Policy import;
- no Connectivity Requirements -> runtime/FastAPI/psycopg import in core;
- no ACC/AM domain model types in Connectivity Requirements Domain;
- no hidden ownership-based authorization;
- no Pending/Approved/Rejected lifecycle;
- no technical address/vendor syntax in Requirement identity;
- no event bus introduced without a real consumer requirement.

## WP3 exit

The implementation gate opens when:
- Tactical model is accepted;
- behavioral requirements/examples are accepted;
- this dependency/port contract is accepted.

All three conditions are now satisfied for I13.
