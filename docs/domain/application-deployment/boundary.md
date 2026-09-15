# Application Deployment — strategic boundary

## Purpose

Own the independently changing truth of which logical deployment of an Application exists and which Resources its Components are currently placed on.

## Ownership

Application Deployment owns `ApplicationDeployment` identity/continuity, Component-to-Resource placement truth (`ComponentPlacement`) and publication of current placement facts needed by governance and materialization.

It does not own Application/Component/Interaction meaning (ACC), Resource identity/address/scope/responsibility (RC), authorization workflow (AG), Policy Rule truth (AP), enforcement placement (NEP), or provider runtime/container/orchestrator truth.

## Strategic model

```text
ApplicationDeployment
    ApplicationDeploymentId
    ApplicationRef
    ComponentPlacements: Set<(ComponentRef, ResourceRef)>
```

A placed Component belongs to the Application referenced by its ApplicationDeployment. A deployment need not place every Component of the Application.

`ComponentPlacement` is a relation value `(ComponentRef, ResourceRef)` inside the current placement set, not a separately identified entity. One Component may be placed on zero, one or many Resources; the same pair cannot occur twice.

## Identity and continuity

`ApplicationDeployment` preserves identity while the same logical deployment remains continuous. Horizontal scaling, Resource migration, Component placement replacement and Resource address changes do not by themselves create a new ApplicationDeployment identity.

The current AD model has no `Planned/Running/Stopped/Retired` state machine. It owns logical deployment identity and current placement truth only.

## Public relationships

```text
ACC -> AD: ApplicationRef / ComponentRef
RC  -> AD: opaque ResourceRef
AM  -> AD: EffectiveAuthority(actor, action, scope, time)
AD  -> AG: source/destination ApplicationDeploymentRef plus applicable current endpoint placements
AD  -> materialization: complete applicable ComponentPlacement / ResourceRef set
```

A complete empty placement set is distinct from an unavailable or unresolved placement result. Consumers must not treat missing evidence as an empty set.

## Resource and address boundary

AD has no endpoint or address-binding concept. `ComponentPlacement` references exactly one Resource; RC resolves that Resource to its current `AddressSpace = HostAddress | Prefix` when required.

```text
ComponentPlacement.ResourceRef
        -> RC Resource
        -> current HostAddress | Prefix
```

Address changes do not change ApplicationDeployment or ComponentPlacement meaning. Multiple simultaneous addresses/interfaces, VIPs, management/data separation, deployment-specific network exposure, `ResourceEndpointRef`, `DeploymentEndpointBinding`, listener/interface identity and provider-runtime identity are not part of the current AD contract.

## Governance implication

```text
GovernedInteractionSubject {
    interactionContractRevisionRef
    sourceApplicationDeploymentRef
    destinationApplicationDeploymentRef
}
```

Governed-subject identity is above individual Component placements and technical addresses. AD publishes complete placement truth; AG owns whether placement/scope changes alter approval obligations or current authorization.

## Scale constraint

AD publishes semantic placement facts without requiring downstream consumers to use per-object remote traversal. Architecture may use rebuildable consumer-local projections or batches while AD remains the semantic owner.

## Tactical owner

`tactical-model.md` defines the current aggregate, placement-set semantics, operations and invariants for this boundary.
