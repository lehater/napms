# Ubiquitous Language

Status: `accepted NAPMS-DDD-001 / source DDD-BDM-010 ubiquitous language`.

## Connectivity Requirements

### Connectivity Requirement
Authoritative statement that one semantic connectivity need exists for one dependent concern.

It has a stable `ConnectivityRequirementId`, a stable Requirement Governance Scope, one immutable Dependent Component Deployment, one immutable Required Semantic Interaction, mutable Applicability/Justification and lifecycle `Active | Retired`.

```text
Connectivity Requirement
!= Access Request / ticket
!= Connectivity Decision
!= Access Rule
!= configured/observed access
```

### Requirement Governance Scope
Stable non-identity scope stored on one Connectivity Requirement and used by Authority Management for later read/mutation actions. Later callers cannot substitute another scope.

### Dependent Component Deployment
The participating Component Deployment whose operational/business concern requires the interaction.

It must be either the Source or Destination Component Deployment of the Required Semantic Interaction.

It is not an actor-owner field and does not grant authority.

### Required Semantic Interaction
Exact immutable required application interaction:

```text
Source Component Deployment
+ Destination Component Deployment
+ immutable DCS revision
```

It uses ACC-owned structural communication semantics but remains distinct from Access Rule / Access Rule Proposal identity ownership.

### Requirement Applicability

```text
Ongoing
| AbsoluteWindow(start, end)
```

Absolute windows use offset-aware half-open `[start,end)` semantics. Applicability is mutable and not identity-defining.

### Requirement Justification
Mandatory non-empty business explanation of why the connectivity is required. It is mutable and is not a Decision/approval reason.

### Requirement Lifecycle

```text
Active -> Retired
```

Retired is terminal in I13. No Pending/Approved/Rejected states belong to Connectivity Requirements.

## Connectivity Decision

### Connectivity Decision
Immutable final business decision for one exact proposed Access Rule semantic identity and governance scope.

```text
Connectivity Decision
    DecisionId
    RuleSemanticIdentity subject
    Decision Governance Scope
    Allowed | NotAllowed
    Validity
    Reason
    Evidence References
    Decision Provenance
    supersedes DecisionId?
```

A Decision is not an Access Rule and does not own Rule lifecycle.

### Decision Governance Scope
Stable scope used by Authority Management for decision/read actions. In the first accepted model it is the accepted proposal authority scope.

It is not part of RuleSemanticIdentity and cannot be caller-substituted after Decision creation.

### Decision Validity
Offset-aware half-open interval `[validFrom, validUntil)`; `validUntil` may be absent.

Validity controls whether a Decision may be consumed at one logical time. Expiry does not silently mutate a Rule already materialized from that Decision.

### Decision Reason
Mandatory stable reason code plus human-readable explanation of why the final outcome is Allowed or NotAllowed.

External policy/requirement/catalogue facts remain owned by their source contexts and are referenced rather than copied as Decision-owned truth.

### Decision Evidence Reference
Opaque source-qualified reference to an authoritative fact used in deciding.

A Connectivity Requirement may be evidence, but:

```text
Required != Allowed
```

### Decision Supersession
Reconsideration creates a new immutable Decision for the same subject/scope and explicitly references the immediately superseded Decision.

Historical Decisions are never rewritten.

### DecideConnectivity
Authority Management domain action permitting one principal to record or supersede a final Connectivity Decision for a scope/time.

`ProposeConnectivity` does not imply `DecideConnectivity`.

### ReadConnectivityDecision
Independent Authority Management action permitting protected Decision reads.

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

### Responsibility Scope
Stable scope reference used to correlate domain responsibility/authority with Resource affiliation.

In the first I16A model it is a reference value, not a standalone aggregate with its own hierarchy/lifecycle.

```text
same Responsibility Scope reference
    Resource Catalogue -> Resource membership
    Authority Management -> Actor/action authority
```

The shared reference does not merge semantic ownership between those contexts.

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

It connects an Actor/action to a Responsibility Scope. It does not state which Resources belong to that scope.

### ReadScopedConnectivity
Independent Authority Management action permitting an Actor to use one Responsibility Scope as the local context of the Scoped Connectivity Inventory at an effective time.

