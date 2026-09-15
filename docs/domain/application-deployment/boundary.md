# Application Deployment — strategic boundary

Status: `Strategic boundary accepted; Tactical model intentionally minimal`.

## Purpose

Own the independently changing truth of which logical deployment of an Application exists and which access-domain Resources its Components are placed on.

## Ownership

Application Deployment owns:

- `ApplicationDeployment` identity and continuity;
- deployment lifecycle semantics;
- Component-to-Resource placement truth (`ComponentPlacement`);
- publication of deployment applicability/placement facts needed by governance and required-policy materialization.

It does not own:

- Application, Component or Interaction meaning — ACC;
- Resource identity, responsibility/scope or technical realization — RC;
- authorization/approval workflow — AG;
- effective Policy Rule truth — AP;
- technical enforcement placement — NEP;
- provider runtime/container/orchestrator truth unless a future accepted requirement introduces such semantics.

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

The exact create/activate/retire vocabulary, move-versus-replacement rule and same-Component/same-Resource multiplicity are Tactical-open.

## Public relationships

```text
ACC -> AD: ApplicationRef / ComponentRef
RC  -> AD: opaque ResourceRef
AM  -> AD: EffectiveAuthority(actor, action, scope, time)
AD  -> AG: source/destination ApplicationDeploymentRef as governed applicability
AD  -> RPM: applicable ComponentPlacement / ResourceRef projection with time and resolution state
```

AD must not expose ACC or RC private tactical structures as its own authority.

## Network exposure

Network exposure is a real placement-related concern but its model is not yet accepted. In particular, this boundary does not establish `ResourceEndpointRef`, `DeploymentEndpointBinding`, Environment, listener/interface, VIP, pod/container or other provider-specific concepts.

RC Tactical DDD must first establish what stable technical network meaning RC actually owns. AD Tactical DDD can then define the smallest semantic declaration/correlation it needs. If the result requires a cross-context contract change, route only that affected edge back through Strategic DDD.

## Governance implication

Working governed subject:

```text
GovernedInteractionSubject {
    interactionContractRevisionRef
    sourceApplicationDeploymentRef
    destinationApplicationDeploymentRef
}
```

This identity is deliberately above individual Component placements and technical addresses. Changes in placement may nevertheless change Resource Scope Affiliations and therefore approval obligations. Whether existing consent remains valid in that case is an S1 product-behavior question, not an AD invariant.

## Scale constraint

AD publishes semantic placement facts; it must not force downstream consumers into per-object remote traversal at scale. Architecture may introduce rebuildable consumer-local projections/batches while AD remains the semantic owner.
