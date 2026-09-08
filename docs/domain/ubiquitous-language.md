# Ubiquitous Language

Status: `accepted NAPMS-DDD-001 / source DDD-BDM-010 ubiquitous language`.

## Access Policy

### Access Rule
Authoritative desired-access unit identified by:

```text
Source Component Deployment
+ Destination Component Deployment
+ Directed Communication Specification
```

### Rule Governance Scope
Stable non-identity Scope under which Authority Management evaluates later domain actions on one Access Rule.

It is established from the accepted proposal authority scope at Rule materialization. Actor assignments/delegations may change over time without silently changing Rule Governance Scope or Rule identity.

### EffectiveWindow
Optional absolute Rule condition `[start, end)` with offset-aware instants. It permits desired effect when `start <= asOf < end`. Absence means no time-window restriction.

EffectiveWindow is declarative Rule data. It does not periodically mutate Active/Inactive and is not part of RuleSemanticIdentity.

### Global Policy
Projection of authorized Access Rules.

### Effective Desired Policy
For one authorized RuleGovernanceScope and logical `asOf`, the Access Policy projection of authoritative Rules that are Active and whose optional EffectiveWindow permits effect.

## Authority Management

### Authority
Effective domain eligibility/power of an Actor to perform a domain action for a Scope at an effective time.

Authority is established/explained through Responsibility Assignments, delegation, transfer, revocation and validity semantics.

```text
Authority
!= governed network Access
!= identity/account lifecycle
!= generic IAM/OAuth/RBAC mechanism
```

### Responsibility Assignment
The scoped, time-qualified assignment that establishes or explains an Actor's domain responsibility and resulting authority.

## Resource Catalogue

### Resource
Stable access-domain identity whose lifecycle/affiliation/realization matters to governed network-access outcomes.

```text
Resource
!= generic enterprise asset
!= provider/device realization
!= Logical Firewall
```

### Resource Endpoint
Current/effective network-address realization through which a Resource participates in governed communication.

## Application Communication Catalogue

### Application / Component
Application structure used to identify the communicating domain participants relevant to governed access.

### Component Deployment
Concrete deployment of a Component used as one side of an Access Rule / Domain Interaction.

### Directed Communication Specification
Application-owned communication contract connecting compatible source/destination component roles and carrying protocol/service/port semantics.

The context owns application/component/deployment structure only to the depth required to define and realize governed communication; it is not a generic application portfolio/CMDB.

## Technical Access Evidence

### Technical Access Evidence
Source-qualified normalized technical access-list material used as evidence for reasoning.

### Evidence Kind

```text
Configured
TrafficDerived
Imported
```

### Technical Access Entry
Normalized technical predicate facts:

- source address/range;
- destination address/range;
- protocol/service/ports;
- action where meaningful;
- source position/order where source semantics make it factual;
- evidence source/scope/time/provenance.

### Configured Evidence
Technical Access Evidence asserting what a device/controller source reported as configured for a scope/time.

### Traffic-Derived Evidence
Technical Access Evidence derived from observed communication. It normally represents permit-like communication material rather than a complete firewall policy.

### Imported Evidence
Technical access-list evidence obtained from a file/external source.

## Access Policy Realization

### Technical Access Predicate
The technical communication/access region described by source/destination ranges and protocol/service constraints.

### Domain Access Resolution
Canonical interpretation of one Technical Access Predicate in the application/resource domain.

Contains:

- exact/covered Domain Interactions;
- partial overlap relations;
- unresolved technical remainder;
- ambiguity/unknown;
- effective-time/provenance facts.

### Domain Interaction
A resolved concrete domain interaction identified by Source Component Deployment + Destination Component Deployment + matching DCS. It is not automatically an Access Rule.

### Access Correspondence
Relation between technical and domain access spaces, for example:

```text
Exact
Covers
CoveredBy
PartialOverlap
None
Unknown
```

### Unresolved Technical Remainder
Part of a technical predicate that cannot currently be mapped to known domain interactions.

### Business-Optimal Enforcement Policy
The enforcement-policy semantics that the domain considers correct/preferred for relevant enforcement points. "Optimal" is a business judgement, not mathematical global optimality.

### Policy Reconciliation
Capability inside Access Policy Realization that determines satisfaction/uncertainty and required semantic change between desired enforcement semantics and configured evidence.

### Required Semantic Change

```text
Add
Remove
Replace
No-op
```

### Policy Algebra
Internal APR semantics for overlap, containment, coverage, equivalence, ordered effective regions, semantic difference and witnesses.

## Proposal use case

### Access Rule Proposal
Application-level handoff proposing materialization of one Access Rule using the future Rule identity triple.

It has no Rule ID, operational state or authorization.

```text
Technical Access Evidence
!= Domain Access Resolution
!= Access Rule Proposal
!= Access Rule
```

## Network Enforcement Placement

### Enforcement Placement
The relation stating that a given traffic relation is subject to enforcement at a particular Logical Firewall / Enforcement Attachment / policy location, based on forwarding knowledge plus accepted corrections.

Placement relevance is independent from whether equivalent policy is already configured.

```text
Enforcement Placement
!= physical equipment placement
!= current-policy duplication
```

### Logical Firewall
Independently configurable enforcement identity.

### Enforcement Attachment
Network/firewall placement semantics connecting traffic relevance to an enforcement point.

Zone/interface/default deny/evaluation behavior belong to NEP/enforcement semantics, not Technical Access Evidence.

## Independent truths

```text
Evidence observed/derived
Domain meaning resolved
Proposal exists
Rule exists
Authorized
Active/Inactive
Enforcement policy derived
Configured evidence observed
Satisfied
```
