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

### Application
Stable ACC-owned structural identity grouping Components that belong to one application concern relevant to governed communication.

```text
Application
    ApplicationId
    Display Name
    Active | Retired
```

Application identity is server-owned and remains stable across display-name changes. Retirement is terminal in the first I27 curation slice and does not rewrite historical Component Deployments, DCS revisions or downstream policy references.

### Component
Stable ACC-owned structural identity inside exactly one Application.

```text
Component
    ComponentId
    ApplicationId
    Display Name
    Active | Retired
```

A Component is not a Component Deployment. Its parent Application is immutable for the Component lifetime. Changing the business parent is represented by replacement rather than in-place reassignment.

### Component Deployment
Concrete deployment of a Component used as one side of an Access Rule / Domain Interaction.

```text
Component Deployment
    ComponentDeploymentId
    ComponentId
    optional Display Name
    Active | Retired
```

The existing Component Deployment UUID remains the stable identity consumed by Requirements, Decisions and Access Rules. Its parent Component is immutable for the deployment lifetime. Retirement prevents new authoring that requires an active participant but preserves historical references.

### Catalogue Display Name
Human-readable ACC-owned presentation metadata for Application, Component, Component Deployment or immutable DCS revision where the owning type supports it.

```text
Catalogue Display Name
!= Application identity
!= Component identity
!= Component Deployment identity
!= DCS revision identity
!= RuleSemanticIdentity
```

Changing or omitting a deployment/DCS display name does not change proposal validity, Connectivity Decision subject, Access Rule identity, effective desired-policy membership or normalized-policy semantics. Consumers must retain the stable UUID/reference as technical identity and fall back according to the owning read contract.

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
Application-owned communication contract connecting compatible source/destination Component Deployments and carrying protocol/service/port semantics.

A persisted DCS revision is immutable. Changing communication semantics creates another revision rather than mutating the revision referenced by existing Requirements, Decisions or Rules.

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
Exact relation between one technical region fragment and one Domain Interaction technical region fragment:

```text
Exact
Covers
CoveredBy
PartialOverlap
None
```

### Resolution Status
Overall Domain Access Resolution classification:

```text
Exact
Covered
Partial
Ambiguous
Unresolved
Unknown
```

`Ambiguous` means one technical overlap maps to more than one distinct Domain Interaction and no winner is selected. `Unknown` means predicate-relevant RC/ACC knowledge or accepted technical algebra is insufficient for a complete conclusion.

### Unresolved Technical Remainder
Canonical technical region not resolved by known Domain Interaction overlap. With complete supported knowledge it is the exact set difference between the input predicate and all overlap witnesses. Under `Unknown`, remainder completeness is not claimed.

### Business-Optimal Enforcement Policy
The enforcement-policy semantics that the domain considers correct/preferred for relevant enforcement points.

For the first I20 slice, “optimal” means exact business-correct technical coverage with no silent broadening/narrowing plus canonical union/deduplication. It does not claim globally minimum rule count, vendor-object efficiency or execution ordering.

### Enforcement Target
I20 target at which desired/configured enforcement semantics are compared:

```text
Logical Firewall
+ Enforcement Attachment
```

Provider realization/path/traversal data is provenance, not target identity.

### Managed Reconciliation Scope
APR correlation value proving one Access Policy governance scope and one Enforcement Target are being compared with configured evidence from the same managed policy partition.

It is not a TAE Source Scope, Authority Management scope or persisted aggregate. Complete comparison requires an explicit trusted source/scope contract; matching names or “same firewall” is insufficient.

### Configured Enforcement Snapshot
APR-owned projection of one explicitly selected TAE Configured capture plus its managed-scope/source contract.

For a complete first-slice comparison it represents exact effective Permit regions for the same managed scope at `EvidenceTime.Instant(asOf)` and carries explicit completeness/evaluation provenance.

TAE evidence alone does not imply this snapshot is current or complete.

### Policy Reconciliation
Capability inside Access Policy Realization that compares canonical desired and configured effective Permit regions for one Managed Reconciliation Scope.

Status:

```text
Satisfied
Drift
Ambiguous
Unknown
```

Exact witnesses:

```text
common  = desired ∩ configured
missing = desired - configured
extra   = configured - desired
```

### Required Semantic Change

```text
No-op    # missing empty, extra empty
Add      # missing non-empty, extra empty
Remove   # missing empty, extra non-empty
Replace  # missing non-empty, extra non-empty
```

The classification is vendor-neutral semantic delta. `Replace` does not promise one device/vendor replace operation; I21/I22 own rendering/execution mechanics.

### Policy Algebra
Internal APR semantics for exact overlap, containment, coverage, equivalence, canonical union, semantic difference and witnesses.

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

### Traffic Relation
Ephemeral NEP query value for traffic whose placement is being selected. The first I19 slice uses one exact source IP + one exact destination IP and explicit logical time.

```text
Traffic Relation
!= Access Rule identity
!= Domain Interaction identity
!= persisted aggregate
```

If truthful forwarding depends on dimensions absent from this first value, placement is `Unknown` until the model is extended.

### Forwarding Path
Normalized ordered path knowledge for one Traffic Relation. The first slice contains ordered Traversal Points and supports zero/one complete path; unsupported multipath is `Unknown`.

### Traversal Point
One ordered path occurrence carrying a provider-realization correspondence reference and normalized Path Attachment reference.

### Logical Firewall
Stable independently configurable enforcement identity.

```text
Logical Firewall
!= provider/device realization
!= Resource
!= Enforcement Attachment
```

Provider replacement does not automatically replace the Logical Firewall.

### Logical Firewall Correspondence
Time-qualified relation between one Logical Firewall and one provider-realization reference. It is many-to-many across the model and preserves provenance.

### Enforcement Attachment
Time-qualified NEP relation connecting one Logical Firewall to one normalized Path Attachment on one provider realization.

The attachment has its own identity and must have a matching effective Logical Firewall Correspondence before it can support placement.

### Enforcement Placement
One selected occurrence stating that traffic traverses a particular effective Logical Firewall through a particular Enforcement Attachment at a path position.

```text
Enforcement Placement
!= physical equipment placement
!= current-policy duplication
!= authorization
```

### Enforcement Selection
Derived NEP result for one Traffic Relation + `asOf`.

```text
Placed
NoEnforcement
NoForwardingPath
Ambiguous
Unknown
```

`NoEnforcement` requires complete path + attachment knowledge and is stronger than “none found”. `NoForwardingPath` requires positive complete no-route knowledge. `Ambiguous` selects no Logical Firewall winner. Missing/unsupported relevant knowledge is `Unknown`.

Zone/interface/default deny/evaluation behavior belong to NEP/enforcement semantics when a later accepted slice models them; they do not belong to Technical Access Evidence.

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
