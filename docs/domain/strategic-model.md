# NAPMS Strategic DDD model

Status: `accepted living baseline`.

Source baseline: DDD-BDM-010, extended by I13-I15 accepted domain closure.

This document defines model/language/responsibility boundaries. It does not define services, databases, teams or deployment units.

## Bounded Contexts

| Bounded Context | Semantic center | Responsibility |
|---|---|---|
| **Connectivity Requirements** | what semantic connectivity is needed? | connectivity-need identity/lifecycle, required interaction, applicability and justification/provenance |
| **Connectivity Decision** | may this exact proposed semantic connectivity be used as permission for Access Policy materialization? | immutable final Allowed/NotAllowed decision identity, scope, validity, reason/provenance and supersession |
| **Access Policy** | what network access is authorized to exist? | authoritative Access Rule identity, uniqueness/idempotency, properties, Active/Inactive, decision consumption and desired-policy projections |
| **Authority Management** | who may perform a domain action for scope/time? | scoped authority, assignment/delegation/transfer/revocation and accountability |
| **Resource Catalogue** | what access-domain resources exist and how are they realized? | Resource/Endpoint identity, current/historical realization and access-relevant lifecycle facts |
| **Application Communication Catalogue** | which application/component interactions are structurally valid? | Application/Component/Deployment/DCS identities and protocol/port contracts |
| **Network Enforcement Placement** | where is traffic subject to enforcement? | forwarding/path knowledge, Logical Firewall correspondence and enforcement attachments |
| **Technical Access Evidence** | what technical access material did a source report? | normalized source-qualified technical evidence with provenance/time/freshness/coverage |
| **Access Policy Realization** | how does authorized/domain access correspond to technical enforcement? | technical↔domain resolution, enforcement-policy derivation/optimization and desired-vs-configured reconciliation |

## Historical Wave-1 participation

Wave 1 directly used:
- Access Policy;
- Authority Management;
- Application Communication Catalogue;
- Resource Catalogue;
- an external Connectivity Decision semantic seam.

That seam was intentionally deferred during Wave 1 and is superseded by the I15 first-class Connectivity Decision context.

## Current product participation through I15

Current accepted semantic owners participating in implemented/planned product flow include:
- Connectivity Requirements;
- Connectivity Decision;
- Access Policy;
- Authority Management;
- Application Communication Catalogue;
- Resource Catalogue.

Network Enforcement Placement, Technical Access Evidence and Access Policy Realization remain strategic product contexts for later roadmap increments.

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
- A Decision may reference a Connectivity Requirement as evidence; `Required != Allowed`.
- Access Policy owns authoritative Access Rule identity/state.
- Decision expiry/supersession does not silently mutate an existing Access Rule.
- Technical evidence is not authorization.
- Technical realization changes do not redefine Rule semantic identity.
- Strategic DDD is revisited when new evidence changes language, lifecycle, authority or responsibility boundaries.
