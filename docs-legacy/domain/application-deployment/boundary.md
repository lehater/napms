# Application Deployment — strategic boundary

Status: `Strategic boundary revalidated 2026-09-16; Tactical model pending alignment`.

## Purpose

Own the independently changing truth of concrete deployed application Component instances and the Resource on which each instance is deployed.

## Ownership

Application Deployment owns `ComponentDeployment` identity/lifecycle and the exact relation from one ACC Component to one RC Resource for each concrete deployment instance.

It does not own Application/Component/Interaction meaning (ACC), Resource identity/address/scope/responsibility (RC), Policy Rule/governance lifecycle (Access Policy), enforcement placement (NEP), or provider runtime/container/orchestrator identity.

## Minimal strategic model

```text
ComponentDeployment
    ComponentDeploymentId
    ComponentRef
    ResourceRef
```

For the first MVP:

- one Component Deployment references exactly one Component;
- one Component Deployment references exactly one Resource;
- deploying the same Component on another Resource creates another Component Deployment;
- several Component Deployments of one Component may coexist and are independently selectable/governable;
- replacing one deployment with another Resource-backed instance creates another Component Deployment rather than mutating a whole-Application placement set;
- changing the Resource AddressSpace does not change ComponentDeployment identity because AddressSpace remains RC realization truth.

The target policy path requires no stable whole-Application `ApplicationDeployment` identity.

## Public relationships

```text
ACC -> AD: ComponentRef
RC  -> AD: opaque ResourceRef
AD  -> Access Policy: ComponentDeploymentRef -> ComponentRef + ResourceRef
AD  -> Required Policy Materialization: ComponentDeploymentRef -> ComponentRef + ResourceRef
AD  -> Evidence Access Recognition: ResourceRef -> matching ComponentDeploymentRef candidates
```

A missing/unavailable deployment resolution is semantically distinct from a known absence. Consumers must not fabricate a deployment from Resource metadata or ACC definitions.

## Identity and continuity rule

A Component Deployment is the identity of one concrete deployed Component instance for the access domain.

Its `ComponentRef` and `ResourceRef` establish what is deployed and where for that deployment identity. Deploying the same Component on another Resource is a different instance and therefore a different Component Deployment.

Resource address changes do not create another Component Deployment because the Resource itself remains the same.

The exact lifecycle vocabulary (`Active`, `Retired`, etc.) and whether Component/Resource references are immutable fields or invariant-protected transitions are Tactical DDD questions. The first MVP does require historical/external references to remain explainable rather than being silently retargeted to another deployment instance.

## Resource/address binding decision

For current scope, AD has no endpoint/address binding concept beyond Resource identity:

```text
ComponentDeployment.ResourceRef
        -> RC Resource
        -> effective HostAddress | Prefix
```

Multiple simultaneous addresses/interfaces, VIPs, management/data separation and deployment-specific network exposure are outside the current target.

`ResourceEndpointRef`, `DeploymentEndpointBinding` and provider-runtime identities are not part of the first target contract.

## Policy implication

One concrete policy connection refers directly to two Component Deployments:

```text
sourceComponentDeploymentRef
    -> destinationComponentDeploymentRef
```

The exact ACC Interaction Contract Revision supplies traffic semantics. Access Policy verifies each deployment's Component matches the corresponding Interaction endpoint.

A second deployment of the same Component on another Resource does not inherit policy automatically; it is a different concrete endpoint.

## Evidence recognition implication

Evidence Access Recognition may resolve an observed address to RC Resource identity and then ask AD which Component Deployment(s), if any, correspond to that Resource.

If correlation is missing or ambiguous, recognition remains unresolved. AD does not decide that observed traffic is authorized or desired.

## Scale constraint

AD publishes semantic deployment facts; it must not force downstream consumers into peer-private persistence traversal. Architecture may introduce rebuildable consumer-local projections/batches while AD remains semantic owner.

## Explicitly undecided

The selected MVP does not require a rule about whether several different Component Deployments may share one Resource. That choice must not be inferred from the one-Resource-per-ComponentDeployment invariant.

## Tactical owner

`tactical-model.md` must be revalidated against this boundary before G2 PASS.
