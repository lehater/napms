# ADR-015 — ACC Component Deployment and Atomic Interaction Contract

Status: `accepted; amended 2026-09-14; implementation pending`.

Date: 2026-09-12.
Amended: 2026-09-14 after G1 revalidation fixed `ComponentDeployment -> exactly one Resource` for MVP.

## Context

The implemented I31 Application Communication Catalogue authoring model treats `ApplicationDeployment` as the deployment unit and scopes Resource bindings to selected interaction sides. Domain review established the target meanings:

- Application is a reusable definition/grouping;
- Component is the deployable application role;
- `ComponentDeployment` is one concrete deployment of one Component on one Resource;
- communication is defined between Components;
- one interaction contract revision is the complete atomic traffic contract consumed by authorization;
- Resource Endpoint/address realization is not part of Access Policy semantic identity;
- bounded contexts exchange opaque stable semantic references rather than cross-schema navigation.

This ADR supersedes ADR-012 and ADR-013 as target ACC domain design. Those ADRs remain historical records of the implemented I31 model until migration is completed.

The original 2026-09-12 version allowed zero/many temporal Resource bindings per ComponentDeployment. Stakeholder G1 revalidation on 2026-09-14 rejected that target interpretation for MVP: a concrete ComponentDeployment must belong to exactly one Resource, Resource association is mandatory at creation, and moving the Component to another Resource creates a different ComponentDeployment/authorization subject.

## Decision

### 1. Component is the deployment unit

```text
ApplicationDefinition
  -> Component
      -> ComponentDeployment
```

A `ComponentDeployment` means one concrete deployment/instance of a Component that participates in governed communication.

It has a stable ACC-owned identity and immutable parent Component for its lifetime.

### 2. Each ComponentDeployment belongs to exactly one Resource in MVP

Target relation:

```text
ComponentDeployment
    -> exactly one ResourceRef
```

`ResourceRef` is an opaque stable Resource Catalogue identifier. Resource identity/facts remain owned by Resource Catalogue.

Required semantics:

- ResourceRef is mandatory when ComponentDeployment is created;
- ResourceRef remains stable for that ComponentDeployment lifetime;
- moving the Component to another Resource is represented by a different ComponentDeployment, not by silently rebinding the existing one;
- Resource Endpoint additions/removals and address changes on the same Resource do not create a different ComponentDeployment;
- Resource/Endpoint/address facts are not members of the published interaction identity beyond the opaque ComponentDeployment reference.

Replica/cluster deployment across several Resources is represented by several concrete ComponentDeployments when each Resource is a distinct deployed authorization participant. The target does not use one multi-Resource ComponentDeployment to collapse those concrete subjects.

### 3. Endpoint-specific deployment binding remains unresolved

This ADR does not decide whether a ComponentDeployment additionally binds to a specific `ResourceEndpoint` or network exposure.

Open later questions include network-context-dependent visibility, NAT and a Component listening only on a subset of Resource endpoints.

No implementation may infer endpoint identity from this ADR.

### 4. Interaction Definition is between Components

An `InteractionDefinition` identifies a directed relation:

```text
source Component -> destination Component
```

The decision-relevant communication contract is an immutable `InteractionContractRevision` with one or more vendor-neutral `TrafficAlternative` values.

Changing decision-relevant traffic creates another immutable revision; existing references are never rewritten.

### 5. One interaction contract revision is atomic

All `TrafficAlternative` entries in one revision form one minimum sufficient communication contract.

Consumers authorize/select the revision as a whole. Independently governed traffic subsets require separate Interaction Definitions rather than selectable fragments of one revision.

### 6. ACC publishes one semantic subject value

For concrete deployed communication ACC validates and publishes:

```text
DirectedInteractionIdentity =
    sourceComponentDeploymentRef
  + destinationComponentDeploymentRef
  + interactionContractRevisionRef
```

Validation requires:

```text
sourceDeployment.component == interaction.sourceComponent
destinationDeployment.component == interaction.destinationComponent
revision belongs to interaction
```

This is a semantic value contract, not a required aggregate/table.

### 7. Cross-context references are opaque IDs

Consumers may persist ACC references in their own stores but must treat them as opaque IDs. There is no domain requirement for SQL foreign keys into ACC-owned tables or shared-schema navigation.

Cross-context validity is established through ACC-owned contracts/adapters.

### 8. Traffic/address realization is not copied into authorization identity

Protocol/port alternatives remain ACC-owned revision facts. Resource Endpoint/address realization is resolved separately through Resource Catalogue and downstream materialization.

## Target domain shape

```text
ApplicationDefinition
  |
  +-- Component
  |     |
  |     +-- ComponentDeployment --> exactly one ResourceRef
  |
  +-- InteractionDefinition
          |
          +-- source Component
          +-- destination Component
          +-- InteractionContractRevision
                  |
                  +-- TrafficAlternative [1..N]

DirectedInteractionIdentity
  = source ComponentDeployment
  + destination ComponentDeployment
  + immutable InteractionContractRevision
```

## Required invariants

1. `ComponentDeployment.componentId` is immutable.
2. Each ComponentDeployment has exactly one ResourceRef in MVP.
3. `ComponentDeployment.resourceRef` is immutable for that deployment lifetime.
4. Moving a Component to another Resource creates another ComponentDeployment.
5. Endpoint/address changes on the same Resource do not change ComponentDeployment identity.
6. Resource/Endpoint/address facts are not part of `DirectedInteractionIdentity` except indirectly through the stable deployment identity.
7. InteractionDefinition is directed from one Component to another.
8. InteractionContractRevision is immutable and contains at least one TrafficAlternative.
9. A contract revision is consumed atomically; traffic subset selection is forbidden.
10. source/destination deployments must belong to the Components declared by the Interaction Definition.
11. published subject is exactly `(sourceDeploymentRef, destinationDeploymentRef, interactionContractRevisionRef)`.
12. cross-context persistence uses opaque stable IDs and no required cross-schema SQL foreign keys.

## Explicitly deferred

- ComponentDeployment-to-ResourceEndpoint binding;
- network-context/NAT endpoint semantics;
- migration from current I31 ApplicationDeployment/DeploymentInteraction and any previous multi-binding representation;
- final UI migration;
- persistence/repository realization details.

## Consequences

- authorization subject corresponds to concrete deployed participants rather than an abstract multi-Resource grouping;
- Resource movement cannot silently transfer existing authorization;
- address/Endpoint changes on the same Resource remain technical realization changes;
- interaction traffic keeps one unambiguous atomic authorization granularity;
- consumers depend on a stable ACC semantic contract rather than ACC persistence structure;
- current I31 runtime remains migration evidence until explicitly conformed to this target.
