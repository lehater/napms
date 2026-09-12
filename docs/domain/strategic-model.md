# NAPMS Strategic DDD model

Status: `accepted living baseline`.

Source baseline: DDD-BDM-010, extended by accepted MVP decisions through ADR-017.

This document defines model/language/responsibility boundaries. It does not define services, databases, teams or deployment units.

## Bounded Contexts

| Bounded Context | Semantic center | Responsibility |
|---|---|---|
| **Connectivity Requirements** | what semantic connectivity is needed? | connectivity-need identity/lifecycle, required interaction, applicability and justification/provenance |
| **Connectivity Decision** | may this exact proposed semantic connectivity be used as permission for Access Policy materialization? | immutable final Allowed/NotAllowed decision identity, scope, validity, reason/provenance and supersession |
| **Access Policy** | what network access is authorized to exist? | authoritative Access Rule identity, uniqueness/idempotency, properties, Active/Inactive and desired-policy projections |
| **Authority Management** | who may perform a domain action for scope/time? | scoped actor/action authority, Responsibility Assignment, delegation/transfer/revocation and accountability |
| **Resource Catalogue** | what access-domain resources exist, to which responsibility scopes do they belong, and how are they realized? | Resource/Endpoint identity, time-qualified Resource Scope Affiliation, current/historical realization and access-relevant lifecycle facts |
| **Application Communication Catalogue** | which application/component interactions are structurally valid? | Application/Component/Deployment/DCS identities and protocol/port contracts |
| **Network Enforcement Placement** | which enforcement devices and policy attachment points are relevant candidates for a technical source/destination pair? | unordered candidate relevance, source-supported ingress/egress interface context, policy/ACL attachment locators, Logical Firewall correlation, provenance and knowledge gaps |
| **Technical Access Evidence** | what technical access material did a source report? | immutable source-qualified normalized technical evidence with source/scope/time/provenance; no authorization/currentness claim |
| **Access Policy Realization** | how does authorized/domain access correspond to technical enforcement? | technical↔domain resolution, enforcement-policy derivation/optimization and desired-vs-configured reconciliation |

## MVP scope

ADR-016 removes the following contexts from the MVP target:

- **Connectivity Requirements**;
- **Connectivity Decision**.

They remain valid strategic concepts for possible post-MVP growth, but MVP use cases, APIs, UI, persistence and target-context contracts must not depend on them.

For MVP, authorization flows directly from an Authority Management-admitted action over a valid ACC-published interaction subject to an authoritative Access Rule:

```text
Application Communication Catalogue
        |
        | valid DirectedInteractionIdentity
        v
Access Policy <----- Authority Management
```

An Access Rule is therefore the MVP authorization truth. Separate required-but-not-authorized and `Allowed | NotAllowed` decision lifecycles are post-MVP concerns.

ADR-017 defines the MVP Network Enforcement Placement contract as an unordered candidate set. NEP must not infer a forwarding route from indirect relevance evidence. For every candidate it may expose source-supported ingress/egress interface references and zero-or-more policy/ACL attachment locators. Configured policy contents remain owned by Technical Access Evidence.

## Historical Wave-1 participation

Wave 1 directly used:
- Access Policy;
- Authority Management;
- Application Communication Catalogue;
- Resource Catalogue;
- an external Connectivity Decision semantic seam.

That seam was intentionally deferred during Wave 1 and was later implemented as the I15 first-class Connectivity Decision context. ADR-016 subsequently removes that context from the MVP target while preserving the implementation as current/historical runtime until cleanup.

## Implemented semantic participation through I20

The implemented product flow historically/currently includes:
- Connectivity Requirements;
- Connectivity Decision;
- Access Policy;
- Authority Management;
- Application Communication Catalogue;
- Resource Catalogue;
- Technical Access Evidence;
- Access Policy Realization.

This list describes implemented/runtime participation, not MVP target scope.

Technical Access Evidence has the I17 Tactical DDD, framework-free core, module-owned PostgreSQL persistence and strict local/import proof. It remains independent from authorization and from technical-to-domain interpretation.

Access Policy Realization now has the I18 Technical-to-Domain Access Resolution slice: one framework-free consumer-independent coverage algebra over explicit TAE/RC/ACC projections, with exact remainder, ambiguity and predicate-relevant Unknown semantics and no independent persistence.

Network Enforcement Placement has the implemented I19 stronger Tactical DDD/runtime slice with exact endpoint-pair Traffic Relation, normalized ordered path Traversal Points, stable Logical Firewall identity, temporal provider correspondence, temporal Enforcement Attachments and fail-closed Enforcement Selection. I26 added weaker unordered candidate semantics. ADR-017 makes the candidate contract, enriched with relevant interfaces and policy/ACL attachment locators, the MVP target; the proven-path model remains optional stronger/current-runtime capability.

Access Policy Realization now also has the implemented I20 derivation/reconciliation slice. Effective desired Access Policy + shared I18 domain resolution + NEP placement are correlated with explicitly selected configured evidence only through an exact managed reconciliation-scope/source contract. Complete Add/Remove/Replace/No-op claims require same-target/same-managed-partition correlation, exact time and trustworthy configured effective-policy completeness. The implementation remains derived on demand through owner-preserving adapters/owner-backed PostgreSQL composition with no APR persistence; I21 rendering and I22 execution remain downstream.

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
- changing Resource Scope Affiliation does not silently rewrite stored governance scope.

`Scoped Connectivity Inventory` is a non-peer application/read composition. Its MVP form must not require Connectivity Requirements or Connectivity Decision.

## MVP dependency map

```text
Access Policy <----- Application Communication Catalogue
    ^
    |
    +----- Authority Management
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

NEP and TAE correlate at the downstream composition boundary through source-qualified device/policy locators; NEP owns relevance/location, while TAE owns configured policy contents.

## Full-domain / post-MVP-capable dependency map

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
- Connectivity Requirements and Connectivity Decision are outside MVP scope per ADR-016.
- Access Policy owns authoritative Access Rule identity/state and is the MVP authorization truth.
- Resource Scope Affiliation does not imply actor authority; actor authority for a scope does not imply Resource membership.
- NEP candidate membership does not prove traffic traversal or route order.
- NEP owns device/interface/policy attachment relevance, not ACL/policy contents.
- Technical evidence is not authorization.
- Technical realization changes do not redefine Rule semantic identity.
- If post-MVP Requirement/Decision capabilities are reintroduced, they must not redefine existing Access Rule semantic identity.
- Strategic DDD is revisited when new evidence changes language, lifecycle, authority or responsibility boundaries.
