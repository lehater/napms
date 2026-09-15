# Application Deployment — strategic boundary

Status: `Strategic boundary accepted; current Resource binding contract closed`.

## Purpose

Own the independently changing truth of which logical deployment of an Application exists and which access-domain Resources its Components are placed on.

## Ownership

Application Deployment owns `ApplicationDeployment` identity/continuity, deployment lifecycle semantics, Component-to-Resource placement truth (`ComponentPlacement`), and publication of placement facts needed by governance/materialization.

It does not own Application/Component/Interaction meaning (ACC), Resource identity/address/scope/responsibility (RC), authorization workflow (AG), Policy Rule truth (AP), enforcement placement (NEP), or provider runtime/container/orchestrator truth.

## Minimal strategic model

```text
ApplicationDeployment
    ApplicationDeploymentId
    ApplicationRef

ComponentPlacement
    ApplicationDeploymentRef
    ComponentRef
    ResourceRef
```

A placed Component belongs to the Application referenced by its ApplicationDeployment. An ApplicationDeployment need not place every Component of the Application.

## Identity and lifecycle rule

`ApplicationDeployment` preserves identity while continuity of the same logical deployment is preserved. Ordinary horizontal scaling, Resource migration and Component placement replacement do not alone create a new ApplicationDeployment identity.

Exact lifecycle vocabulary, move-versus-replacement mechanics and same-Component/same-Resource multiplicity remain Tactical-open.

## Public relationships

```text
ACC -> AD: ApplicationRef / ComponentRef
RC  -> AD: opaque ResourceRef
AM  -> AD: EffectiveAuthority(actor, action, scope, time)
AD  -> AG: source/destination ApplicationDeploymentRef as governed applicability
AD  -> RPM: applicable ComponentPlacement / ResourceRef projection with time and resolution state
```

## Resource/address binding decision

For the current scope, AD has no endpoint or address binding concept. `ComponentPlacement` references exactly a Resource; RC resolves that Resource at a logical time to at most one effective `AddressSpace = HostAddress | Prefix`.

```text
ComponentPlacement.ResourceRef
        -> RC Resource
        -> effective HostAddress | Prefix
```

Address changes do not change ApplicationDeployment or ComponentPlacement identity. Multiple simultaneous addresses/interfaces, VIPs, management/data separation and deployment-specific network exposure are explicitly out of scope until a confirmed use case requires them.

`ResourceEndpointRef`, `DeploymentEndpointBinding`, listener/interface and provider-runtime identities are therefore not part of the current target contract.

## Governance implication

```text
GovernedInteractionSubject {
    interactionContractRevisionRef
    sourceApplicationDeploymentRef
    destinationApplicationDeploymentRef
}
```

This identity is deliberately above individual Component placements and technical addresses. Placement changes may nevertheless change Resource Scope Affiliations and approval obligations; resulting authorization behavior remains an S1 product question.

## Scale constraint

AD publishes semantic placement facts; it must not force downstream consumers into per-object remote traversal at scale. Architecture may introduce rebuildable consumer-local projections/batches while AD remains the semantic owner.