# Application Deployment — MVP Tactical DDD model

Status: `S2 MVP Tactical model accepted for convergence 2026-09-15`.

## Purpose

Own the identity/continuity of one logical deployment of an Application and the current Component-to-Resource placement truth needed by governance and technical materialization.

This model is deliberately smaller than a runtime/orchestrator inventory. It does not model pods, processes, containers, interfaces, listeners, addresses or deployment-specific endpoints.

## Aggregate root — ApplicationDeployment

```text
ApplicationDeployment {
    applicationDeploymentId
    applicationRef
    componentPlacements: Set<ComponentPlacement>
}
```

`ApplicationDeployment` is the semantic identity/consistency owner for its current placement set.

### Identity / sameness

`applicationDeploymentId` identifies one logical deployment and is never derived from current Resources or addresses.

The same ApplicationDeployment remains the same while continuity of that logical deployment is preserved, including:

- adding/removing placement of a Component;
- horizontal scaling of one Component to several Resources;
- Resource migration;
- Resource address change;
- ordinary replacement of one placement by another.

Changing the referenced Application is not a mutation of the same ApplicationDeployment; it requires a different logical deployment identity.

## ComponentPlacement — relation value, not independent entity

For the first MVP:

```text
ComponentPlacement = (ComponentRef, ResourceRef)
```

`ComponentPlacement` has no independent semantic identity or lifecycle. It is a current relation value owned by its ApplicationDeployment.

Consequences:

- there is no `ComponentPlacementId` requirement in the MVP domain;
- the exact same `(ComponentRef, ResourceRef)` pair cannot occur twice in one ApplicationDeployment;
- one Component may be placed on zero, one or many distinct Resources;
- one Resource may host placements for several Components;
- removing and later re-adding the same pair does not imply continuity of a separately identified placement entity;
- placement history/audit may be added later only if a concrete product requirement needs independently addressable historical placement facts.

This explicitly avoids the false invariant “exactly one placement per Component”.

## Placement-set semantics

For one ApplicationDeployment and Component:

```text
CurrentPlacements(applicationDeploymentRef, componentRef)
    = Set<ResourceRef>
```

The set is authoritative AD truth for the current model.

- empty set = AD knows that the Component currently has no placement in this ApplicationDeployment;
- non-empty set = every ResourceRef in the set is an applicable current placement;
- failure to obtain/resolve AD truth is **not** the same as an empty set and must remain unresolved at the consuming boundary.

Downstream consumers must preserve all members of the set. They may not choose one arbitrary Resource when several placements exist.

## Invariants

1. Every ApplicationDeployment references exactly one ACC `ApplicationRef`.
2. Every placed `ComponentRef` must belong to that referenced Application according to ACC public semantics.
3. Every placement references one opaque RC `ResourceRef`; AD does not copy Resource address, responsibility or scope semantics.
4. The current placement set contains no duplicate `(ComponentRef, ResourceRef)` pair.
5. Placement multiplicity is unrestricted by the MVP domain beyond set uniqueness.
6. ApplicationDeployment identity is independent of its current placement set.
7. Resource AddressSpace changes do not mutate ComponentPlacement meaning because placement references Resource identity, not address.
8. Interaction identity/traffic semantics remain in ACC; a placement never embeds or owns an Interaction.

## Minimal domain operations

The MVP needs only relation-set semantics:

```text
EstablishApplicationDeployment(applicationRef)
PlaceComponent(componentRef, resourceRef)
UnplaceComponent(componentRef, resourceRef)
```

These names express domain meaning, not frozen API commands.

A “move” or “replacement” is not a separate required domain concept for MVP. It is a change from one valid placement set to another. This avoids inventing atomic move semantics that the product has not required.

Likewise, horizontal scaling is simply a placement set containing several ResourceRefs for the same ComponentRef.

## Interaction applicability

Given an ACC InteractionContractRevision with source/destination endpoint Components, a logical ApplicationDeployment can realize one endpoint only when:

1. the deployment references the Application containing that endpoint Component; and
2. the endpoint Component has at least one current placement ResourceRef in that deployment.

This is only deployment/placement applicability. AG remains responsible for approval-obligation resolvability; RC remains responsible for Resource scope/address truth.

For a governed source/destination deployment pair, all applicable endpoint placements are preserved. Governance/materialization may fail closed if required downstream scope/address facts are unresolved; AD does not hide a placement to manufacture a simpler result.

## Published semantic values

AD may publish a current placement projection equivalent to:

```text
ApplicationDeploymentPlacementView {
    applicationDeploymentRef
    applicationRef
    placements: Set<(ComponentRef, ResourceRef)>
}
```

or a component-filtered equivalent.

The semantic contract is the complete current set for the requested scope, not a specific DTO or transport shape.

A consumer must be able to distinguish:

- complete current empty set;
- complete current non-empty set;
- unavailable/unresolved result.

The mechanism for completeness/failure signalling is Architecture, not Tactical DDD.

## Lifecycle classification

AD owns ApplicationDeployment lifecycle in the strategic sense, but the accepted first MVP behavior does not currently distinguish `Planned`, `Running`, `Stopped`, `Retired` or similar deployment states.

No lifecycle state machine is therefore introduced merely for implementation convenience.

For the current MVP DDD:

- ApplicationDeployment identity/continuity is defined;
- current placement mutation is defined;
- richer deployment lifecycle vocabulary remains deliberately deferred until an accepted journey gives those states observable meaning.

This deferral is non-blocking for the first happy path because selection/governance/materialization depend on the current published deployment and placement facts, not on an unaccepted lifecycle enum.

## Historical-state classification

The MVP domain does not require independently queryable ComponentPlacement history. AG preserves the approval basis/provenance used for governance decisions, so historical authorization evidence does not require AD to invent a placement-history aggregate.

If future audit/product requirements require “what exact placements existed at time T?” as AD-owned domain truth, temporal placement facts can be introduced then without changing ApplicationDeployment identity or the current set semantics above.

## Deliberately deferred

- deployment lifecycle states beyond current identity/continuity;
- placement-history entity IDs and temporal fact model;
- ordering/ordinal of replicas;
- desired replica count;
- runtime instance/process/container identity;
- deployment-specific endpoint/listener/interface selection;
- multiple address selection or VIP semantics;
- atomic move/replace workflow;
- provider/orchestrator state.

## Tactical coherence result

For the first MVP vertical, AD now has sufficient Tactical semantics:

- one stable ApplicationDeployment aggregate identity;
- ComponentPlacement as a set relation value rather than an invented entity;
- zero/one/many placements per Component are valid;
- exact duplicate relations are not;
- placement changes preserve deployment identity;
- all applicable placements are visible to AG/RPM;
- empty placement and unresolved access to placement truth cannot be conflated;
- no endpoint/address/runtime-instance ownership leaks into AD.

No remaining AD Tactical decision is required by the accepted first MVP happy path.
