# Connectivity Requirements tactical model

Status: `accepted I13 WP1 baseline`.

Date: 2026-09-09.

## Scope

This model defines the first executable consistency model for the **Connectivity Requirements** bounded context.

It owns the authoritative statement that a semantic connectivity need exists for one dependent concern.

It does not own:
- whether the need is Allowed or NotAllowed;
- Access Rule identity/state;
- configured or observed technical access;
- Requirement-to-Policy Alignment;
- provider/device enforcement.

Core invariant:

```text
Required != Authorized
Required != Configured/Observed
ConnectivityRequirement != AccessRequest/ticket
```

## Value objects

### RequirementGovernanceScope

Stable non-identity scope under which Authority Management evaluates actions on one Connectivity Requirement.

Rules:
- selected from an effective Authority Management scope during declaration;
- stored on the Requirement;
- later operations use the stored scope;
- caller-supplied scope cannot replace the stored scope;
- responsibility/assignment changes do not silently rebind it;
- not part of semantic interaction identity.

### DependentComponentDeploymentId

The Component Deployment whose operational/business concern requires the interaction.

I13 supports exactly one Dependent kind: Component Deployment.

Invariant:

```text
DependentComponentDeploymentId
    in {
      RequiredSemanticInteraction.SourceComponentDeploymentId,
      RequiredSemanticInteraction.DestinationComponentDeploymentId
    }
```

The Dependent is not an actor-owner field. Who may act is always evaluated by Authority Management.

### RequiredSemanticInteraction

Immutable application-semantic subject:

```text
SourceComponentDeploymentId
+ DestinationComponentDeploymentId
+ DcsContractRevisionId
```

It uses the same exact ACC-owned interaction subject already used by proposal/Rule semantics, but remains a Connectivity Requirements value:

```text
RequiredSemanticInteraction
!= AccessRule
!= AccessRuleProposal
```

Technical addresses, Resource realizations, actor ownership, governance scope and Requirement applicability are not members.

### RequirementApplicability

First supported vocabulary:

```text
Ongoing
AbsoluteWindow(start, end)
```

`AbsoluteWindow` invariants:
- start/end are offset-aware instants;
- `start < end`;
- applicability holds exactly when `start <= asOf < end`.

`Ongoing` has no absolute time restriction.

Recurring/calendar/conditional alternatives are deferred until accepted examples require them.

Applicability is mutable and does not change Requirement identity.

### RequirementJustification

Mandatory non-empty business statement explaining why the semantic connectivity is required.

It is mutable and is not part of semantic identity.

Decision reasons/approval reasons do not belong to this value.

## Aggregate boundary

### ConnectivityRequirement

Aggregate root:
- `ConnectivityRequirementId` — stable surrogate authoritative identity;
- immutable `RequirementGovernanceScope`;
- immutable `DependentComponentDeploymentId`;
- immutable `RequiredSemanticInteraction`;
- mutable `RequirementApplicability`;
- mutable mandatory `RequirementJustification`;
- `LifecycleState = Active | Retired`;
- declaration provenance;
- accepted-change audit/history;
- authoritative aggregate version.

Declaration starts `Active`.

`Retired` is terminal in I13.

## Active semantic uniqueness

At most one Active Requirement exists for:

```text
RequirementGovernanceScope
+ DependentComponentDeploymentId
+ RequiredSemanticInteraction
```

Consequences:
- repeated declaration of the same active semantic need resolves the existing Requirement;
- concurrent declaration converges on one active Requirement ID;
- justification/applicability do not affect semantic uniqueness;
- changing Dependent or RequiredSemanticInteraction creates another Requirement;
- after retirement, a later declaration of the same semantic key starts a new lifecycle episode with a new Requirement ID.

The uniqueness constraint is business meaning; a database constraint only enforces it.

## Declaration

Semantic command:

`DeclareConnectivityRequirement`

Inputs:
- governance scope;
- Dependent Component Deployment;
- exact Required Semantic Interaction;
- Requirement Applicability;
- non-empty Justification;
- actor;
- effective action time.

Application/domain behavior:
1. evaluate Authority Management action `DeclareConnectivityRequirement` for actor/scope/effective time;
2. denied/unknown authority fails closed;
3. validate exact Required Semantic Interaction through an ACC consumer-owned port;
4. verify Dependent is one of the interaction participants;
5. resolve existing Active Requirement by semantic uniqueness key;
6. if one exists, return it unchanged;
7. otherwise create a new Requirement ID, state Active and declaration provenance;
8. commit under authoritative active semantic uniqueness;
9. concurrent uniqueness race resolves the winning existing Active Requirement.

