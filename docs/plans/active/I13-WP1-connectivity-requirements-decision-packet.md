# I13 WP1 — Connectivity Requirements Tactical decision packet

Status: `working decision packet; not canonical domain truth`.

Date: 2026-09-09.

## Purpose

Resolve only the Tactical DDD choices required to open I13 implementation.

This packet separates:
- accepted strategic facts;
- derived constraints;
- recommended To-Be choices;
- alternatives;
- owner decisions still required.

Nothing marked `RECOMMENDED` becomes canonical until accepted.

## Accepted strategic facts

### Semantic ownership

Connectivity Requirements owns:

> what semantic connectivity is needed by an identified dependent concern?

It owns connectivity-need identity/lifecycle, required interaction, applicability and justification/provenance.

It does not own:
- whether access is Allowed/NotAllowed;
- Access Rule identity/state;
- configured/observed technical access;
- technical realization;
- enforcement placement.

### Invariants

```text
Required != Authorized
Required != Configured/Observed
Authority-to-declare != Requirement
ConnectivityRequirement != AccessRequest/ticket
```

A different policy/security authority or mechanism decides whether the requested access is allowed.

### Identity separation

Accepted repository truth keeps distinct:

```text
Resource
!= Resource Endpoint
!= Component Deployment
!= Access Rule
!= actor ownership/responsibility
```

Ownership/responsibility changes do not automatically change the identity of the governed subject.

### Authority boundary

Authority Management owns who may perform a domain action for scope/time.

Connectivity Requirements must not infer permission directly from:
- a property named `owner`;
- organizational affiliation;
- Component Deployment identity;
- Resource identity.

## Derived constraints for I13

These follow from accepted truth and do not require a new business decision.

1. A Connectivity Requirement must have its own authoritative identifier/lifecycle record if it is to be listed, amended/retired and audited.
2. It must retain a stable governance scope established at declaration so later actions are checked against authoritative stored scope rather than caller-supplied scope.
3. Declaration cannot call Connectivity Decision or materialize an Access Rule as a side effect.
4. No `Pending/Approved/Rejected` state belongs in I13; those terms would invent Decision-domain workflow.
5. DCS semantics used by an exact interaction remain ACC-owned and immutable.
6. Business audit/provenance must be domain truth, not only an HTTP log.
7. Technical addresses/protocol/vendor configuration must not become Requirement identity.

## D1 — Aggregate identity and semantic uniqueness

### RECOMMENDED

Use two distinct concepts:

```text
ConnectivityRequirementId
    = stable synthetic authoritative ID

ActiveRequirementSemanticKey
    =
      RequirementGovernanceScope
    + Dependent Component Deployment
    + Required Semantic Interaction
```

Where the Required Semantic Interaction is the exact:

```text
Source Component Deployment
+ Destination Component Deployment
+ immutable DCS revision
```

Consequences:
- Requirement ID survives changes to non-identity properties;
- the same active semantic need is declared idempotently;
- concurrent repeated declaration converges on one active Requirement;
- retiring the Requirement closes that lifecycle episode;
- a later re-declaration of the same need may create a new Requirement ID and preserve the retired historical record;
- justification/applicability are properties, not identity;
- changing dependent or Required Semantic Interaction means another Requirement.

### Why this is preferred

A natural key alone is poor aggregate identity for an auditable lifecycle.

Putting applicability into the key makes a date-window edit silently create another business identity.

Using only a random ID without semantic uniqueness allows contradictory duplicate active statements of the same need.

### Alternative

Make every declaration an independent Requirement ID, including duplicate semantic needs.

Rejected as default recommendation because Connectivity Requirement is explicitly not a ticket/request record.

### OWNER DECISION

Accept the recommended stable ID + active semantic uniqueness model?

## D2 — Dependent

### RECOMMENDED first executable slice

`Dependent` is one **Component Deployment** participating in the Required Semantic Interaction.

Invariant:

```text
DependentComponentDeploymentId
    in {
      SourceComponentDeploymentId,
      DestinationComponentDeploymentId
    }
```

The dependent states whose operational/business concern requires the interaction. It is intentionally separate from the interaction because either participating side may be the concern whose responsible actor declares the need.

Authority remains scope-based through AM; the Requirement does not contain an actor-owner field.

