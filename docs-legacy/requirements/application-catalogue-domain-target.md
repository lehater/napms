# Application Catalogue Domain Target Requirements

Status: `G1 revalidated for concrete Component deployment semantics 2026-09-16`.

Date: 2026-09-16.

## Scope

These requirements define observable application communication, component deployment and Resource realization behavior required by the selected first-MVP policy path. They do not prescribe aggregate, table, service or package boundaries.

## Requirements

Application communication behavior shall:

1. model an Application as a reusable definition containing Components;
2. define each directed Interaction between a source Component and destination Component of the same Application;
3. reject an Interaction whose source and destination Components belong to different Applications;
4. keep Interaction meaning independent from deployment, Resource and address realization;
5. preserve decision-relevant interaction traffic as immutable `InteractionContractRevision` snapshots;
6. require each contract revision to contain one or more vendor-neutral traffic alternatives;
7. treat the complete set of alternatives in one revision as one atomic communication contract;
8. require independently governed traffic subsets to be separate Interactions;
9. make a material traffic change create a new immutable revision while preserving the Interaction itself.

Component deployment behavior shall:

10. represent one concrete deployed instance of one Component on one Resource as one independently addressable Component Deployment;
11. bind each Component Deployment to exactly one Component and exactly one Resource for the first MVP;
12. create a different Component Deployment when the same Component is deployed on another Resource;
13. allow several independently addressable Component Deployments of the same Component to coexist;
14. not require a whole-Application logical deployment identity in order to create, govern or export access between concrete deployed Components;
15. preserve enough identity to distinguish two otherwise identical Component instances deployed on different Resources;
16. leave richer runtime/container/orchestrator instance semantics outside the first MVP unless separately required.

Resource behavior shall:

17. own stable Resource identity/lifecycle independently from Component Deployment identity;
18. for the current scope, expose at most one effective AddressSpace per Resource at a logical time;
19. represent that AddressSpace as either one `HostAddress` or one `Prefix`;
20. allow an address/prefix change without changing Resource identity.

## Concrete access endpoint semantics

For access governance and policy export, the source and destination are concrete Component Deployments rather than whole-Application deployment plus later placement expansion.

```text
ACC Component
    -> Component Deployment
        -> exactly one ResourceRef
            -> RC effective AddressSpace [0..1]
                = HostAddress | Prefix
```

Deploying the same Component on a second Resource produces a second independently selectable Component Deployment:

```text
Component A + Resource R1 -> ComponentDeployment 1
Component A + Resource R2 -> ComponentDeployment 2
```

The first MVP does not infer that these two deployments share access policy merely because they reference the same Component.

A Resource with no resolved current AddressSpace makes downstream technical materialization unresolved. A Prefix remains a Prefix and need not be expanded to individual hosts.

## Interaction revision behavior

An Interaction is the reusable directed communication definition between two Components of one Application. Its immutable revision fixes the exact traffic semantics for a decision or policy at a point in the lifecycle.

Changing traffic such as TCP destination port `443 -> 8443` creates a new Interaction Contract Revision. Existing consumers of the older revision continue to refer to that older immutable revision until an accepted change explicitly moves them to the newer revision.

A revision reference therefore identifies both the exact traffic contract and, through its owning Interaction, the corresponding source and destination Component definitions. Consumers need not carry a duplicate Interaction reference solely to recover that meaning.

## Explicit current limitations

The first MVP intentionally does not yet define:

- several simultaneous addresses/prefixes on one Resource;
- multiple interfaces or endpoint purpose;
- VIPs or deployment-specific network exposure;
- provider/container/pod identities;
- whether several different Component Deployments may share one Resource simultaneously, because the selected policy/export behavior does not require that choice yet.

These are not inferred from storage or implementation convenience.

## Acceptance invariants

A conforming target behavior must prove at least:

- an Interaction never crosses Application boundaries;
- changing traffic creates a new immutable Interaction Contract Revision without replacing the Interaction;
- one Component Deployment identifies one Component deployed on one Resource;
- deploying the same Component on another Resource produces another Component Deployment;
- two Component Deployments of the same Component may participate in different access relationships;
- changing a Resource address/prefix leaves Resource identity unchanged;
- a consumer can resolve endpoint Components and traffic semantics from the exact revision reference plus concrete source/destination Component Deployment references;
- missing Resource AddressSpace remains unresolved rather than becoming empty access;
- no consumer persistence contract is required to use SQL foreign keys across semantic owners.

## Domain alignment

S2 subsequently accepted:

- **Application Communication Catalogue** as owner of Application/Component/Interaction/immutable revision meaning;
- **Application Deployment** as owner of target `ComponentDeploymentId + ComponentRef + ResourceRef` identity/lifecycle;
- **Resource Catalogue** as owner of Resource/AddressSpace/scope truth.

See `docs/domain/application-deployment/tactical-model.md`, `docs/domain/application-communication-catalogue/target-tactical-model.md` and `docs/domain/resource-catalogue/tactical-model.md`.

## Relationship to current as-built behavior

`application-catalogue-target.md`, ADR-012, ADR-013 and the implemented ACC compatibility model remain current **as-built reconstruction truth**. They may use `ApplicationDeployment`, `DeploymentInteraction` and ACC-owned compatibility `ComponentDeployment` concepts that do not define this target product behavior.

The target `ComponentDeployment` belongs to Application Deployment and means one concrete Component-on-Resource instance. It must not be inferred from or conflated with the implemented ACC compatibility identity merely because the same term appears in both models.
