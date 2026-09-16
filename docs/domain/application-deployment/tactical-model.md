# Application Deployment — MVP Tactical DDD model

Status: `S2 MVP Tactical model revalidated 2026-09-16`.

## Purpose

Own the identity and lifecycle of one concrete deployed Component instance and its exact Resource relation for the access domain.

The model deliberately does not represent provider pods, processes, containers, interfaces, listeners, addresses or a whole-Application deployment aggregate.

## Aggregate root — ComponentDeployment

```text
ComponentDeployment {
    componentDeploymentId
    componentRef
    resourceRef
    lifecycle: Active | Retired
}
```

`ComponentDeployment` is the semantic identity/consistency owner for one concrete deployed Component instance.

### Identity / sameness

`componentDeploymentId` is the stable AD-owned identity.

Two Component Deployments are different when they represent different concrete deployed instances, including when the same ACC Component is deployed on two different Resources.

```text
Component A + Resource R1 -> CD-1
Component A + Resource R2 -> CD-2
```

`componentRef` and `resourceRef` are identity-defining semantic facts for the instance and do not change in place for the first MVP.

Consequences:

- moving/redeploying the same Component to another Resource creates another Component Deployment;
- changing the referenced Component creates another Component Deployment;
- changing the Resource AddressSpace does **not** create another Component Deployment because Resource identity is unchanged;
- a retired Component Deployment is not repointed to a replacement Resource or Component;
- downstream historical references remain meaningful.

A generated persistence row identifier is not a separate semantic identity beyond `ComponentDeploymentId`.

## Lifecycle

Target lifecycle is terminal:

```text
Active -> Retired
```

There is no normal semantic hard delete and no `Retired -> Active` reactivation in the first MVP.

Retirement means the concrete deployed instance is no longer current/selectable for new policy work. Historical Policy Rules/change records/evidence may continue to refer to it for explanation.

Whether retirement is blocked while a current effective Policy Rule references the deployment is a cross-context product/architecture concern that must preserve historical truth; AD itself does not silently mutate peer policy.

No richer `Planned/Running/Stopped` runtime state machine is required.

## Core invariants

1. every Component Deployment has one stable `ComponentDeploymentId`;
2. every Component Deployment references exactly one ACC `ComponentRef`;
3. every Component Deployment references exactly one opaque RC `ResourceRef`;
4. `componentRef` and `resourceRef` are fixed for that Component Deployment identity in the first MVP;
5. deploying the same Component on another Resource creates another Component Deployment identity;
6. Resource AddressSpace changes do not change ComponentDeployment identity;
7. Interaction identity/traffic semantics remain ACC truth and are never embedded as AD-owned semantics;
8. Resource address, responsibility and scope remain RC truth;
9. Retired Component Deployments remain referentially explainable and are excluded from normal new-selection semantics.

The MVP does **not** impose a uniqueness rule preventing different Component Deployments from referencing the same Resource because no accepted behavior currently requires that restriction.

## Minimal domain operations

```text
EstablishComponentDeployment(componentRef, resourceRef)
RetireComponentDeployment(componentDeploymentId)
```

These are semantic operations, not frozen API command names.

There is deliberately no `MoveComponentDeployment` operation. A deployment on a different Resource is a different Component Deployment.

Horizontal replication is represented by several Component Deployments of the same `ComponentRef`, not by one deployment with a placement set or replica count.

## Interaction applicability

Given an ACC `InteractionContractRevision`:

```text
revision
  -> Interaction
      sourceComponentRef
      destinationComponentRef
```

one source/destination Component Deployment pair is compatible only when:

```text
sourceDeployment.componentRef == sourceComponentRef
destinationDeployment.componentRef == destinationComponentRef
```

AD owns only each deployment's Component/Resource facts. Access Policy owns whether that compatible concrete pair is proposed/authorized.

## Published semantic contract

AD publishes a public projection equivalent to:

```text
ResolveComponentDeployment(componentDeploymentRef)
-> {
     componentDeploymentRef
     componentRef
     resourceRef
     lifecycle/currentness
   }
| unresolved
```

Exact DTO/transport/persistence shape is Architecture.

Consumers must distinguish a known Retired deployment, a known Active deployment and an unavailable/unresolved lookup where that distinction affects behavior.

For evidence recognition, AD may also support a semantic query equivalent to:

```text
FindActiveComponentDeploymentsByResource(resourceRef)
-> ComponentDeploymentRef[] | unresolved
```

Several matches are valid because the current domain does not prohibit several Component Deployments on one Resource. Recognition must preserve ambiguity rather than choose arbitrarily.

## Historical-state classification

The first MVP does not require a separately queryable time series of deployment mutations because Component/Resource references do not mutate in place. Historical identity is preserved by the durable Component Deployment plus terminal retirement.

If future requirements need exact activation/retirement effective intervals or provider runtime history, that can be added without returning to a mutable placement-set model.

## Deliberately deferred

- whether several Component Deployments may share one Resource as a product constraint;
- activation/retirement effective-time interval modelling beyond preserved provenance;
- provider pod/container/process identity;
- desired replica count/grouping;
- deployment-specific interface/listener/address selection;
- several simultaneous addresses or VIP semantics;
- provider/orchestrator state.

## Tactical coherence result

The revalidated AD model now matches the accepted concrete endpoint behavior:

- one aggregate identity per concrete deployed Component instance;
- one Component and one Resource per instance;
- replicas are separate identities;
- redeployment to another Resource creates another identity;
- Resource address change does not;
- `Active -> Retired` preserves identity/history without hard delete;
- consumers use opaque `ComponentDeploymentRef` rather than peer-private persistence.
