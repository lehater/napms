# Network Enforcement Placement Boundary — I19

Status: `accepted I19 WP-0 architecture contract`.

Date: 2026-09-09.

## Purpose

Define the first module/dependency boundary for Network Enforcement Placement while keeping provider mechanics outside the core and I20 Access Policy Realization semantics downstream.

## Target module

```text
src/napms/network_enforcement_placement/
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
    +--> optional RC/ACC projection for domain-attributable proof
```

Rules:
- NEP Domain imports no peer bounded context, framework, DB, transport, configuration or logging type;
- NEP Application imports only NEP Domain + NEP-owned protocols;
- source adapters translate provider-native path/device/interface material into NEP-owned references;
- provider/device identifiers stay opaque correspondence/provenance values;
- APR/RC/ACC/TAE do not become dependencies of NEP Domain/Application;
- no peer-owned SQL/table access.

## Application query

`SelectEnforcement` receives:
- exact source IP;
- exact destination IP;
- explicit offset-aware `asOf`;
- optional opaque caller provenance.

It obtains one NEP-owned `PlacementKnowledgeSnapshot` from a consumer-owned knowledge port.

## Placement knowledge port

Minimum shape:

```text
load_for(source_ip, destination_ip, asOf)
    -> PlacementKnowledgeSnapshot
         path | noForwardingPath
         logicalFirewalls[]
         correspondences[]
         attachments[]
         completeForPair
         completeForAttachments
         knowledgeGaps[]
```

The port may be backed by NEP-owned PostgreSQL facts plus source-specific adapters. It must not convert missing data into false absence.

## First durable adapter

The first concrete acquisition path may be a strict local JSON import used only as trusted composition proof.

It must:
- reject duplicate JSON object keys;
- reject unknown fields;
- require explicit source/capture/provenance;
- require offset-aware validity timestamps;
- represent path completeness explicitly;
- reject multiple path alternatives as unsupported rather than picking one;
- normalize provider-native references into opaque source-qualified NEP references.

It is not a public human API and does not imply Authority Management semantics.

## PostgreSQL ownership

I19 may add one NEP-owned schema, expected `napms_network_enforcement_placement`.

Persistence owns only NEP facts:
- Logical Firewall identity/lifecycle;
- temporal provider correspondences;
- temporal Enforcement Attachments;
- normalized forwarding-path facts/source provenance.

No Access Policy, APR, RC, ACC or TAE tables are read directly.

## Composition proof

The smallest accepted end-to-end proof is:

```text
strict local NEP knowledge import
    -> NEP-owned PostgreSQL
    -> SelectEnforcement(exact endpoint pair, asOf)
    -> Placed / NoEnforcement / NoForwardingPath / Ambiguous / Unknown
```

A domain-attributable test may carry an opaque Domain Interaction/Resource provenance reference into the query, but NEP core does not import those owner types.

## Failure semantics

- invalid input invariant -> explicit domain/application error;
- missing/incomplete relevant knowledge -> successful `Unknown` result with gaps;
- positively known no route -> `NoForwardingPath`;
- complete route with complete zero attachment -> `NoEnforcement`;
- non-unique Logical Firewall at a traversed attachment -> `Ambiguous`;
- persistence corruption/commit uncertainty -> fail closed; never report a complete selection.

## Runtime scope

I19 requires no:
- public HTTP route;
- Web workspace;
- background scheduler;
- vendor renderer;
- provider mutation client.

A later operator workflow can consume the same application contract without changing NEP meaning.

## Validation

Required executable proof:
- framework-free Domain/Application boundary;
- exact logical-time validation;
- provider/LF identity separation;
- ordered multi-placement selection;
- `NoForwardingPath != NoEnforcement != Unknown`;
- ambiguity with no winner;
- strict import rejection;
- module-owned PostgreSQL and no cross-context SQL;
- no Access Policy/Decision/TAE/APR side effects.
