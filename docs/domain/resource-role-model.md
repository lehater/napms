# Resource Role Model

Status: `Strategic summary aligned to simplified MVP DDD 2026-09-16`.

## Resource inclusion rule

A provider/device is not automatically a Resource. A first-class Resource exists when its stable access-domain identity/lifecycle matters to managed outcomes.

## Resource Catalogue ownership

RC owns:

```text
Resource identity / lifecycle
Resource -> effective AddressSpace [0..1] = HostAddress | Prefix
Resource Scope Affiliation
Resource Responsibility
```

AddressSpace is technical realization, not Resource identity. Address/prefix change therefore does not replace the Resource.

Current target deliberately has no `ResourceEndpoint` identity and no multiple simultaneous addresses/interfaces.

## Application Deployment relation

Application Deployment, not RC, owns which concrete deployed Component instance uses a Resource:

```text
ComponentDeployment
    ComponentRef
    ResourceRef
```

One ComponentDeployment references exactly one Resource for the first MVP. Deploying the same Component on another Resource creates another ComponentDeployment identity.

RC does not own Application/Component semantics or ComponentDeployment identity. AD does not own Resource AddressSpace/scope/responsibility.

Changing Resource AddressSpace does not change ComponentDeployment identity because the deployment references Resource identity, not address.

The current MVP does not impose a domain rule prohibiting several different ComponentDeployments from referencing the same Resource.

## Responsibility and authority

`ResourceScopeAffiliation(ResourceRef, ResponsibilityScopeRef, validity, provenance)` is RC truth. `ResourceResponsibility` is operational/contact truth. Neither grants actor authority.

Authority Management independently answers whether Actor A may perform Action X for Scope S at Time T.

The simplified Access Policy MVP does **not** derive mandatory source/destination approval obligations from Resource Scope Affiliation. AP may consume Authority Management to protect a propose/decide/withdraw action, but the formal RuleChange decision is still one `Accepted | Rejected` outcome and customer-specific approval procedure is external to the baseline model.

Changing Resource scope affiliation/responsibility therefore does not, by itself, rewrite or invalidate a PolicyRule decision in the baseline MVP.

Future customer-specific governance may explicitly reuse RC scope facts and AM authority, but that requires a separate accepted requirement/domain extension.

## Enforcement identity

Firewall identity and policy-locator relevance remain Network Enforcement Placement truth and are distinct from Resource identity and provider/device realization.

## Policy consequence

Current concrete Policy Rule subject is the directed pair:

```text
sourceComponentDeploymentRef
+ destinationComponentDeploymentRef
```

The exact `revisionRef` is the Rule's proposed/current traffic semantics rather than connection identity.

Resource AddressSpace and Scope Affiliation are not PolicyRule identity.

## Evidence-recognition consequence

Evidence Access Recognition may correlate an observed address to Resource identity and then use Application Deployment to find matching ComponentDeployment candidates. Several or zero matches remain ambiguous/unresolved rather than being guessed by RC.

## Guardrail

This is a problem-space ownership model, not a database schema, class hierarchy, API or deployment topology.
