# Resource Role Model

Status: `Strategic summary aligned to revalidated MVP DDD 2026-09-16`.

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

RC does not own Application/Component semantics or ComponentDeployment identity. Application Deployment does not own Resource AddressSpace/scope/responsibility.

Changing the AddressSpace of a Resource does not change ComponentDeployment identity because the deployment refers to Resource identity, not address.

The current MVP does not impose a domain rule prohibiting several different ComponentDeployments from referencing the same Resource.

## Responsibility and authority

`ResourceScopeAffiliation(ResourceRef, ResponsibilityScopeRef, validity, provenance)` is RC truth. `ResourceResponsibility` is operational/contact truth. Neither grants actor authority.

Authority Management independently answers whether Actor A may perform Action X for Scope S at Time T. Access Policy owns how the two Policy Rule endpoint Resources and their scope facts establish bilateral approval obligations.

Changing scope affiliation/responsibility does not rewrite historical policy-governance facts.

Accepted current-policy behavior is:

- if an Active Rule's current approval obligations remain materially valid, its current effective revision remains effective;
- if accepted lifecycle rules determine that materially changed obligations invalidate current consent, Access Policy withdraws current effectiveness while preserving history;
- reauthorization requires a new RuleChange under current obligations;
- old approved RuleChanges do not silently reactivate a withdrawn Rule.

## Enforcement identity

Firewall identity and policy-locator relevance remain Network Enforcement Placement truth and are distinct from Resource identity and provider/device realization.

## Policy consequence

Current concrete Policy Rule subject is the directed pair:

```text
sourceComponentDeploymentRef
+ destinationComponentDeploymentRef
```

The exact `revisionRef` is the Rule's proposed/current traffic semantics rather than connection identity.

Resource AddressSpace is downstream technical realization, not Policy Rule identity.

## Evidence-recognition consequence

Evidence Access Recognition may correlate an observed address to Resource identity and then use Application Deployment to find matching ComponentDeployment candidates. Several or zero matches remain ambiguous/unresolved rather than being guessed by RC.

## Guardrail

This is a problem-space ownership model, not a database schema, class hierarchy, API or deployment topology.
