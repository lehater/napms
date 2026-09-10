# ADR-013 — I31 Application Catalogue Compatibility and Reference Semantics

Status: `accepted`.

Date: 2026-09-10.

## Context

ADR-012 changes the Application Communication Catalogue product model from Component Deployment-centric authoring to:

```text
Application Definition
  -> Components
  -> Interaction Definitions

Application Deployment
  -> selected Deployment Interactions
      -> interaction-scoped source/destination Resource bindings
```

Existing downstream NAPMS contexts already consume the stable semantic triple:

```text
sourceComponentDeploymentId
destinationComponentDeploymentId
dcsContractRevisionId
```

Historical Connectivity Requirements, Connectivity Decisions, Access Rules and policy/export facts must not be rewritten. The accepted target also introduces Application/Component metadata and Deployment Company/Environment/Scope fields without introducing a Company/Organization or directory bounded context.

This ADR closes the blocking I31 M0 choices required before implementation.

## Decision

### 1. Preserve the existing downstream semantic triple as an ACC compatibility contract

`DeploymentInteraction` is the target user-facing selected interaction identity. For each Active Deployment Interaction, ACC owns an internal compatibility projection:

```text
DeploymentInteraction
  -> source compatibility ComponentDeployment
  -> destination compatibility ComponentDeployment
  -> current immutable DcsRevision
  -> DirectedInteractionIdentity
```

The two compatibility Component Deployment identities are server-owned and stable for the lifetime of that Deployment Interaction. They are unique per Deployment Interaction side; they are not shared merely because two interactions use the same Component.

This uniqueness is required because ADR-012 allows the same Component to bind to different Resource sets in different Deployment Interactions.

Compatibility Component Deployment IDs are implementation identities. New target Web/API authoring does not expose them as concepts the user must understand or assemble.

### 2. Interaction-scoped Resource bindings project through compatibility sides

A target source-side Resource binding is realized through the source compatibility Component Deployment for that Deployment Interaction. A destination-side binding is realized through its destination compatibility Component Deployment.

Existing temporal `DeploymentResourceBinding` facts therefore remain usable by the current ACC resolver without changing downstream contracts. Target application/domain code owns the stronger meaning that each binding belongs to one Deployment Interaction side.

Ending or replacing a target side binding ends/replaces the corresponding temporal compatibility binding; historical binding facts remain preserved.

### 3. Interaction Definition endpoint edits are structurally constrained

An Interaction Definition owns stable source and destination Component references.

Changing either endpoint in place is allowed only while the Interaction Definition has no Active Deployment Interaction selections. Once selected by an Active Application Deployment, endpoint replacement would change the meaning of existing compatibility side identities and is therefore blocked.

When endpoint change is blocked, the normal workflow is:

1. create another Interaction Definition with the desired endpoints;
2. remove/retire affected Deployment Interactions after their active dependencies are cleared;
3. select the replacement Interaction Definition where required;
4. retire the old Interaction Definition when no Active selections remain.

Historical retired Deployment Interactions continue to explain their last compatibility snapshot and are not rewritten by later Definition changes.

### 4. Traffic edits create immutable downstream snapshots

Interaction Definition traffic remains editable current definition data. A traffic edit never mutates an existing DCS revision.

For every Active Deployment Interaction selecting the edited Interaction Definition, ACC creates a new immutable DCS revision over the same compatibility source/destination identities and atomically advances that Deployment Interaction's current compatibility projection to the new revision.

Old DCS revisions remain addressable by historical downstream subjects.

A traffic edit is blocked if any affected current compatibility triple has an owner-reported active/effective downstream business reference. This prevents a currently effective Requirement, Decision or Access Rule from silently remaining authoritative for traffic that the current Deployment Interaction no longer declares.

The blocking reference classes are:

```text
Active/effective Connectivity Requirement
Effective/final Connectivity Decision
Active/effective Access Rule
```

Each owning context defines whether its reference is active/effective. ACC consumes those decisions through application-owned ports/adapters and does not redefine peer lifecycle semantics.

When no such active/effective downstream references exist, traffic edit may update all Active Deployment Interactions in one semantic operation. Historical references do not block the edit.

### 5. Target metadata is catalogue descriptive/correlation data, not new identity ownership

The target fields required by the accepted wireframes have these semantics.

#### Application Definition

```text
description: optional descriptive text
domain: optional classification label
ownerReference: optional external responsible-party/team correlation reference
```

`description` and `domain` are ACC-owned descriptive metadata. They do not define Application identity or authority.

`ownerReference` is an external correlation value. NAPMS does not create a Person/Team/Organization identity from it and does not derive catalogue or policy authority from it.

