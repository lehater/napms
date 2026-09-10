# Resource Role Model

Status: `canonical Strategic DDD summary for access-relevant Resources, provider realizations, responsibility and enforcement identities`.

## Purpose

Clarify which identities and organizational relations belong to the access domain without turning the product into either a parallel firewall inventory or a generic enterprise asset/CMDB.

## Resource inclusion rule

```text
provider/device exists
!=
automatic Resource Catalogue identity
```

A physical/virtual network device may be:

- only infrastructure/provider realization;
- an access-domain Resource because its independent identity matters to access outcomes;
- both.

A first-class Resource is justified when its identity/lifecycle is needed for outcomes such as responsibility/stewardship, management-plane access, access-relevant affiliation, access posture, or reconciliation of changes.

## Keep identities distinct

```text
Resource
!= Resource Endpoint
!= provider/device realization
!= Logical Firewall
!= Enforcement Attachment
!= Application / Component Deployment
```

Simple deployments may make some of these one-to-one. The domain model must not depend on that coincidence.

## Ownership

### Resource Catalogue

Owns access-relevant Resource identity, Resource Endpoint/current realization and Resource lifecycle/affiliation/responsibility facts required by access outcomes.

For I16A this explicitly includes **Resource Scope Affiliation**: the time-qualified relation stating that an existing Resource belongs to one Responsibility Scope for owner/responsibility-oriented product views.

```text
Resource Scope Affiliation
    Resource reference
    Responsibility Scope reference
    Validity [validFrom, validUntil)
    Provenance
```

The relation is not Resource identity. One Resource may be effectively affiliated with more than one Responsibility Scope at the same logical time when the business organization genuinely overlaps.

For one Resource + one Responsibility Scope + one logical time, at most one effective Resource Scope Affiliation is authoritative. Overlapping effective records for the same pair are an integrity ambiguity and fail closed until corrected.

Changing or ending an affiliation does not create another Resource.

I26 adds **Resource Responsibility** as a separate time-qualified operational/contact relation:

```text
Resource Responsibility
    Resource reference
    Responsible Party reference
    Party kind: Person | Team
    Role: ServiceOwner | TechnicalOwner | OperationsContact | BusinessOwner
    Display name
    Optional contact point
    Validity [validFrom, validUntil)
    Provenance
```

Resource Responsibility answers who is operationally responsible for, owns, supports or should be contacted about a Resource. It does not grant a NAPMS action authority.

A Resource may have multiple simultaneous assignments, including multiple assignments for the same role. The first slice exposes all effective assignments and does not invent a single `primary` owner.

A Responsible Party is an opaque person/team reference for this relation. I26 does not require an enterprise identity provider, directory or CMDB. The supported local target may use deterministic local responsibility data behind the same port.

### Network Enforcement Placement

Owns normalized forwarding/path meaning where proven, weaker Network Context candidate-set meaning, Logical Firewall identity/correspondence, Enforcement Selection and Enforcement Attachment semantics.

A Logical Firewall may map to one or several provider realizations, and a provider realization may host zero or several Logical Firewalls.

Provider replacement does not automatically create a new Logical Firewall. Provider retirement and Logical Firewall retirement are separate decisions.

### Authority Management

Owns who may curate, administer, approve, plan, execute or otherwise act for the relevant Resource/Logical Firewall/scope. Authority is not inferred from Resource Responsibility, property ownership or provider location.

Authority Management does **not** own which Resources belong to a Responsibility Scope or who is an operational Resource contact. It evaluates actor/action eligibility for the same stable scope reference; Resource Catalogue owns Resource-to-scope affiliation and Resource Responsibility facts.

I16A adds an independent workspace-read action `ReadScopedConnectivity`. It admits using one Responsibility Scope as the actor's local workspace context. It does not imply Requirement/Decision/Rule detail read or any mutation action.

### Network Environment Operations

Owns provider-facing acquisition/diagnostic/mutation mechanics where product scope uses them. It does not own normalized RC/NEP/TAE truth.

## Management-plane access

Access **to** a firewall/network device management service is ordinary governed communication when that endpoint/service participates in the access domain.

It must remain distinct from traffic **through** the same device's enforcement role.

The current Access Rule semantics still use the normal application-backed identity:

```text
Source Component Deployment
+ Destination Component Deployment
+ Directed Communication Specification
```

## Organizational relations

Keep independent:

```text
property / asset ownership
Resource Responsibility / operational contact
Resource Scope Affiliation
actor Responsibility Assignment / domain-action authority
technical custody / administration
access/security policy authority
network planning/execution authority
physical/network placement
catalogue visibility
```

Changing one relation must not silently change the others.

```text
Resource --Resource Responsibility--> Person / Team + operational role
Resource --Resource Scope Affiliation--> Responsibility Scope
Actor    --Responsibility Assignment--> Responsibility Scope + Action
```

These relations may refer to related organizational concepts but have different semantic meanings and owners.

- Resource Catalogue answers **which Resources are in scope S at time T**.
- Resource Catalogue answers **which operational responsibility/contact assignments exist for Resource R at time T**.
- Authority Management answers **whether actor A may perform action X for scope S at time T**.
- current catalogue visibility answers only whether catalogue metadata may be discovered/read; it does not create responsibility or authority.

Ownership, stewardship, Resource Responsibilities, Resource Scope Affiliations and Responsibility Assignments are temporal relations to existing domain subjects, not identity-defining fields of Resource, Application, Component, Component Deployment or Access Rule merely because an actor or organizational relation changes.

```text
ownership / responsibility / Resource Scope Affiliation change
!= domain entity identity change
!= Access Rule identity change
```

Such a change may alter who should be contacted, may require responsibility review, and may become an input to a future Connectivity Decision re-evaluation if that domain defines it as decision-relevant. It must not silently manufacture a new identity or action authority.

## Responsibility-scope consequences

The resource-centric owner workspace derives its local side as:

```text
actor
  -> effective unambiguous ReadScopedConnectivity authority for scope S
  -> effective Resource Scope Affiliations for S
  -> local Resources
```

Resource Responsibility is orthogonal to that derivation. Being listed as Service Owner or Operations Contact does not by itself place a Resource in a scope and does not give the listed party a NAPMS action right.

Other domain actions remain independently authorized. In particular, local-workspace membership does not itself permit declaring a Requirement, deciding connectivity, mutating a Rule or reading protected business details.

Existing Requirement Governance Scope, Decision Governance Scope and Rule Governance Scope are stored context on those entities. A later Resource Scope Affiliation or Resource Responsibility change must not silently rebind those stored scopes.

A Resource with no effective Resource Scope Affiliation is still a Resource and remains catalogue-readable under the current global catalogue visibility baseline; it simply cannot appear as a local Resource for that scope.

## Checker consequence

Checker may project Resource Responsibility for every Resource candidate resolved from the source/destination technical addresses. If address resolution is ambiguous, responsibility is shown per Resource candidate; Checker shall not collapse the candidates into one asserted owner.

This projection supports operational questions such as whom a network engineer should contact before maintenance affecting a traffic relationship.

## Lifecycle consequences

A Resource affiliation/address/site/lifecycle/responsibility change may trigger responsibility review, Network Context/enforcement re-evaluation and Access Policy Realization without changing the semantic identity of an existing Access Rule.

Retiring/replacing provider infrastructure does not silently migrate policy authority, Logical Firewall identity or every responsibility assignment.

## Guardrail

This is a problem-space identity/ownership model, not a class hierarchy, database schema, API contract, service boundary or provider inventory design.