### Why not Resource first

Resource is explicitly distinct from Component Deployment and represents access-domain resource/realization concerns. Making Resource the first Requirement dependent would pull technical realization identity into a semantic application-connectivity need before a real requirement demands it.

Deployment-to-Resource bindings remain available later for realization, not Requirement identity.

### Why not a polymorphic DependentRef first

Supporting Resource | Application | Component | Deployment from day one adds type/lifecycle rules without accepted examples.

Generalize only when a real requirement needs another dependent kind.

### OWNER DECISION

For I13, accept Component Deployment as the only Dependent kind?

## D3 — Required Semantic Interaction

### RECOMMENDED first executable slice

Use the same exact application semantic subject already established for proposal/Rule semantics:

```text
Source Component Deployment
+ Destination Component Deployment
+ immutable DCS revision
```

But keep the type/context ownership distinct:

```text
RequiredSemanticInteraction
!= AccessRule
!= AccessRuleProposal
```

Connectivity Requirements may validate the exact directed interaction through a consumer-owned ACC port.

### Why

- structurally valid meaning already exists in ACC;
- I14 Requirement-to-Policy Alignment can compare exact semantic subjects without inventing fuzzy matching;
- no firewall syntax is introduced;
- abstract/alternative requirements were explicitly deferred by Strategic DDD.

### Alternative

Allow abstract requirements such as “Application A needs service B” without exact deployment/DCS.

This needs new matching/selection semantics and should be a later increment if real examples require it.

### OWNER DECISION

Accept exact Deployment + Deployment + immutable DCS as the I13 Required Semantic Interaction?

## D4 — Applicability

### RECOMMENDED

First model:

```text
RequirementApplicability
    = Ongoing
    | AbsoluteWindow(start, end)
```

Semantics for AbsoluteWindow:

```text
offset-aware instants
start < end
half-open [start, end)
```

Absence of a window means ongoing applicability.

This is a Connectivity Requirements value object; it does not reuse Access Policy `EffectiveWindow` as a shared domain type.

Applicability is mutable while the Requirement is Active and does not change Requirement identity.

### Why

- Strategic DDD says applicability is owned by the context;
- absolute windows are already an accepted product temporal pattern;
- no cron/calendar/recurring semantics are invented;
- I14 can evaluate requirement relevance at one logical `asOf`.

### Simpler alternative

I13 supports only Ongoing and defers all temporal requirement applicability.

This is smaller but would immediately force I14 either to ignore the strategic applicability dimension or reopen I13.

### OWNER DECISION

Accept Ongoing + optional absolute window in I13?

## D5 — Lifecycle and amendments

### RECOMMENDED

Minimal lifecycle:

```text
Active -> Retired
```

Commands:

```text
DeclareConnectivityRequirement
SetRequirementApplicability
SetRequirementJustification
RetireConnectivityRequirement
```

Rules:
- declaration starts Active;
- Retired is terminal in I13;
- no approval state exists;
- changing Dependent or RequiredSemanticInteraction is not an amendment: declare another Requirement and retire the old one if appropriate;
- applicability and justification changes keep the same Requirement ID;
- setting an already-requested property value is an explicit no-op/idempotent result;
- no `Superseded` state until a real workflow needs that semantic distinction.

### Alternative

Generic `AmendRequirement` allowing all properties to change.

Not recommended because it makes identity-defining changes ambiguous and weakens audit semantics.

### OWNER DECISION

Accept Active/Retired + explicit property mutations, with dependent/interaction immutable?

## D6 — Justification and provenance

### RECOMMENDED

Requirement stores:
- non-empty human/business `justification`;
- declaration provenance:
  - actor ID;
  - effective time;
  - Requirement Governance Scope;
  - authority reference;
  - ACC validation/reference where available;
- durable audit entries for accepted applicability/justification/lifecycle mutations with actor/time/scope/authority reference.

Justification is not part of semantic identity.

No arbitrary approval reason or Decision reason is stored in this context.

### OWNER DECISION

Should non-empty justification be mandatory for declaration, or optional in the first slice?

Recommendation: **mandatory** because “why this connectivity is needed” is part of the accepted semantic responsibility of the BC and will be material input for later Decision work.

