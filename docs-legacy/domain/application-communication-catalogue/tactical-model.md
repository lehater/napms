# Application Communication Catalogue Tactical Model

Status: `accepted and implemented through I31`.

Date: 2026-09-10.

## Purpose

Define the current Application Communication Catalogue write/read semantics selected by ADR-012 and ADR-013. This model supersedes the I27 Application-side tactical structure for current authoring while preserving legacy Component Deployment/DCS/binding truth and unchanged downstream semantic identities.

## Current structure

```text
Application Definition
  -> Components
  -> Interaction Definitions

Application Deployment
  -> Application Definition
  -> deployment context
  -> Deployment Interactions

Deployment Interaction
  -> Interaction Definition
  -> source Resource bindings
  -> destination Resource bindings
  -> internal current compatibility projection
```

## Identities and fields

### Application Definition

The existing stable ACC `applicationId` remains the Application Definition identity.

```text
ApplicationDefinition
    applicationId: UUID
    displayName: non-empty string
    description: optional descriptive text
    domain: optional classification label
    ownerReference: optional external correlation reference
    lifecycle: Active | Retired
    provenanceReference
    technical concurrency token
```

Description, domain and owner reference do not participate in identity. Owner reference does not grant authority.

### Component

The existing stable ACC `componentId` remains the Component identity and belongs to exactly one Application Definition.

```text
Component
    componentId: UUID
    applicationId: UUID
    displayName: non-empty string
    type: optional classification label
    description: optional descriptive text
    lifecycle: Active | Retired
    provenanceReference
    technical concurrency token
```

Component type is descriptive and open-ended in I31; no domain behavior branches on the text value.

### Interaction Definition

```text
InteractionDefinition
    interactionDefinitionId: UUID
    applicationId: UUID
    sourceComponentId: UUID
    destinationComponentId: UUID
    trafficAlternatives: 1+
    lifecycle: Active | Retired
    provenanceReference
    technical concurrency token
```

Source and destination Components must belong to the same Application Definition as the Interaction Definition.

Traffic uses the existing vendor-neutral DCS traffic value semantics for protocols and port constraints.

Interaction Definition is current reusable communication intent. It is not itself the immutable downstream DCS revision identity.

### Application Deployment

```text
ApplicationDeployment
    applicationDeploymentId: UUID
    applicationId: UUID
    companyReference: non-empty external correlation reference
    environment: non-empty deployment-context label
    scopeReference: non-empty external Responsibility Scope reference
    lifecycle: Active | Retired
    provenanceReference
    technical concurrency token
```

Application Deployment belongs to exactly one Application Definition. Company/Environment/Scope are mutable context metadata, not identity components and not authority scope.

A new Application Deployment may contain zero Deployment Interactions.

### Deployment Interaction

```text
DeploymentInteraction
    deploymentInteractionId: UUID
    applicationDeploymentId: UUID
    interactionDefinitionId: UUID
    lifecycle: Active | Retired
    provenanceReference
    technical concurrency token
```

For one Application Deployment, the same Active Interaction Definition may be selected at most once.

A Deployment Interaction inherits source Component, destination Component and traffic from its active Interaction Definition. Deployment-specific traffic or endpoint overrides do not exist in I31.

### Deployment Interaction Resource Binding

A Resource binding belongs to exactly one Deployment Interaction side.

```text
DeploymentInteractionResourceBinding
    bindingReference: stable string
    deploymentInteractionId: UUID
    side: Source | Destination
    resourceReference: Resource Catalogue reference
    validity: [validFrom, validTo)
    provenanceReference
    technical concurrency token
```

The same Resource may be bound to both sides only when each side independently selects it; the side relation is explicit.

Within one Deployment Interaction side, duplicate simultaneously effective bindings for the same Resource are invalid.

## Compatibility identity

The current model preserves the existing downstream semantic boundary through an ACC-owned compatibility projection.

For each Active Deployment Interaction:

```text
CompatibilityProjection
    deploymentInteractionId
    sourceCompatibilityComponentDeploymentId
    destinationCompatibilityComponentDeploymentId
    currentDcsRevisionId
```

The source/destination compatibility Component Deployment identities are unique per Deployment Interaction side and stable for that Deployment Interaction lifetime.

The current immutable DCS revision references those two compatibility identities and carries the current Interaction Definition traffic snapshot.

Target Resource bindings project to the corresponding compatibility Component Deployment. Existing downstream resolvers therefore continue to obtain Resource sets and DCS payload through the existing `DirectedInteractionIdentity` triple.

Compatibility IDs are not user-facing authoring identities.

## Creation invariants

### Create Interaction Definition

Required:

1. parent Application Definition exists and is Active;
2. source and destination Components exist, are Active and belong to that same Definition;
3. at least one valid traffic alternative is supplied;
4. traffic semantics satisfy the existing DCS traffic constraints.

No compatibility projection is created until the Interaction Definition is selected by an Application Deployment.

### Create Application Deployment

Required:

1. referenced Application Definition exists and is Active;
2. Company, Environment and Scope context values are present and valid bounded values;
3. no Company/Scope existence or authority is inferred from the text values.

### Select Deployment Interaction

Required:

