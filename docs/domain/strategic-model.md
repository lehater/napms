# NAPMS Strategic DDD model

Status: `accepted living baseline`.

Source baseline: DDD-BDM-010, extended by I13-I19 accepted domain closure.

This document defines model/language/responsibility boundaries. It does not define services, databases, teams or deployment units.

## Bounded Contexts

| Bounded Context | Semantic center | Responsibility |
|---|---|---|
| **Connectivity Requirements** | what semantic connectivity is needed? | connectivity-need identity/lifecycle, required interaction, applicability and justification/provenance |
| **Connectivity Decision** | may this exact proposed semantic connectivity be used as permission for Access Policy materialization? | immutable final Allowed/NotAllowed decision identity, scope, validity, reason/provenance and supersession |
| **Access Policy** | what network access is authorized to exist? | authoritative Access Rule identity, uniqueness/idempotency, properties, Active/Inactive, decision consumption and desired-policy projections |
| **Authority Management** | who may perform a domain action for scope/time? | scoped actor/action authority, Responsibility Assignment, delegation/transfer/revocation and accountability |
| **Resource Catalogue** | what access-domain resources exist, to which responsibility scopes do they belong, and how are they realized? | Resource/Endpoint identity, time-qualified Resource Scope Affiliation, current/historical realization and access-relevant lifecycle facts |
| **Application Communication Catalogue** | which application/component interactions are structurally valid? | Application/Component/Deployment/DCS identities and protocol/port contracts |
| **Network Enforcement Placement** | where is traffic subject to enforcement? | forwarding/path knowledge, Logical Firewall correspondence and enforcement attachments |
| **Technical Access Evidence** | what technical access material did a source report? | immutable source-qualified normalized technical evidence with source/scope/time/provenance; no authorization/currentness claim |
| **Access Policy Realization** | how does authorized/domain access correspond to technical enforcement? | technical↔domain resolution, enforcement-policy derivation/optimization and desired-vs-configured reconciliation |

## Historical Wave-1 participation

Wave 1 directly used:
- Access Policy;
- Authority Management;
- Application Communication Catalogue;
- Resource Catalogue;
- an external Connectivity Decision semantic seam.

That seam was intentionally deferred during Wave 1 and is superseded by the I15 first-class Connectivity Decision context.

## Current semantic participation through I19

Current accepted semantic owners participating in implemented product flow include:
- Connectivity Requirements;
- Connectivity Decision;
- Access Policy;
- Authority Management;
- Application Communication Catalogue;
- Resource Catalogue;
- Technical Access Evidence;
- Access Policy Realization.

Technical Access Evidence has the I17 Tactical DDD, framework-free core, module-owned PostgreSQL persistence and strict local/import proof. It remains independent from authorization and from technical-to-domain interpretation.

Access Policy Realization now has the I18 Technical-to-Domain Access Resolution slice: one framework-free consumer-independent coverage algebra over explicit TAE/RC/ACC projections, with exact remainder, ambiguity and predicate-relevant Unknown semantics and no independent persistence.

Network Enforcement Placement now has the accepted I19 Tactical DDD baseline: exact endpoint-pair Traffic Relation, normalized ordered path Traversal Points, stable Logical Firewall identity, temporal provider correspondence, temporal Enforcement Attachments and fail-closed Enforcement Selection. I19 implementation is in progress; APR enforcement-policy derivation/reconciliation remains later I20 scope.

## I16A responsibility-scope relationship

I16A makes an existing responsibility boundary explicit without adding a Bounded Context.

```text
Resource Catalogue
    Resource --Resource Scope Affiliation--> Responsibility Scope reference

Authority Management
    Actor --Responsibility Assignment(action,time)--> Responsibility Scope reference
```

The shared Responsibility Scope reference correlates the facts; it does not merge ownership.

- Resource Catalogue owns which Resources belong to scope S at time T.
- Authority Management owns whether actor A may perform action X for scope S at time T.
- current catalogue visibility is independent from both.
- one Resource may belong to multiple responsibility scopes without changing Resource identity.
- changing Resource Scope Affiliation does not silently rewrite Requirement, Decision or Rule governance scope.

`Scoped Connectivity Inventory` is a non-peer application/read composition over these owners plus ACC, Connectivity Requirements, Connectivity Decision and Access Policy.

## Core dependency map

```text
Connectivity Requirements
        |
        | need/evidence (does not authorize)
        v
Connectivity Decision <----- Authority Management
        |
        | effective Allowed | NotAllowed
        v
Access Policy <----- Application Communication Catalogue
    ^   ^
    |   |
    |   +----- Authority Management
    |
Resource Catalogue

Technical Access Evidence ---> Access Policy Realization <--- Access Policy
                                      ^
                                      |
                    Resource Catalogue + Application Communication Catalogue
                                      ^
                                      |
                         Network Enforcement Placement
```

## Rules

- A Bounded Context is not a service/deployment unit.
- Declared connectivity need is not authorization.
- Connectivity Decision owns final decision reason/validity/supersession; Access Policy does not.
- Proposal authority does not imply decision authority.
- Resource Scope Affiliation does not imply actor authority; actor authority for a scope does not imply Resource membership.
- A Decision may reference a Connectivity Requirement as evidence; `Required != Allowed`.
- Access Policy owns authoritative Access Rule identity/state.
- Decision expiry/supersession does not silently mutate an existing Access Rule.
- Technical evidence is not authorization.
- Technical realization changes do not redefine Rule semantic identity.
- Strategic DDD is revisited when new evidence changes language, lifecycle, authority or responsibility boundaries.