## D7 — Authority actions and governance scope

### RECOMMENDED

Authority actions:

```text
DeclareConnectivityRequirement
ReadConnectivityRequirement
SetConnectivityRequirementApplicability
SetConnectivityRequirementJustification
RetireConnectivityRequirement
```

On declaration:
- caller selects one authority scope from an AM-provided effective scope list;
- successful declaration stores it as `RequirementGovernanceScope`.

On later actions:
- backend loads the Requirement;
- AM is checked against the stored RequirementGovernanceScope;
- caller cannot replace/supply trusted governance scope.

Read/list:
- list uses effective `ReadConnectivityRequirement` scope discovery;
- ambiguous scopes fail closed;
- detail checks read authority against stored scope.

### Simpler alternative

One broad `ManageConnectivityRequirement` action for all mutations.

Not recommended because declaration, content changes and retirement are materially distinguishable responsibilities and explicit actions are consistent with existing AP authority semantics.

### OWNER DECISION

Accept the explicit action set above?

## D8 — Responsibility/ownership

### RECOMMENDED

No owner/responsible actor field participates in authorization.

Responsibility is represented only through Authority Management assignments for the RequirementGovernanceScope.

The Connectivity Requirement records the actor who performed each audited action, but that historical actor is not “the owner” of the Requirement.

If a responsibility assignment changes:
- Requirement identity does not change;
- RequirementGovernanceScope does not change;
- a different actor may become authorized to read/change/retire it.

This follows existing accepted Resource Role Model semantics and requires no new owner decision unless a separate “business owner of requirement” concept is desired.

## D9 — Idempotency and concurrency

### RECOMMENDED

Declaration:
- semantic uniqueness applies only to Active Requirements under the same RequirementGovernanceScope;
- repeated declaration of the same active semantic key resolves the existing Requirement ID;
- concurrent declaration is enforced by the persistence uniqueness constraint plus application-level resolve semantics;
- a Retired historical requirement does not block a later new declaration of the same semantic key.

Property mutation:
- expected current aggregate version is used for optimistic concurrency or equivalent atomic compare-and-save;
- same requested value produces a stable no-op outcome and no duplicate business audit entry;
- stale conflicting mutation returns explicit conflict/unknown outcome, never silent last-write-wins.

### OWNER DECISION

Accept “one active requirement per scope + dependent + exact interaction”, while allowing a later new lifecycle episode after retirement?

## Proposed Tactical aggregate if D1–D9 are accepted

```text
ConnectivityRequirement
  RequirementId
  RequirementGovernanceScope
  DependentComponentDeploymentId          immutable
  RequiredSemanticInteraction             immutable
      SourceComponentDeploymentId
      DestinationComponentDeploymentId
      DcsContractRevisionId
  RequirementApplicability                mutable
      Ongoing | AbsoluteWindow
  Justification                           mutable
  LifecycleState
      Active | Retired
  DeclarationProvenance
  AuditHistory
  Version
```

## Proposed first application use cases

Commands:
- `DeclareConnectivityRequirement`;
- `SetConnectivityRequirementApplicability`;
- `SetConnectivityRequirementJustification`;
- `RetireConnectivityRequirement`.

Queries:
- `DiscoverConnectivityRequirementScopes`;
- `DiscoverRequiredInteractions`;
- `ListConnectivityRequirements`;
- `GetConnectivityRequirement`.

No I13 use case:
- approves/rejects a requirement;
- calls Connectivity Decision as a side effect;
- materializes an Access Rule;
- calculates Requirement-to-Policy Alignment;
- inspects configured access.

## Smallest owner decision set

The implementation gate can open after answers to these seven choices:

1. Dependent = participating Component Deployment for I13?
2. Required interaction = exact Source Deployment + Destination Deployment + DCS?
3. Requirement identity = stable RequirementId, with one Active requirement per governance scope + dependent + exact interaction?
4. Applicability = Ongoing or optional absolute `[start,end)` window, mutable without identity change?
5. Lifecycle = Active -> Retired; dependent/interaction immutable; justification/applicability mutable?
6. Justification mandatory?
7. Explicit AM actions per operation, rather than one broad Manage action?

Everything else in this packet follows from those choices plus existing canonical guardrails.
