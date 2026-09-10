# Application Communication Catalogue Tactical Model

Status: `accepted for I27 catalogue curation Stage 0`.

Date: 2026-09-10.

## Purpose

Define the Tactical DDD model required to curate the Application Communication Catalogue through normal NAPMS product workflows while preserving existing Access Rule, Connectivity Requirement, Connectivity Decision and policy identities.

This document refines the already accepted Strategic DDD ownership:

```text
Application Communication Catalogue
    owns Application / Component / Component Deployment / Directed Communication Specification identities and structure
```

It does not turn NAPMS into a generic application portfolio, deployment inventory or CMDB.

## Product boundary

The catalogue exists to describe application participants and communication semantics that are relevant to governed network access.

The first curation slice supports this hierarchy:

```text
Application
  -> Component
      -> Component Deployment

Component Deployment
  -> Deployment Resource Binding -> Resource Catalogue Resource

Directed Communication Specification Revision
  -> Source Component Deployment
  -> Destination Component Deployment
  -> immutable traffic projection
```

Application and Component are structural catalogue identities. Component Deployment remains the identity used directly by Connectivity Requirement, Connectivity Decision and Access Rule semantic subjects.

## Identity model

### Application

```text
Application
    applicationId: UUID
    displayName: non-empty string
    lifecycle: Active | Retired
    provenanceReference: non-empty string
```

`applicationId` is stable and server-owned.

Display-name changes do not create another Application and do not affect downstream policy identity.

### Component

```text
Component
    componentId: UUID
    applicationId: UUID
    displayName: non-empty string
    lifecycle: Active | Retired
    provenanceReference: non-empty string
```

A Component belongs to exactly one Application for its lifetime.

Moving a Component between Applications is not an in-place edit in I27. If the business concept changes parent Application, curate a replacement Component and retire the old one. This avoids silently rewriting structural provenance relied on by deployed participants.

### Component Deployment

```text
Component Deployment
    deploymentId: UUID
    componentId: UUID
    displayName: optional non-empty string
    lifecycle: Active | Retired
    provenanceReference: non-empty string
```

`deploymentId` is the existing stable UUID already consumed by downstream semantic identities.

A Component Deployment belongs to exactly one Component for its lifetime.

Changing its parent Component in place is forbidden. Replacement is represented by another deployment identity plus retirement of the old deployment when appropriate.

The existing optional deployment display name remains presentation metadata. If omitted, consumers may fall back to the parent Component name or stable deployment ID according to the owning read contract.

### Directed Communication Specification Revision

The existing DCS revision identity remains unchanged:

```text
DcsRevision
    revisionId: UUID
    sourceComponentDeploymentId: UUID
    destinationComponentDeploymentId: UUID
    immutable projectionPayload
    displayName: optional non-empty string
    provenanceReference: non-empty string
```

A DCS revision is immutable communication truth. Editing communication semantics creates another DCS revision; existing Requirements, Decisions and Rules keep references to their original immutable revision.

I27 may add authoring commands that produce a DCS projection, but those commands must not expose `projectionPayload` as a user-authored opaque persistence blob.

### Deployment Resource Binding

The existing temporal relation remains:

```text
Deployment Resource Binding
    referenceId: stable string
    componentDeploymentId: UUID
    resourceReference: Resource Catalogue reference
    validity: [validFrom, validUntil)
    provenanceReference: non-empty string
```

A binding relates two independently owned identities. It does not make Resource identity part of Component Deployment identity.

## Lifecycle

### Catalogue entity lifecycle

I27 adopts a minimal lifecycle for Application, Component and Component Deployment:

```text
Active -> Retired
```

`Retired` is terminal for the first curation slice.

Retirement means the catalogue identity is no longer available for new authoring/discovery flows that require active participants. Historical reads and references remain valid.

Retirement does not rewrite or delete existing Connectivity Requirements, Connectivity Decisions, Access Rules, DCS revisions or historical bindings.

### Parent/child retirement invariants

Retirement does not cascade physically.

The application layer must reject retirement that would create structurally invalid active children:

- an Application cannot be retired while it has Active Components;
- a Component cannot be retired while it has Active Component Deployments;
- a Component Deployment may be retired while historical bindings/DCS revisions/downstream policy references exist because those references remain historical truth.

This requires the user to retire from leaves upward and makes the consequence explicit rather than silently cascading state changes.

### Hard deletion

Normal product commands do not hard-delete Applications, Components, Component Deployments, DCS revisions or historical bindings.

Database-level destructive maintenance is outside the I27 product contract.

## Structural invariants

The ACC write model enforces:

