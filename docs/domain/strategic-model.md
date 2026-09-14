# NAPMS Strategic DDD model

Status: `S2 strategic revalidation in progress`.

Source baseline: DDD-BDM-010, revalidated by 2026-09-14 G1 requirements, ADR-019 and ADR-020.

This document defines model/language/responsibility boundaries. It does not define services, databases, teams or deployment units.

## Current target Bounded Contexts

| Bounded Context | Semantic center | Responsibility |
|---|---|---|
| **Business Connectivity** | why is application connectivity needed by the business? | Business Process meaning/responsibility, application-semantic Connectivity Need, business attribution and justification reconciliation |
| **Access Governance** | has a concrete deployed interaction received and retained the required consent? | Access Request history, source/destination approval obligations, side decisions, bilateral grant, withdrawal/revocation and governance provenance |
| **Access Policy** | what network access is currently authorized to exist? | authoritative Policy Rule truth, semantic uniqueness/idempotency and effective authorized-policy projection |
| **Authority Management** | who may perform a domain action for scope/time? | effective actor/action/scope authority, role/group/scope assignments and accountability semantics |
| **Resource Catalogue** | what access-domain resources exist, to which responsibility scopes do they belong, and how are they currently realized? | Resource/Endpoint identity, Resource Scope Affiliation, current/historical corporate-visible address realization and access-relevant lifecycle facts |
| **Application Communication Catalogue** | which application/component interactions and concrete Component Deployments are structurally valid? | Application/Component/ComponentDeployment/Interaction identities and immutable interaction traffic contracts |
| **Network Enforcement Placement** | which enforcement locations and policy locators are candidates for a technical source/destination pair? | Firewall candidate relevance from current network state/overrides and applicable policy/ACL locators |
| **Technical Access Evidence** | what technical access material did a source report? | immutable/source-qualified normalized technical evidence with scope/time/provenance; no authorization claim |
| **Access Policy Realization** | how does configured effective access compare with required effective access for a supplied comparable target, and what semantic policy change is needed? | realization assessment, semantic reconciliation, change design and proposed-change semantic verification; provider rendering ownership remains under revalidation |

`Connectivity Requirements` and `Connectivity Decision` are **legacy/current-state context boundaries**, not current target Bounded Contexts. ADR-019 supersedes the stronger MVP-scope assumptions of ADR-016 while preserving the decision not to carry those old boundaries forward unchanged.

## Core semantic ladder

```text
Observed != Recognized != Needed != Authorized != Realized
```

- **Needed** is owned by Business Connectivity.
- **Authorized** governance/consent history is owned by Access Governance.
- current authoritative Policy Rule truth is owned by Access Policy.
- **Realized** comparison is downstream of derived required-policy materialization and normalized network evidence.

A fact at one level must not be silently promoted to another.

## Business Connectivity boundary

Business Connectivity owns enduring business justification for application-semantic communication.

Its central facts are conceptually:

```text
Business Process
    -> Connectivity Need
        -> required Application Interaction
        -> dependent participant/component role
```

A Need is not permission, is not identified by IP/Endpoint/Deployment, may survive deployment/address replacement, may lead to several concrete Access Requests, and may disappear without rewriting governance history.

## Access Governance boundary

Access Governance owns consent lifecycle/history for a concrete deployed interaction.

```text
source ComponentDeployment
+ destination ComponentDeployment
+ stable Interaction meaning
```

```text
Grant  = source-side consent AND destination-side consent
Revoke = source withdrawal OR destination withdrawal
```

Access Governance publishes authorization grant/withdrawal semantics to Access Policy. It does not own Need identity or actor-authority resolution.

## Authority Management boundary

Authority Management owns effective action authority for actor/scope/time and the private role/group/scope mechanics that establish it.

```text
actor + action + scope + time
    -> admitted | denied | unknown/ambiguous
```

Consumers use the effective result and required provenance rather than reimplementing role/group logic.

## Access Policy boundary

Access Policy owns current semantic authorization truth expressed as authoritative Policy Rules and effective authorized-policy projection.

It consumes `AuthorizationGranted` / `AuthorizationWithdrawn` from Access Governance and trusted ACC subject identity. Multiple Needs/Requests may justify one Rule. Address/Endpoint changes do not redefine Rule semantic identity.

## Primary contracts for the governance chain

### Business Connectivity -> Access Governance

Provides Process-backed Need/business justification for deliberate requests. Need existence does not authorize access.

### Application Communication Catalogue -> Access Governance / Access Policy

Publishes the exact deployed Interaction subject:

```text
sourceComponentDeploymentRef
+ destinationComponentDeploymentRef
+ interactionContractRevisionRef
```

