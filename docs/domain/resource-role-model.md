# Resource Role Model

Status: `canonical Strategic DDD summary for access-relevant Resources, provider realizations and enforcement identities`.

## Purpose

Clarify which identities belong to the access domain without turning the product into either a parallel firewall inventory or a generic enterprise asset/CMDB.

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

Owns access-relevant Resource identity, Resource Endpoint/current realization and Resource lifecycle/affiliation facts required by access outcomes.

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

### Network Enforcement Placement

Owns normalized forwarding/path meaning, Logical Firewall identity/correspondence, Enforcement Selection and Enforcement Attachment semantics.

A Logical Firewall may map to one or several provider realizations, and a provider realization may host zero or several Logical Firewalls.

Provider replacement does not automatically create a new Logical Firewall. Provider retirement and Logical Firewall retirement are separate decisions.

### Authority Management

Owns who may curate, administer, approve, plan, execute or otherwise act for the relevant Resource/Logical Firewall/scope. Authority is not inferred from property ownership or provider location.

Authority Management does **not** own which Resources belong to a Responsibility Scope. It evaluates actor/action eligibility for the same stable scope reference; Resource Catalogue owns Resource-to-scope affiliation.

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
Resource Scope Affiliation
actor Responsibility Assignment / domain-action authority
technical custody / administration
access/security policy authority
network planning/execution authority
physical/network placement
catalogue visibility
```

Changing one relation must not silently change the others.

For the first I16A model:

```text
Resource --Resource Scope Affiliation--> Responsibility Scope
Actor    --Responsibility Assignment--> Responsibility Scope + Action
```

These are correlated by the stable Responsibility Scope reference but have different semantic owners and meanings.

- Resource Catalogue answers **which Resources are in scope S at time T**.
- Authority Management answers **whether actor A may perform action X for scope S at time T**.
- current catalogue visibility answers only whether catalogue metadata may be discovered/read; it does not create responsibility or authority.

Ownership, stewardship, Resource Scope Affiliations and Responsibility Assignments are temporal relations to existing domain subjects, not identity-defining fields of Resource, Application, Component, Component Deployment or Access Rule merely because an actor or organizational relation changes.

```text
ownership / responsibility / Resource Scope Affiliation change
!= domain entity identity change
!= Access Rule identity change
```

Such a change may alter who is authorized to act, may require responsibility review, and may become an input to a future Connectivity Decision re-evaluation if that deferred domain defines it as decision-relevant. It must not silently manufacture a new identity.

## Responsibility-scope consequences

The resource-centric owner workspace derives its local side as:

```text
actor
  -> effective unambiguous ReadScopedConnectivity authority for scope S
  -> effective Resource Scope Affiliations for S
  -> local Resources
```

Other domain actions remain independently authorized. In particular, local-workspace membership does not itself permit declaring a Requirement, deciding connectivity, mutating a Rule or reading protected business details.

Existing Requirement Governance Scope, Decision Governance Scope and Rule Governance Scope are stored context on those entities. A later Resource Scope Affiliation change must not silently rebind those stored scopes.

A Resource with no effective Resource Scope Affiliation is still a Resource and remains catalogue-readable under the current global catalogue visibility baseline; it simply cannot appear as a local Resource for that scope.

## Lifecycle consequences

A Resource affiliation/address/site/lifecycle change may trigger responsibility review, path/enforcement re-evaluation and Access Policy Realization without changing the semantic identity of an existing Access Rule.

Retiring/replacing provider infrastructure does not silently migrate policy authority, Logical Firewall identity or every responsibility assignment.

## Guardrail

This is a problem-space identity/ownership model, not a class hierarchy, database schema, API contract, service boundary or provider inventory design.
