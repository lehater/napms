# NAPMS Strategic DDD model

Status: `accepted living baseline`.

Source baseline: DDD-BDM-010, extended by accepted MVP decisions through ADR-018.

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
| **Network Enforcement Placement** | which enforcement devices and policy attachment points are relevant for a technical source/destination pair? | target relevance from current network state and overrides, applicable policy/ACL locators, provenance and collection state |
| **Technical Access Evidence** | what technical access material did a source report? | immutable source-qualified normalized technical evidence with source/scope/time/provenance; no authorization claim |
| **Access Policy Realization** | how exactly does configured effective access on a given target realize required effective access, and what verified policy change is needed? | effective-policy realization assessment, exact semantic reconciliation, policy-change design, pre-change semantic verification and semantics-preserving target rendering |

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

ADR-018 defines the current MVP Network Enforcement Placement target. NEP owns deciding which Firewalls/policy locators are relevant for supplied traffic pairs. APR consumes the resulting target-specific contract without reevaluating why a target was selected.

## Access Policy Realization strategic boundary

The current APR problem statement is canonical in:

- `docs/domain/access-policy-realization/README.md`.

Strategically:

- target selection/relevance is upstream of APR;
- APR compares **effective access semantics**, not raw configuration text or rule identity;
- required and configured policy sides must refer to a trustworthy comparable target/scope;
- APR owns the semantic difference between those sides and the policy-change reasoning built on that difference;
- APR may verify and render a proposed change, but provider/device mutation execution remains downstream;
- large-set computation may be data-local without transferring semantic ownership of upstream facts to APR;
- physical database co-location does not authorize APR to depend on peer-private persistence schemas.

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

Access Policy + Resource Catalogue + Application Communication Catalogue
                         + Network Enforcement Placement
                                      |
                                      | published target-specific required-policy input
                                      v
                         Access Policy Realization
                                      ^
                                      |
                         published configured effective-policy input
                                      |
                         Technical Access Evidence / source adapters
                                      |
                                      v
                         verified/rendered policy change
                                      |
                                      v
                         Network Environment Operations
```

The arrows above express contracts, not table ownership. APR does not reinterpret NEP relevance and does not acquire authority over Access Policy, catalogue, placement or evidence facts.

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

Access Policy + Resource Catalogue + Application Communication Catalogue
                         + Network Enforcement Placement
                                      |
                                      v
                         Access Policy Realization
                                      ^
                                      |
                         configured effective-policy input
                                      |
                         Technical Access Evidence / source adapters
                                      |
                                      v
                         Network Environment Operations
```

## Rules

- A Bounded Context is not a service/deployment unit.
- Connectivity Requirements and Connectivity Decision are outside MVP scope per ADR-016.
- Access Policy owns authoritative Access Rule identity/state and is the MVP authorization truth.
- Resource Scope Affiliation does not imply actor authority; actor authority for a scope does not imply Resource membership.
- NEP owns target relevance and policy/ACL location semantics; APR does not second-guess target selection.
- Technical evidence is not authorization.
- APR compares effective policy behavior, not textual/configuration decomposition.
- Technical realization changes do not redefine Rule semantic identity.
- If post-MVP Requirement/Decision capabilities are reintroduced, they must not redefine existing Access Rule semantic identity.
- Strategic DDD is revisited when new evidence changes language, lifecycle, authority or responsibility boundaries.
