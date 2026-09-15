# Application Deployment — Tactical DDD model

## Purpose

Application Deployment owns the identity and continuity of one logical Application deployment and the current Component-to-Resource placement truth used by governance and technical materialization.

It does not own runtime instances, processes, containers, interfaces, listeners, addresses, deployment-specific endpoints or provider/orchestrator state.

## Aggregate root — ApplicationDeployment

```text
ApplicationDeployment {
    applicationDeploymentId
    applicationRef
    componentPlacements: Set<ComponentPlacement>
}
```

`ApplicationDeployment` is the semantic identity and consistency owner for its current placement set.

`applicationDeploymentId` identifies one logical deployment and is independent of current Resources and addresses. Adding, removing or replacing placements, scaling one Component across Resources, migrating Resources or changing Resource addresses does not by itself change deployment identity. Changing the referenced Application requires a different ApplicationDeployment identity.

## ComponentPlacement

```text
ComponentPlacement = (ComponentRef, ResourceRef)
```

`ComponentPlacement` is a relation value owned by its ApplicationDeployment. It has no independent semantic identity or lifecycle.

- the same `(ComponentRef, ResourceRef)` pair cannot occur twice in one ApplicationDeployment;
- one Component may be placed on zero, one or many Resources;
- one Resource may host placements for several Components;
- removing and re-adding the same pair does not imply continuity of a separately identified placement entity.

## Placement truth

For one ApplicationDeployment and Component:

```text
CurrentPlacements(applicationDeploymentRef, componentRef)
    = Set<ResourceRef>
```

The set is authoritative current AD truth.

- empty set = AD knows the Component currently has no placement in this ApplicationDeployment;
- non-empty set = every ResourceRef in the set is an applicable current placement;
- unavailable or unresolved AD truth is distinct from an empty set.

Consumers must preserve all members and may not choose an arbitrary Resource when several placements exist.

AD may publish a projection equivalent to:

```text
ApplicationDeploymentPlacementView {
    applicationDeploymentRef
    applicationRef
    placements: Set<(ComponentRef, ResourceRef)>
}
```

A consumer must be able to distinguish a complete empty set, a complete non-empty set and an unresolved result. The transport representation and failure signalling mechanism belong to Architecture.

## Interaction applicability

For an ACC `InteractionContractRevision` with source and destination Components, an ApplicationDeployment can realize an endpoint when:

1. the deployment references the Application containing that Component; and
2. the Component has at least one current placement ResourceRef in the deployment.

For a governed source/destination deployment pair, all applicable endpoint placements are preserved. AD does not hide placements to simplify downstream governance or materialization.

AG owns approval-obligation semantics. RC owns Resource scope and address truth. ACC owns Interaction identity and traffic semantics.

## Domain operations

```text
EstablishApplicationDeployment(applicationRef)
PlaceComponent(componentRef, resourceRef)
UnplaceComponent(componentRef, resourceRef)
```

A move, replacement or horizontal scale operation is represented by the resulting valid placement set; it is not a separate AD domain entity.

## Invariants

1. Every ApplicationDeployment references exactly one ACC `ApplicationRef`.
2. Every placed `ComponentRef` belongs to that Application according to ACC public semantics.
3. Every placement references one opaque RC `ResourceRef`; AD does not copy Resource address, responsibility or scope semantics.
4. The current placement set contains no duplicate `(ComponentRef, ResourceRef)` pair.
5. Placement multiplicity is unrestricted beyond set uniqueness.
6. ApplicationDeployment identity is independent of its current placement set.
7. Resource AddressSpace changes do not change ComponentPlacement meaning.
8. Interaction identity and traffic semantics remain in ACC.
9. AD publishes current placement truth; it does not claim independently addressable placement history or runtime inventory semantics.