#### Component

```text
type: optional classification label
description: optional descriptive text
```

Component `type` is deliberately not a closed enum in I31. Values such as `Frontend`, `Service` and `Database` are useful classifications, not domain behavior switches. A fixed vocabulary may be introduced later only if an accepted requirement gives it semantic meaning.

Neither Component `type` nor `description` participates in Component identity.

#### Application Deployment

```text
companyReference: required external correlation reference
environment: required bounded label
scopeReference: required external Responsibility Scope correlation reference
```

I31 does not introduce Company/Organization or Responsibility Scope registry ownership. `companyReference` and `scopeReference` are external correlation values. `scopeReference` uses the same externally-owned Responsibility Scope concept already admitted by ADR-011.

`environment` is ACC-owned deployment-context metadata such as `Production` or `Test`; I31 does not define a closed environment taxonomy.

Company, Environment and Scope do not form Application Deployment identity, do not grant authority and may be corrected through an audited/concurrency-safe mutation without changing `applicationDeploymentId`.

Future registry/discovery adapters may replace explicit local-first text entry with selection without changing ACC identity or mutation semantics.

### 6. Lifecycle uses active-reference blockers, not hard deletion

The target lifecycle remains terminal:

```text
Active -> Retired
```

Normal hard delete remains absent.

Retirement is blocked by active dependants/references. Historical references do not block retirement.

Required blocker sets are:

```text
Application Definition
  -> Active Components
  -> Active Interaction Definitions
  -> Active Application Deployments

Component
  -> Active Interaction Definitions using it
  -> Active legacy I27 Component Deployments, while legacy coexistence remains

Interaction Definition
  -> Active Deployment Interactions selecting it

Application Deployment
  -> Active Deployment Interactions

Deployment Interaction
  -> effective source/destination Resource bindings
  -> active/effective Connectivity Requirements for its current compatibility triple
  -> effective/final Connectivity Decisions for its current compatibility triple
  -> active/effective Access Rules for its current compatibility triple
```

For Component retirement the read model may additionally aggregate the number of Active Application Deployments indirectly depending on the Component through selected Interaction Definitions so the blocked UI can explain impact, but the direct structural blocker remains the Active Interaction Definition.

Deployment Interaction retirement first requires effective side bindings to be ended and active/effective downstream references to be retired/ended according to their owning contexts. Only then may its compatibility Component Deployments be retired. Their historical DCS/binding/downstream references remain valid.

### 7. Blocked operations expose structured dependencies

`CatalogueRetirementBlocked` and traffic-edit blocking must be explainable through a structured dependency projection, not only a generic message.

The application/read contract returns grouped dependency kinds and counts. Required semantic groups include, where applicable:

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

Each non-zero group is drillable through a bounded server-side list in the target API. Exact HTTP paths and pagination DTOs are owned by I31 M3, but clients must not infer dependencies from already-loaded UI trees.

### 8. Existing I27 rows coexist as legacy compatibility truth

Existing Component Deployments, DCS revisions and Deployment Resource Bindings are not automatically promoted into target Application Deployments or Interaction Definitions.

Automatic promotion is unsafe because legacy rows may connect different Applications and contain no trustworthy Company/Environment/Scope evidence.

Existing Application and Component identities may continue to appear as target Definitions/Components because their identity meaning is compatible. Their pre-I31 Component Deployments/DCS/bindings remain legacy ACC truth and continue to satisfy existing downstream references.

During coexistence:

- target authoring creates only the new Application Deployment / Deployment Interaction model;
- target Web does not expose legacy Component Deployment as the deployment unit;
- existing legacy rows remain available to downstream compatibility reads;
- legacy active Component Deployments may block Component retirement and must be exposed as a dependency class rather than silently ignored;
- removal of the legacy maintenance surface is deferred until no required active legacy participant remains or an explicit migration workflow supplies missing business context.

No legacy display name is used to invent Company, Environment, Scope, target Deployment or Interaction Definition identity.

## Consequences

- existing downstream contexts keep their semantic identity types and historical rows unchanged;
- target interaction-scoped Resource sets work because each Deployment Interaction owns distinct compatibility sides;
- traffic edits preserve immutable DCS history and fail safely when active downstream truth would become stale;
- structural endpoint replacement cannot silently change compatibility identity meaning;
- accepted wireframe metadata can be implemented without inventing Company/Organization/Party registries or authority coupling;
- retirement becomes explainable and consistently blocked by active references;
- legacy I27 runtime truth can coexist with target-created truth without fabricated migration semantics;
- I31 M1 can implement the target Domain/Application model without requiring downstream bounded-context rewrites.