Declaration never:
- calls Connectivity Decision as a side effect;
- materializes an Access Rule;
- claims Allowed/NotAllowed;
- claims configured/observed access.

## Applicability mutation

Semantic command:

`SetConnectivityRequirementApplicability(requirementId, applicability, actor, effectiveTime)`.

Behavior:
1. load authoritative Requirement;
2. evaluate `SetConnectivityRequirementApplicability` against stored RequirementGovernanceScope;
3. denied/unknown authority fails closed;
4. Retired Requirement rejects mutation;
5. same value returns explicit no-op and creates no audit record;
6. accepted change preserves Requirement ID, scope, Dependent and interaction;
7. accepted change and audit commit atomically.

## Justification mutation

Semantic command:

`SetConnectivityRequirementJustification(requirementId, justification, actor, effectiveTime)`.

Behavior:
1. justification remains non-empty;
2. authority action is `SetConnectivityRequirementJustification`;
3. stored scope is authoritative;
4. Retired Requirement rejects mutation;
5. same value is an explicit no-op with no audit;
6. accepted change preserves identity-defining fields and commits with business audit atomically.

## Retirement

Semantic command:

`RetireConnectivityRequirement(requirementId, actor, effectiveTime)`.

Behavior:
1. load authoritative Requirement;
2. evaluate `RetireConnectivityRequirement` against stored RequirementGovernanceScope;
3. denied/unknown authority fails closed;
4. `Active -> Retired` is the only accepted lifecycle transition;
5. already Retired returns explicit no-op;
6. retirement preserves Requirement ID, scope, Dependent and interaction;
7. accepted retirement and audit commit atomically;
8. retirement creates no Access Policy side effect.

## Workspace reads

Semantic queries:

`ListConnectivityRequirements(actor, effectiveTime, page, pageSize)`

`GetConnectivityRequirement(requirementId, actor, effectiveTime)`

Authority action: `ReadConnectivityRequirement`.

Behavior:
1. list discovers effective unambiguous `ReadConnectivityRequirement` scopes;
2. ambiguous scopes fail closed and expose no Requirement rows;
3. list returns Requirements whose stored governance scope is permitted;
4. details load by Requirement ID, then evaluate read authority against stored scope;
5. denied/unknown read returns no Requirement data;
6. reads do not mutate business truth;
7. read authority does not imply mutation authority.

## Authority actions

I13 accepted actions:

```text
DeclareConnectivityRequirement
ReadConnectivityRequirement
SetConnectivityRequirementApplicability
SetConnectivityRequirementJustification
RetireConnectivityRequirement
```

There is no broad `ManageConnectivityRequirement` permission in I13.

Historical actor/provenance recorded on a Requirement is not authority to act later.

## Provenance and audit

Declaration records:
- Requirement ID;
- actor ID;
- effective action time;
- RequirementGovernanceScope;
- authority reference;
- exact Required Semantic Interaction;
- ACC validation/reference where available;
- initial applicability;
- initial justification.

Accepted applicability/justification/retirement changes record:
- Requirement ID;
- previous/new business value or lifecycle transition;
- actor ID;
- effective action time;
- stored governance scope;
- authority reference.

Technical logs do not replace business audit.

## Concurrency

Declaration correctness must be linearizable enough at the authoritative active-semantic-uniqueness boundary that concurrent/retried declarations of the same active semantic key yield one Requirement ID.

Property/lifecycle mutations require version-aware or equivalent atomic consistency:
- stale conflicting change cannot silently overwrite accepted business truth;
- same requested value remains idempotent;
- mutation state and audit are one transaction.

Exact locking mechanics are infrastructure choices.

## Errors / non-results

- authority denied/unknown -> action rejected;
- invalid/unknown ACC interaction -> no Requirement created;
- Dependent not participating in interaction -> invalid Requirement subject;
- blank justification -> invalid declaration/mutation;
- invalid applicability window -> invalid value;
- unknown Requirement -> explicit not-found;
- mutation on Retired Requirement -> explicit lifecycle rejection;
- same applicability/justification/retirement requested -> explicit no-op, no audit;
- persistence/commit uncertainty -> no reported successful mutation unless authoritative outcome is established.

## Commands / queries

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

No domain event is required merely for ceremony.

## Deferred growth

Not part of I13:
- abstract Application-level or Resource-level Dependents;
- abstract/non-exact required interactions;
- alternatives between multiple acceptable interactions;
- recurring/calendar conditions;
- approval/decision lifecycle;
- Requirement-to-Policy Alignment;
- configured/observed satisfaction;
- impact analysis.
