# NAPMS Strategic DDD model

Status: `accepted living baseline`.

Source baseline: DDD-BDM-010, accepted 2026-09-08.

This document defines model/language/responsibility boundaries. It does not define services, databases, teams or deployment units.

## Bounded Contexts

| Bounded Context | Semantic center | Responsibility |
|---|---|---|
| **Connectivity Requirements** | what semantic connectivity is needed? | connectivity-need identity/lifecycle, required interaction, applicability and justification/provenance |
| **Access Policy** | what network access is authorized to exist? | authoritative Access Rule identity, uniqueness/idempotency, properties, Active/Inactive, decision consumption and desired-policy projections |
| **Authority Management** | who may perform a domain action for scope/time? | scoped authority, assignment/delegation/transfer/revocation and accountability |
| **Resource Catalogue** | what access-domain resources exist and how are they realized? | Resource/Endpoint identity, current/historical realization and access-relevant lifecycle facts |
| **Application Communication Catalogue** | which application/component interactions are structurally valid? | Application/Component/Deployment/DCS identities and protocol/port contracts |
| **Network Enforcement Placement** | where is traffic subject to enforcement? | forwarding/path knowledge, Logical Firewall correspondence and enforcement attachments |
| **Technical Access Evidence** | what technical access material did a source report? | normalized source-qualified technical evidence with provenance/time/freshness/coverage |
| **Access Policy Realization** | how does authorized/domain access correspond to technical enforcement? | technical↔domain resolution, enforcement-policy derivation/optimization and desired-vs-configured reconciliation |

## Current Wave-1 participation

Wave 1 directly uses:
- Access Policy;
- Authority Management;
- Application Communication Catalogue;
- Resource Catalogue;
- an external Connectivity Decision semantic seam.

Connectivity Requirements, Network Enforcement Placement, Technical Access Evidence and Access Policy Realization remain strategic product contexts but are not automatically Wave-1 deployment/runtime modules.

## Core dependency map

```text
Connectivity Requirements
        |
        | need (does not authorize)
        v
Connectivity Decision (external/deferred domain seam)
        |
        | Allowed | NotAllowed for exact Rule semantic identity
        v
Authority Management -----> Access Policy <----- Application Communication Catalogue
                                  ^
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
- Technical evidence is not authorization.
- Access Policy owns authoritative Access Rule identity/state.
- Connectivity Decision reasons/workflow are outside Access Policy.
- Technical realization changes do not redefine Rule semantic identity.
- Strategic DDD is revisited when new evidence changes language, lifecycle, authority or responsibility boundaries.