It does not imply:
- catalogue mutation;
- Requirement read/mutation;
- Connectivity Decision read/decision authority;
- Access Rule read/mutation.

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

### Resource Scope Affiliation
Resource Catalogue-owned, time-qualified relation stating that one existing Resource belongs to one Responsibility Scope for an effective interval.

```text
Resource
+ Responsibility Scope reference
+ [validFrom, validUntil)
+ provenance
```

Properties:
- not part of Resource identity;
- may change/end without replacing the Resource;
- one Resource may be affiliated with multiple Responsibility Scopes at the same time;
- does not grant actor authority;
- does not define catalogue visibility;
- does not silently rewrite stored Requirement/Decision/Rule governance scopes.

## Application Communication Catalogue

### Application / Component
Application structure used to identify the communicating domain participants relevant to governed access.

### Component Deployment
Concrete deployment of a Component used as one side of an Access Rule / Domain Interaction.

### Catalogue Display Name
Optional Application Communication Catalogue-owned human-readable presentation metadata for a Component Deployment or immutable DCS revision.

```text
Catalogue Display Name
!= Component Deployment identity
!= DCS revision identity
!= RuleSemanticIdentity
```

Changing or omitting a display name does not change proposal validity, Connectivity Decision subject, Access Rule identity, effective desired-policy membership or normalized-policy semantics. Consumers must retain the stable UUID/reference as technical identity and fall back to it when no display name exists.

### Deployment Resource Binding
Application Communication Catalogue-owned, time-qualified relation from one Component Deployment to one-or-more stable Resource references used to obtain technical realization from Resource Catalogue.

The binding is not Resource realization and is not part of Access Rule identity.

### DCS Projection Semantics
Complete immutable Application Communication Catalogue-owned projection payload correlated to one exact DCS contract/revision. I5 captures it without interpreting protocol/service/port structure. I6 decodes it through a local translation boundary into normalized DCS Traffic Alternatives.

### DCS Traffic Alternative
One vendor-neutral traffic selector derived from DCS projection semantics:

```text
protocol
+ source Ports
+ destination Ports
+ optional ACC service reference
```

The protocol is a non-empty canonical token within the normalized export contract.

### Port Constraint

```text
NotApplicable
Any
PortRangeSet
```

`Any` means unconstrained ports where port semantics apply. `NotApplicable` means ports do not apply for that protocol/side.

### Port Range
Inclusive integer interval `first..last` within `0..65535`. Sets of ranges are canonicalized to sorted, non-overlapping and non-adjacent ranges and are not expanded into individual ports.

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
Immutable child evidence item carrying normalized technical predicate facts:

- source address/range;
- destination address/range;
- protocol/ports;
- action where meaningful;
- source entry reference and position/order where source semantics make them factual.

The enclosing Technical Access Evidence Set supplies the source/scope/capture/time/recording provenance shared by its entries. Source-native service/object names are not silently promoted into source-neutral predicate semantics.

### Configured Evidence
Technical Access Evidence asserting what a device/controller source reported as configured for a scope/time.

### Traffic-Derived Evidence
Technical Access Evidence derived from observed communication. It represents observed technical communication material, not a complete firewall policy and not an inferred Permit/Block action unless a concrete source contract can support that fact without semantic invention.

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

## Scoped Connectivity Inventory

### Scoped Connectivity Inventory
Non-peer application/read composition for one actor-admitted Responsibility Scope and logical time.

It derives local Resources from effective Resource Scope Affiliations, correlates bound Component Deployments/interactions, and presents independently owned Need/Decision/Policy summaries.

```text
Scoped Connectivity Inventory
!= Bounded Context
!= aggregate
!= authoritative Connectivity Status
```

### Local Resource
UI/application projection term for a Resource effectively affiliated with the selected Responsibility Scope.

It is not a new Resource subtype or ownership field.

### Remote Resource
UI/application projection term for a Resource on the opposite side of a displayed Component interaction relative to one Local Resource.

Under the current product baseline foreign catalogue Resources remain readable; Remote Resource does not imply foreign authority.

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
