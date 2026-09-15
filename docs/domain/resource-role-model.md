# Resource Role Model

Status: `Strategic summary aligned 2026-09-15`.

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
ComponentPlacement -> opaque ResourceRef
```

RC does not own Application/Component semantics or placement lifecycle. AD does not own Resource address realization.

## Responsibility and authority

`ResourceScopeAffiliation(ResourceRef, ResponsibilityScopeRef, validity, provenance)` is RC truth. `ResourceResponsibility` is operational/contact truth. Neither grants actor authority.

Authority Management independently answers whether actor A may perform action X for scope S at time T. Access Governance owns how Resource scope facts establish bilateral approval obligations.

Changing scope affiliation/responsibility does not rewrite historical governance facts. Whether it changes current authorization validity is an active S1 Access Governance question.

## Enforcement identity

Logical Firewall / enforcement attachment identities remain Network Enforcement Placement truth and are distinct from Resource identity and provider/device realization.

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
