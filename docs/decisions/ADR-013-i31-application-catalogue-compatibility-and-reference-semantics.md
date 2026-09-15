# ADR-013 — Application Catalogue Compatibility and Reference Semantics

Status: `current as-built compatibility decision`.

## Role

This ADR defines compatibility semantics required to reproduce the current implemented Application Catalogue and its downstream contracts. It is retained because these identities, projections and dependency rules are still part of the as-built design.

It does not define current target ACC/AD ownership. Target semantics are owned by the Strategic model, ACC target model and Application Deployment model.

## Context

The implemented catalogue authoring model is:

```text
Application Definition
  -> Components
  -> Interaction Definitions

Application Deployment
  -> selected Deployment Interactions
      -> interaction-scoped Source/Destination Resource bindings
```

Existing downstream implemented flows consume the stable compatibility subject:

```text
sourceComponentDeploymentId
+ destinationComponentDeploymentId
+ dcsContractRevisionId
```

Current Connectivity Requirement, Connectivity Decision, Access Rule and export records that reference these identities must remain explainable and must not be rewritten merely because the catalogue authoring model changes.

## Decision

### 1. Preserve the downstream semantic triple through an ACC compatibility projection

For each Active Deployment Interaction, ACC owns an internal compatibility projection:

```text
DeploymentInteraction
  -> source compatibility ComponentDeployment
  -> destination compatibility ComponentDeployment
  -> current immutable DcsRevision
  -> DirectedInteractionIdentity
```

The two compatibility Component Deployment identities are server-owned, unique per Deployment Interaction side and stable for that Deployment Interaction lifetime. They are not shared merely because two interactions use the same Component.

Compatibility Component Deployment IDs are implementation identities. Current Web/API authoring does not require users to understand or assemble them.

### 2. Interaction-scoped Resource bindings project through compatibility sides

A source-side Resource binding is realized through the source compatibility Component Deployment for that Deployment Interaction. A destination-side binding is realized through the destination compatibility Component Deployment.

Temporal `DeploymentResourceBinding` facts therefore remain usable by current downstream Resource resolution while the stronger application meaning remains that the binding belongs to one Deployment Interaction side.

Ending/replacing a side binding ends/replaces the corresponding temporal compatibility binding without erasing historical binding facts.

### 3. Interaction Definition endpoint edits are constrained

An Interaction Definition owns stable source and destination Component references.

Changing either endpoint in place is allowed only while the Interaction Definition has no Active Deployment Interaction selections. Once selected, endpoint replacement would change the meaning of existing compatibility side identities and is therefore blocked.

Replacement is represented by creating another Interaction Definition and explicitly changing selections after active dependencies are cleared. Existing retired/reference-bearing compatibility facts remain intact.

### 4. Traffic edits create immutable downstream snapshots

Interaction Definition traffic is editable current definition data, but an existing DCS revision is immutable.

For every Active Deployment Interaction selecting an edited Interaction Definition, ACC creates a new immutable DCS revision over the same compatibility source/destination identities and advances that Deployment Interaction's current compatibility projection to the new revision.

Old DCS revisions remain addressable by existing downstream subjects.

A traffic edit is blocked if any affected current compatibility triple has an owner-reported active/effective downstream reference that would otherwise become stale. Current blocker classes are:

```text
active/effective Connectivity Requirement
effective/final Connectivity Decision
active/effective Access Rule
```

Each owning module defines its own effective/current meaning. ACC consumes those results through application ports rather than reimplementing peer lifecycle semantics.

When no blocking current references exist, the traffic edit updates all affected Active Deployment Interactions as one semantic operation.

### 5. Catalogue metadata is descriptive/correlation data

Application Definition may carry optional description, domain classification and owner correlation reference. Component may carry optional type/classification and description.

Application Deployment carries:

```text
companyReference
environment
scopeReference
```

Company/owner/scope references are correlation data. They do not create Organization/Person/Team/Responsibility Scope aggregates and do not grant catalogue or policy authority.

Environment is descriptive deployment context. Company, Environment and Scope do not form Application Deployment identity and may be corrected without changing `applicationDeploymentId`.

Discovery adapters may improve value selection without changing these identity semantics.

### 6. Lifecycle uses active-reference blockers rather than hard deletion

The implemented lifecycle remains:

```text
Active -> Retired
```

Normal hard delete is absent. Retirement is blocked by active dependants/references while historical references remain preserved.

Current blocker groups include, where applicable:

```text
Components
Interactions
ApplicationDeployments
DeploymentInteractions
ResourceBindings
ConnectivityRequirements
ConnectivityDecisions
AccessRules
CompatibilityComponentDeployments
```

Deployment Interaction retirement requires effective side bindings and blocking current downstream references to be cleared first. Its compatibility identities may then leave normal authoring/discovery while referenced DCS/binding/business history remains valid.

### 7. Blocked operations expose structured dependencies

Dependency-blocked retirement and traffic edits expose grouped dependency kinds and exact counts with bounded server-side drill-downs. Clients do not infer dependency state from already loaded UI trees.

### 8. Compatibility facts are not fabricated into newer authoring identities

Existing compatibility Component Deployments, DCS revisions and Deployment Resource Bindings are not automatically promoted into Application Deployments/Interaction Definitions when required business context cannot be inferred safely.

Existing Application and Component identities may be reused where their identity meaning remains compatible. Compatibility participants stay available to downstream reads and dependency explanation while current authoring uses Application Definition / Application Deployment / Deployment Interaction.

No display name or technical value is used to invent Company, Environment, Scope, Deployment or Interaction identity.

## Current target relationship

The current target domain model is different from this as-built compatibility model:

- ACC target owns Application, Component, Interaction and immutable `InteractionContractRevision`;
- target Application Deployment is a separate Bounded Context owning logical deployment identity and current Component-to-Resource placement set;
- the target governed subject uses `InteractionContractRevisionRef + sourceApplicationDeploymentRef + destinationApplicationDeploymentRef`;
- compatibility `ComponentDeployment`, `DeploymentResourceBinding`, `DirectedInteractionIdentity` and `DeploymentInteraction` do not become target domain ownership merely because current runtime uses them.

This ADR remains authoritative only for reproducing and safely evolving the current compatibility path until that path is explicitly migrated.

## Consequences

- existing downstream subjects and records remain stable;
- interaction-scoped Resource sets work through distinct compatibility sides;
- traffic edits preserve immutable DCS history and fail safely when current downstream truth would become stale;
- endpoint replacement cannot silently change compatibility identity meaning;
- metadata is implemented without inventing new organization/party authority semantics;
- retirement remains explainable and preserves referenced history;
- the current product can be reconstructed without confusing compatibility implementation with target domain ownership.
