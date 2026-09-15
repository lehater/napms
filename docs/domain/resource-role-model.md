# Resource Role Model

Status: `Strategic summary aligned to MVP DDD 2026-09-15`.

## Resource inclusion rule

A provider/device is not automatically a Resource. A first-class Resource exists when its stable access-domain identity/lifecycle matters to governed outcomes.

## Resource Catalogue ownership

RC owns:

```text
Resource identity / lifecycle
Resource -> effective AddressSpace [0..1] = HostAddress | Prefix
Resource Scope Affiliation
Resource Responsibility
```

AddressSpace is technical realization, not Resource identity. Address/prefix change therefore does not replace the Resource. Current target deliberately has no `ResourceEndpoint` identity and no multiple simultaneous addresses/interfaces.

## Application Deployment relation

AD, not RC, owns where application Components are placed:

```text
ApplicationDeployment
    -> current Set<(ComponentRef, ResourceRef)>
```

One Component may have zero, one or many current Resource placements in one logical ApplicationDeployment. RC does not own Application/Component semantics or placement continuity. AD does not own Resource address realization.

## Responsibility and authority

`ResourceScopeAffiliation(ResourceRef, ResponsibilityScopeRef, validity, provenance)` is RC truth. `ResourceResponsibility` is operational/contact truth. Neither grants actor authority.

Authority Management independently answers whether Actor A may perform Action X for Scope S at Time T. Access Governance owns how Resource scope facts establish bilateral approval obligations.

Changing scope affiliation/responsibility does not rewrite historical governance facts.

Accepted current-authorization behavior is:

- if the resolved source/destination approval obligations remain materially unchanged, the current AG grant remains valid;
- if they materially change, AG withdraws the current grant and publishes `AuthorizationWithdrawn`;
- the governed subject identity itself does not change merely because placement/scope/address facts changed;
- historical approvals do not silently restore authorization after withdrawal.

## Enforcement identity

Firewall identity and policy-locator relevance remain Network Enforcement Placement truth and are distinct from Resource identity and provider/device realization.

## Governed subject consequence

Current semantic authorization subject is:

```text
InteractionContractRevisionRef
+ sourceApplicationDeploymentRef
+ destinationApplicationDeploymentRef
```

Resource AddressSpace and ComponentPlacement are downstream/current applicability facts, not subject identity.

## Guardrail

This is a problem-space ownership model, not a database schema, class hierarchy, API or deployment topology.