1. every Component references an existing Application;
2. every Component Deployment references an existing Component;
3. active Components require an Active parent Application;
4. active Component Deployments require an Active parent Component and Active ancestor Application;
5. DCS source and destination deployments must exist;
6. new DCS revisions may reference only Active deployments for normal authoring;
7. new Deployment Resource Bindings may reference only an Active Component Deployment and an existing Resource Catalogue Resource admitted by the consuming use case;
8. no parent identity is changed in place;
9. no lifecycle action changes downstream semantic identities.

## Aggregate and consistency boundary

Application, Component and Component Deployment are separate stable catalogue entities persisted within the ACC bounded context.

I27 does not require one large aggregate loading an entire Application tree for every command. Structural invariants are enforced through ACC-owned application services/repositories under one transactional boundary where a command spans several ACC records.

The tactical model should remain KISS-oriented:

- command one semantic mutation at a time;
- validate parent existence/state before child creation;
- use database foreign keys as structural backstops, not as the only domain validation;
- preserve downstream immutable references.

## Command responsibility

The application layer will expose task-oriented commands rather than a generic repository CRUD API.

Expected command families after Stage 0 closure:

```text
CreateApplication
RenameApplication
RetireApplication

CreateComponent
RenameComponent
RetireComponent

CreateComponentDeployment
RenameComponentDeployment
RetireComponentDeployment

CreateDeploymentResourceBinding
EndDeploymentResourceBinding

CreateDcsRevision
```

Exact authority action names and DCS authoring request shape remain separate Stage 0 P0 decisions.

## Query responsibility

Catalogue curation requires read models that support:

```text
Applications
  -> Components
      -> Component Deployments
          -> effective Resource bindings
          -> communication specifications
```

The read side may be optimized independently from write entities, but it must preserve ACC ownership and stable IDs.

Existing interaction discovery/read consumers remain valid and must not be forced through the curation UI projection.

## Compatibility with the existing implementation

### Existing state

Before I27, persisted ACC state contains:

```text
component_deployments
    component_deployment_id
    provenance_reference
    display_name

dcs_revisions
    revision_id
    source_component_deployment_id
    destination_component_deployment_id
    projection_payload
    provenance_reference
    display_name

deployment_resource_bindings
    ...
```

Downstream contexts already treat `component_deployment_id` and `revision_id` as stable semantic references. I27 must preserve them exactly.

### Migration principle

The schema extension introduces Application and Component parent identities without replacing existing deployment IDs.

For existing pre-I27 rows, migration must create deterministic compatibility parents rather than invent domain meaning from display names.

Accepted migration strategy:

```text
one compatibility Application
    id = deterministic repository-defined UUID
    name = "Imported catalogue"

one compatibility Component per existing Component Deployment
    id = deterministic function of deploymentId
    name = existing deployment displayName when present,
           otherwise deploymentId

existing Component Deployment
    keeps deploymentId unchanged
    gains componentId pointing to its compatibility Component
```

Why one Component per deployment initially:

- there is no trustworthy pre-I27 evidence that two deployments belong to the same logical Component;
- grouping by equal display name would manufacture identity;
- grouping every deployment under one Component would collapse distinctions the strategic model says are independent;
- deterministic one-to-one compatibility parents preserve all existing semantics and can later be curated explicitly through supported replacement/retirement workflows.

The compatibility Application/Components are real ACC records after migration, not UI-only aliases.

Migration-generated provenance must explicitly identify the I27 compatibility migration as its source.

### Migration non-goals

The migration must not:

- change an existing `component_deployment_id`;
- change an existing DCS `revision_id` or its source/destination deployment references;
- infer Application names, Component grouping, ownership or responsibility from deployment names;
- rewrite Connectivity Requirements, Decisions, Access Rules or policy export facts;
- create Resource bindings that did not already exist.

## Concurrency and consistency

Commands that mutate catalogue entities must use explicit optimistic concurrency or another accepted lost-update prevention mechanism before HTTP/Web mutation is opened.

The exact version field/ETag contract is decided in the I27 command/idempotency P0 closure. The tactical invariant is that concurrent edits must not silently overwrite each other.

## Authority boundary

Catalogue lifecycle or structural ownership does not imply actor permission.

Every mutation command is admitted by Authority Management using the authority action model accepted later in I27 Stage 0.

Read/discovery visibility remains independent from mutation authority.

Resource Responsibility and Resource Scope Affiliation remain Resource Catalogue concerns and do not grant ACC mutation authority.

## Consequences

- the accepted Strategic DDD hierarchy now has an explicit write model;
- existing deployment/DCS identities remain compatible;
- parent reassignment cannot silently mutate meaning;
- normal product deletion becomes retirement rather than referential destruction;
- migration handles missing historical Application/Component knowledge without guessing it;
- infrastructure/API/UI implementation can proceed only after the remaining Stage 0 authority, DCS-authoring and command-concurrency decisions are closed.
