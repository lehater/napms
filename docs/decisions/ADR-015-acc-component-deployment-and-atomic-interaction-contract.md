# ADR-015 — ACC Component Deployment and Atomic Interaction Contract

Status: `accepted; implementation pending`.

Date: 2026-09-12.

## Context

The implemented I31 Application Communication Catalogue authoring model treats `ApplicationDeployment` as the deployment unit and scopes Resource bindings to selected `DeploymentInteraction` sides. Further domain review established a different business meaning:

- an Application is a reusable definition/grouping;
- a Component is the deployable application role;
- a concrete deployment is therefore a `ComponentDeployment`;
- communication is defined between Components;
- the traffic declared for one interaction contract is the complete minimum sufficient set for that interaction and is consumed atomically;
- technical Resource realization must not become part of Access Policy semantic identity.

The target must also preserve bounded-context independence. Access Policy must not navigate ACC tables or depend on ACC persistence schema merely because its Rule subject contains ACC-owned identities.

This ADR supersedes ADR-012 and ADR-013 as target ACC domain design. Those ADRs remain historical records of the implemented I31 model until migration is completed.

## Decision

### 1. Component is the deployment unit

The target ACC structure is:

```text
ApplicationDefinition
  -> Component
      -> ComponentDeployment
```

`ComponentDeployment` means one concrete deployment/instance/grouping of a Component that can participate in governed communication.

An Application as a whole is not the deployment unit in the target model. `ApplicationDeployment` and `DeploymentInteraction` are not target domain concepts.

A `ComponentDeployment` has a stable ACC-owned identity and an immutable parent `Component` for its lifetime.

### 2. Resource realization is separate from Component Deployment identity

A Component Deployment is related to Resource Catalogue through a separate temporal relation:

```text
ComponentDeployment
  -> DeploymentResourceBinding [0..N]
      -> ResourceRef
```

`ResourceRef` is an opaque stable Resource Catalogue identifier. Resource identity and Resource facts remain owned by Resource Catalogue.

The relation is not part of Component Deployment identity and not part of interaction/policy semantic identity. Changing, ending or adding Resource bindings does not by itself create a new Component Deployment or a new interaction subject.

The target permits more than one effective Resource binding for one Component Deployment; this supports replicas, clusters and other multi-resource realizations without changing the deployment identity model.

### 3. Endpoint-specific deployment binding is intentionally unresolved

This ADR does **not** decide whether a Component Deployment may additionally bind to a specific `ResourceEndpoint` or network exposure.

The base fact is only:

```text
ComponentDeployment -> Resource
```

The following remain a separate domain question:

- a Resource having multiple addresses/interfaces;
- different addresses being reachable from different network contexts;
- NAT or other translated exposure;
- a Component listening only on a subset of Resource endpoints.

No implementation may infer `ComponentDeployment -> ResourceEndpoint` identity or ownership from this ADR.

### 4. Interaction Definition is between Components

An `InteractionDefinition` belongs to one Application Definition and identifies a directed relation:

```text
source Component -> destination Component
```

Both endpoints are ACC-owned Component identities.

The concrete communication contract is represented by an immutable `InteractionContractRevision` belonging to the Interaction Definition.

```text
InteractionDefinition
  -> InteractionContractRevision [1..N over history]
      -> TrafficAlternative [1..N]
```

Each revision is immutable and has a stable ACC-owned identifier.

Changing decision-relevant traffic creates another immutable revision. Existing references to an older revision are never rewritten.

### 5. One interaction contract revision is atomic

All `TrafficAlternative` entries belonging to one `InteractionContractRevision` form one minimum sufficient communication contract.

A consumer selects/authorizes the revision **as a whole**. Partial selection of its traffic alternatives is not valid domain behavior.

If two traffic subsets need independent lifecycle, approval, authorization or applicability, they are modeled as separate `InteractionDefinition`s rather than as selectable subsets of one contract.

This is a normative invariant, not a UI convention.

### 6. ACC publishes one semantic subject value

For a concrete interaction between deployed Components, ACC validates and publishes a `DirectedInteractionIdentity` value:

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

The published value is not a new aggregate or required persistence table. It is a value/contract composed of three stable ACC-owned identifiers.

### 7. Bounded-context references are opaque IDs, not cross-schema foreign keys

A consuming bounded context may persist the three values of `DirectedInteractionIdentity` in its own storage, for example as three UUID columns, but must treat them as opaque ACC references.

There is no SQL foreign key from a consumer-owned table to ACC-owned tables and no requirement that bounded contexts share one database schema.

Cross-context validity is established through ACC-owned application/API contracts, not by direct navigation of foreign tables.

This ADR defines only the ACC-published boundary. It does not redesign Access Policy, Connectivity Requirements, Connectivity Decision or Resource Catalogue internals.

### 8. Traffic is not copied into Access Policy identity

Protocol/port alternatives remain ACC-owned interaction-contract facts. The published semantic subject references the immutable contract revision instead of copying a selectable traffic subset into the consumer identity.

Technical Resource/Endpoint/address realization is resolved separately and must not redefine this semantic subject.

## Target domain shape

```text
ApplicationDefinition
  |
  +-- Component
  |     |
  |     +-- ComponentDeployment
  |             |
  |             +-- DeploymentResourceBinding --> ResourceRef
  |
  +-- InteractionDefinition
          |
          +-- source Component
          +-- destination Component
          +-- InteractionContractRevision
                  |
                  +-- TrafficAlternative [1..N]

ACC published contract:

DirectedInteractionIdentity
  = source ComponentDeployment
  + destination ComponentDeployment
  + immutable InteractionContractRevision
```

## Required invariants

1. `ComponentDeployment.componentId` is immutable.
2. Resource binding changes do not change `ComponentDeploymentId`.
3. Resource/Endpoint/address facts are not part of `DirectedInteractionIdentity`.
4. An `InteractionDefinition` is directed from one Component to another.
5. An `InteractionContractRevision` is immutable.
6. A contract revision contains at least one traffic alternative.
7. A contract revision is consumed atomically; traffic subset selection is forbidden.
8. Source/destination deployments must belong to the Components declared by the Interaction Definition.
9. The published subject is exactly `(sourceDeploymentRef, destinationDeploymentRef, interactionContractRevisionRef)`.
10. Cross-bounded-context persistence uses opaque stable IDs and no cross-schema SQL foreign keys.

## Explicitly deferred

- binding Component Deployment to a specific Resource Endpoint/network exposure;
- Resource Catalogue endpoint/address model changes;
- Access Policy aggregate/table redesign beyond consuming the published ACC subject;
- migration mechanics from implemented I31 `ApplicationDeployment` / `DeploymentInteraction` rows;
- final UI migration from current I31 screens;
- exact aggregate boundaries and repository layout inside ACC Tactical DDD.

## Consequences

- the domain language matches the operational fact that Components, not whole Applications, are deployed;
- interaction traffic has one unambiguous authorization granularity;
- Resource movement/replication remains technical realization rather than policy identity;
- peer bounded contexts depend on one stable ACC semantic contract instead of ACC persistence structure;
- the current I31 implementation is no longer the target and requires an explicit migration before code can be considered conformant.