For MVP each ComponentDeployment belongs to exactly one Resource.

### Authority Management -> Access Governance

Publishes effective request/approve/revoke authority and audit provenance.

### Access Governance -> Access Policy

Publishes:

```text
AuthorizationGranted(subject, provenance)
AuthorizationWithdrawn(subject, provenance)
```

Pending/rejected Requests remain governance history.

## Resource realization contract

Resource Catalogue owns ResourceEndpoint identity and current corporate-visible address realization.

Target MVP semantics:

```text
Resource
    -> ResourceEndpoint [0..N]
        -> current corporate-visible address/prefix [0..1]
```

Endpoint identity is stable across address changes. Resource/Endpoint may exist before an address is known. Resource Catalogue records the address/prefix meaningful in the corporate access-management address space and does not calculate NAT.

An Endpoint without a current address is valid catalogue truth and must be surfaced downstream as unresolved materialization rather than silently omitted.

Canonical target realization semantics: `docs/domain/resource-catalogue/target-realization-model.md`.

## Required Policy Materialization

ADR-020 establishes semantic-to-technical required-policy materialization as a **non-peer derived composition**, not a Bounded Context.

It deterministically composes published facts:

```text
Access Policy effective Policy Rules
    + ACC deployed Interaction + immutable traffic contract
    + Resource Catalogue current Endpoint/address realization
    + NEP candidate target/policy-locator result
        -> TargetRequiredPolicy
        -> APR
```

The composition owns no upstream fact and no independent business lifecycle.

For each effective Rule it derives normalized technical predicates from all current source and destination Endpoint address combinations plus the complete Interaction traffic contract. Duplicate predicates are deduplicated only while preserving all contributing Policy Rule provenance.

Each technical source/destination pair is submitted to NEP. The composition groups required predicates by comparable candidate `firewallId + policyLocator` and publishes a derived `TargetRequiredPolicy` with logical time/freshness/provenance.

If a Resource/Endpoint/address, placement fact, or comparable policy locator is unavailable, the semantic authorization remains valid and materialization is explicitly `unresolved`. `Unresolved` is neither empty required policy nor APR `missing`.

NEP remains the owner of candidate relevance. APR consumes comparable target-specific required policy and must not reconstruct authorization/catalogue/placement semantics.

## Responsibility Scope relationship

A stable Responsibility Scope reference correlates independent Resource Catalogue membership and Authority Management action-authority facts. Neither implies the other; catalogue visibility is independently governed.

## Realization chain

```text
Business Connectivity
    -> Access Governance
        -> Access Policy
            -> Required Policy Materialization (derived composition)
                -> ACC + Resource Catalogue
                -> Network Enforcement Placement
                -> TargetRequiredPolicy
                    -> Access Policy Realization
                        <-> configured effective-policy evidence
                            -> change execution / post-check downstream
```

Technical Access Evidence supplies source-qualified technical evidence and never becomes authorization simply because evidence exists.

## Non-peer compositions

- `Required Policy Materialization` derives target-specific required effective policy; it owns no independent source truth.
- `Scoped Connectivity Inventory` is an application/read composition over authoritative contexts.
- Requirement-to-Policy Alignment is legacy/current-state terminology and must be revalidated before target reuse.

## Strategic invariants

- A Bounded Context is not a service/deployment unit.
- Business Need and security authorization are separate truths/lifecycles.
- Business Connectivity and Access Governance are separate target BCs per ADR-019.
- Authority Management owns effective action authority; consuming contexts own decisions made using that authority.
- Access Governance owns bilateral consent history; Access Policy owns current Policy Rule truth.
- Resource Scope Affiliation does not imply actor authority, and actor authority does not imply Resource membership.
- ResourceEndpoint identity is stable across address changes; current corporate-visible address realization is a separate Resource Catalogue fact.
- Required Policy Materialization is derived composition, not authoritative peer domain truth.
- one semantic Rule is not one firewall line; many Rules may contribute to one normalized predicate and provenance must survive deduplication.
- unresolved materialization is not empty required policy and not realization drift.
- technical evidence is not authorization.
- NEP owns enforcement-location relevance; APR does not second-guess placement.
- APR compares normalized effective policy semantics rather than raw configuration identity.
- technical realization changes do not redefine semantic authorization identity.
- legacy CR/CD artifacts are migration/history evidence and do not override target semantics.

## Remaining strategic questions

- provider-specific effective-policy normalization/rendering boundaries around TAE/APR/operations;
- whether responsibility-scope changes require warning, reapproval or automatic revocation;
- exact Process organizational-responsibility contract with external enterprise structure.
