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

### Network Enforcement Placement

Owns normalized forwarding/path meaning, Logical Firewall identity/correspondence, Enforcement Selection and Enforcement Attachment semantics.

A Logical Firewall may map to one or several provider realizations, and a provider realization may host zero or several Logical Firewalls.

Provider replacement does not automatically create a new Logical Firewall. Provider retirement and Logical Firewall retirement are separate decisions.

### Authority Management

Owns who may curate, administer, approve, plan, execute or otherwise act for the relevant Resource/Logical Firewall/scope. Authority is not inferred from property ownership or provider location.

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
organizational affiliation
technical custody / administration
access/security policy authority
network planning/execution authority
physical/network placement
```

Changing one relation must not silently change the others.

Ownership, stewardship and Responsibility Assignments are temporal relations to an existing domain subject, not identity-defining fields of Resource, Application, Component, Component Deployment or Access Rule merely because an actor changes.

```text
ownership / responsibility change
!= domain entity identity change
!= Access Rule identity change
```

Such a change may alter who is authorized to act, may require responsibility review, and may become an input to a future Connectivity Decision re-evaluation if that deferred domain defines it as decision-relevant. It must not silently manufacture a new identity.

## Lifecycle consequences

A Resource affiliation/address/site/lifecycle change may trigger responsibility review, path/enforcement re-evaluation and Access Policy Realization without changing the semantic identity of an existing Access Rule.

Retiring/replacing provider infrastructure does not silently migrate policy authority, Logical Firewall identity or every responsibility assignment.

## Guardrail

This is a problem-space identity/ownership model, not a class hierarchy, database schema, API contract, service boundary or provider inventory design.