1. Application Deployment exists and is Active;
2. Interaction Definition exists, is Active and belongs to the same Application Definition;
3. the Interaction Definition is not already selected as another Active Deployment Interaction in that Application Deployment.

Creation establishes the Deployment Interaction and its compatibility source/destination Component Deployment identities plus initial immutable DCS revision in one semantic operation.

### Bind Resource

Required:

1. Deployment Interaction is Active;
2. selected side is Source or Destination;
3. referenced Resource exists and is admitted by the Resource Catalogue consuming contract;
4. temporal interval is valid;
5. no duplicate effective binding exists for the same Deployment Interaction side and Resource.

## Edit semantics

### Descriptive/context fields

Display names, descriptions, classifications, owner correlation reference and Application Deployment context may be corrected in place with provenance and optimistic concurrency. These values do not change stable identity or downstream compatibility identity.

### Interaction endpoints

Source/destination Component change is allowed only when the Interaction Definition has no Active Deployment Interaction selection.

If Active selections exist, endpoint change is rejected as a dependency conflict. Replacement is represented by another Interaction Definition and explicit replacement of selections.

### Interaction traffic

Traffic edit is a semantic operation over the Interaction Definition and all of its Active Deployment Interactions.

Before update, ACC asks downstream dependency ports whether any affected current compatibility triple has an active/effective Connectivity Requirement, effective/final Connectivity Decision or active/effective Access Rule.

If any such dependency exists, the edit is blocked and returns grouped dependencies.

Otherwise the operation:

1. validates the new traffic alternatives;
2. updates the Interaction Definition current traffic;
3. creates one new immutable DCS revision per Active Deployment Interaction using its existing compatibility side IDs;
4. advances each affected Deployment Interaction current projection to that new revision;
5. preserves every previous DCS revision and historical downstream reference.

The operation must not leave some Active Deployment Interactions on old current traffic while others use the new Definition traffic.

## Lifecycle and dependency invariants

Lifecycle is terminal:

```text
Active -> Retired
```

No normal hard delete exists.

Retirement does not cascade. The user clears active dependants first.

### Application Definition retirement blockers

- Active Components;
- Active Interaction Definitions;
- Active Application Deployments.

### Component retirement blockers

- Active Interaction Definitions using the Component as source or destination;
- Active legacy I27 Component Deployments belonging to the Component during coexistence.

### Interaction Definition retirement blockers

- Active Deployment Interactions selecting it.

### Application Deployment retirement blockers

- Active Deployment Interactions.

### Deployment Interaction retirement blockers

- effective source Resource bindings;
- effective destination Resource bindings;
- owner-reported active/effective Connectivity Requirements for the current compatibility triple;
- owner-reported effective/final Connectivity Decisions for the current compatibility triple;
- owner-reported active/effective Access Rules for the current compatibility triple.

After blockers are cleared, retiring a Deployment Interaction retires its compatibility Component Deployment identities from new authoring/discovery while preserving historical DCS/binding/downstream references.

## Dependency projection

Blocked retirement and blocked traffic edit return grouped dependency counts owned by the application/read model. Supported semantic groups are:

```text
Components
Interactions
ApplicationDeployments
DeploymentInteractions
ResourceBindings
ConnectivityRequirements
ConnectivityDecisions
AccessRules
LegacyComponentDeployments
```

Counts are server-derived and each non-zero group has a bounded drill-down query. The Web client does not infer dependency counts from loaded children.

## Read-model responsibility

Current reads are bounded projections rather than one whole Application tree.

Required projections support:

- paged/searchable/filterable Application Definitions with Component/Interaction/Deployment counts;
- Definition overview;
- separately paged Components;
- separately paged Interaction Definitions with active Deployment-selection counts;
- separately paged Definition-local Application Deployments;
- paged global Application Deployments;
- Deployment detail and paged Deployment Interaction connectivity rows;
- paged Resource set for one Deployment Interaction side;
- grouped dependency summaries and bounded dependency drill-downs.

Potentially unbounded lists use server-side stable sort and paging.

## Legacy coexistence

Existing I27 Application and Component IDs remain valid and may be presented as current Definitions/Components.

Existing pre-I31 Component Deployments, DCS revisions and Deployment Resource Bindings are not automatically transformed into Application Deployments or Interaction Definitions because required business context cannot be inferred safely.

They remain legacy ACC truth for existing downstream references. Active legacy Component Deployments are an explicit retirement dependency until retired through the retained compatibility/maintenance path or a future explicit migration workflow.

## Authority and external references

Catalogue mutation authority remains the existing ACC curation authority contract. Company, owner and Responsibility Scope correlation values do not grant or select mutation authority.

Future Company/Party/Scope discovery integrations remain optional adapters. They may improve selection/validation without moving ACC entity ownership or changing identity.

## Consequences

- the current user mental model is represented directly in ACC;
- existing downstream semantic identity remains unchanged through an internal compatibility projection;
- interaction-scoped Resource sets do not leak into global Component identity;
- traffic history remains immutable and active downstream semantics cannot silently become stale;
- missing enterprise registries do not block the local-first product;
- retirement blockers are explicit and explainable;
- pre-I31 Component Deployment/DCS/binding truth remains available for historical and compatibility consumers without becoming the current authoring model.
