# Application Catalogue Domain Target Requirements

Status: `G1 behavior clarified; S2 ownership split aligned`.

Date: 2026-09-15.

## Scope

These requirements define application communication semantics and the accepted separation between Application Communication Catalogue (ACC), Application Deployment (AD) and Resource Catalogue (RC).

## Requirements

ACC shall:

1. model an Application as a reusable definition containing Components;
2. define each directed Interaction between a source Component and destination Component;
3. keep Interaction independent from deployment, Resource and address realization;
4. preserve decision-relevant interaction traffic as immutable `InteractionContractRevision` snapshots;
5. require each contract revision to contain one or more vendor-neutral traffic alternatives;
6. treat the complete set of alternatives in one revision as one atomic communication contract;
7. require independently governed traffic subsets to be separate Interactions;
8. publish stable opaque Application, Component, Interaction and InteractionContractRevision references.

AD shall:

9. model `ApplicationDeployment` as the stable logical deployment identity of one Application;
10. model `ComponentPlacement` as the fact that a Component of that Application is placed on one Resource;
11. allow ordinary scaling, Resource migration and placement replacement without changing ApplicationDeployment identity while logical deployment continuity is preserved;
12. publish placement Resource references without copying Resource address realization.

RC shall:

13. own Resource identity and effective network AddressSpace;
14. for the current scope, expose at most one effective AddressSpace per Resource at a logical time;
15. represent that AddressSpace as either one `HostAddress` or one `Prefix`;
16. allow address/prefix changes without changing Resource identity.

Governance shall identify the logical governed subject from:

```text
InteractionContractRevisionRef
+ sourceApplicationDeploymentRef
+ destinationApplicationDeploymentRef
```

Technical address realization is not part of that semantic subject identity.

## Current deployment/resource/address semantics

```text
ACC Component
    -> AD ComponentPlacement
        -> exactly one ResourceRef
            -> RC effective AddressSpace [0..1]
                = HostAddress | Prefix
```

A Resource with no resolved current AddressSpace makes downstream technical materialization unresolved. A Prefix remains a Prefix and need not be expanded to individual hosts.

## Explicit current limitation

The current target does not model several simultaneous addresses/prefixes on one Resource, multiple interfaces, endpoint purpose, VIPs, deployment-specific exposure, `ResourceEndpoint` or `DeploymentEndpointBinding`. Those concepts require a future confirmed use case before entering the target model.

## Acceptance invariants

A conforming target must prove at least:

- Interaction identity is Component-to-Component semantic identity and contains no deployment/Resource/address identity;
- a ComponentPlacement references one Component and one Resource;
- changing Resource address/prefix leaves Resource, ApplicationDeployment and governed-subject identity unchanged;
- moving/replacing placements does not by itself create a new ApplicationDeployment while logical deployment continuity remains;
- changing interaction traffic creates a new immutable contract revision;
- a consumer cannot authorize only one traffic alternative from an atomic revision;
- the published governed subject contains no ResourceEndpoint, IP address, protocol or port identity fields;
- no consumer persistence adapter requires SQL foreign keys across BC-owned storage.

## Superseded behavior

The 2026-09-14 requirement that ACC itself own `ComponentDeployment -> exactly one Resource`, that moving Resource necessarily create a new ComponentDeployment identity, and that ACC publish `DirectedInteractionIdentity{sourceComponentDeploymentRef, destinationComponentDeploymentRef, interactionContractRevisionRef}` is superseded by the accepted AD boundary and Interaction-template clarification.

Legacy runtime/migration artifacts may still use those terms and must be classified as current-state implementation rather than target domain truth.