# Application Deployment — strategic boundary

Status: `Strategic boundary accepted; MVP Tactical model aligned 2026-09-15`.

## Purpose

Own the independently changing truth of which logical deployment of an Application exists and which access-domain Resources its Components are currently placed on.

## Ownership

Application Deployment owns `ApplicationDeployment` identity/continuity, Component-to-Resource placement truth (`ComponentPlacement`), and publication of current placement facts needed by governance/materialization.

It does not own Application/Component/Interaction meaning (ACC), Resource identity/address/scope/responsibility (RC), authorization workflow (AG), Policy Rule truth (AP), enforcement placement (NEP), or provider runtime/container/orchestrator truth.

## Minimal strategic model

```text
ApplicationDeployment
    ApplicationDeploymentId
    ApplicationRef
    ComponentPlacements: Set<(ComponentRef, ResourceRef)>
```

A placed Component belongs to the Application referenced by its ApplicationDeployment. An ApplicationDeployment need not place every Component of the Application.

For the MVP Tactical model, `ComponentPlacement` is a relation value `(ComponentRef, ResourceRef)` inside the deployment's current placement set, not a separately identified entity. One Component may therefore be placed on zero, one or many distinct Resources; the exact same pair is not duplicated.

## Identity and continuity rule

`ApplicationDeployment` preserves identity while continuity of the same logical deployment is preserved. Ordinary horizontal scaling, Resource migration and Component placement replacement do not alone create a new ApplicationDeployment identity.

The accepted first MVP does not require a `Planned/Running/Stopped/Retired` state machine, so richer lifecycle vocabulary remains explicitly deferred rather than invented by Tactical DDD.

## Public relationships

```text
ACC -> AD: ApplicationRef / ComponentRef
RC  -> AD: opaque ResourceRef
AM  -> AD: EffectiveAuthority(actor, action, scope, time)
AD  -> AG: source/destination ApplicationDeploymentRef plus applicable current endpoint placements
AD  -> RPM: complete applicable ComponentPlacement / ResourceRef set for the requested deployment/component
```

A complete empty placement set is semantically different from an unavailable/unresolved placement result. Consumers must not treat missing evidence as an empty set.

## Resource/address binding decision

For the current scope, AD has no endpoint or address binding concept. `ComponentPlacement` references exactly a Resource; RC resolves that Resource at a logical time to at most one effective `AddressSpace = HostAddress | Prefix`.

```text
ComponentPlacement.ResourceRef
        -> RC Resource
        -> effective HostAddress | Prefix
```

Address changes do not change ApplicationDeployment or ComponentPlacement meaning. Multiple simultaneous addresses/interfaces, VIPs, management/data separation and deployment-specific network exposure are explicitly out of scope until a confirmed use case requires them.

`ResourceEndpointRef`, `DeploymentEndpointBinding`, listener/interface and provider-runtime identities are therefore not part of the current target contract.

## Governance implication

```text
GovernedInteractionSubject {
    interactionContractRevisionRef
    sourceApplicationDeploymentRef
    destinationApplicationDeploymentRef
}
```

This identity is deliberately above individual Component placements and technical addresses.

Accepted AG behavior already covers placement/scope changes: when they leave approval obligations materially unchanged, current authorization remains; when they materially change obligations, AG withdraws current authorization without changing governed-subject identity.

AD does not own that decision. It publishes placement truth and preserves all applicable placements rather than selecting a convenient subset.

## Scale constraint

AD publishes semantic placement facts; it must not force downstream consumers into per-object remote traversal at scale. Architecture may introduce rebuildable consumer-local projections/batches while AD remains the semantic owner.

## Tactical owner

The canonical MVP Tactical model is `tactical-model.md`. It closes placement identity/multiplicity/current-set semantics for the first happy path while deliberately deferring runtime-instance, endpoint and richer lifecycle concepts.
