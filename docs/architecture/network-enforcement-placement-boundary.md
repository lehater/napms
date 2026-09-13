# Network Enforcement Placement Boundary — I19

Status: `accepted historical implementation boundary; current NEP target semantics are owned by ADR-018 and target Tactical DDD`.

Date: 2026-09-13.

## Purpose

Document the existing NEP module/dependency boundary while keeping provider mechanics outside the core and Access Policy Realization policy semantics downstream.

This file does not define APR inputs or target-selection semantics for APR. Current NEP target semantics are canonical in `docs/domain/network-enforcement-placement/target-tactical-model.md`; APR consumes the published target-specific outcome without importing NEP reasoning.

## Target module

```text
backend/src/napms/network_enforcement_placement/
    domain/
        model.py
        selection.py
    application/
        ports.py
        select.py
    adapters/
        local_import.py
        postgres/
```

## Dependency direction

```text
NEP Domain
    ^
    |
NEP Application + NEP-owned ports
    ^
    |
outer adapters / composition
    |
    +--> provider/network source parsing
    +--> PostgreSQL persistence
    +--> optional owner projections where needed
```

Rules:
- NEP Domain imports no peer bounded context, framework, DB, transport, configuration or logging type;
- NEP Application imports only NEP Domain + NEP-owned protocols;
- source adapters translate provider-native path/device/interface material into NEP-owned references;
- provider/device identifiers stay opaque correspondence/provenance values;
- APR/RC/ACC/TAE do not become dependencies of NEP Domain/Application;
- no peer-owned SQL/table access.

## Existing runtime query

The existing runtime still contains the older `SelectEnforcement` query shape and stronger placement knowledge structures. They are implementation/migration material, not the current APR contract and not a reason to reproduce their status vocabulary downstream.

The accepted current NEP target is defined by ADR-018 and `docs/domain/network-enforcement-placement/target-tactical-model.md`.

## PostgreSQL ownership

NEP owns its persistence schema and acquisition/runtime state. No Access Policy, APR, RC, ACC or TAE private tables are read directly by NEP core.

Cross-context consumers receive published NEP outputs/contracts rather than navigating NEP persistence.

## APR boundary

APR receives the target/policy-locator information selected upstream. APR does not:
- rerun NEP routing/candidate logic;
- classify why a target was relevant;
- reinterpret route/candidate ambiguity;
- infer a different target from NEP internal evidence.

Once a target-specific contract crosses the boundary, APR's concern is required-vs-configured effective policy realization for that supplied target.

## Runtime scope

NEP core does not require APR rendering, APR reconciliation or provider mutation clients.

A later operator workflow may consume NEP application contracts without changing ownership.

## Validation guardrails

- framework-free Domain/Application boundary;
- provider/Firewall identity separation according to the accepted target model;
- explicit uncertainty rather than invented target certainty;
- module-owned persistence and no cross-context SQL;
- no Access Policy/Decision/TAE/APR side effects;
- no downstream context may treat an internal NEP runtime status vocabulary as its own domain model.
