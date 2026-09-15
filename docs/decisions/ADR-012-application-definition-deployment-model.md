# ADR-012 — Application Definition and Deployment Model

Status: `superseded as target by ADR-015; retained as implemented I31 history`.

Date: 2026-09-10.

> ADR-015 replaces the target semantics of this ADR. In particular, the accepted target now deploys Components through `ComponentDeployment`; it does not use `ApplicationDeployment` / `DeploymentInteraction` as target domain concepts. This document remains authoritative only for explaining the existing I31 implementation and its history.

## Context

The current I27 Application Communication Catalogue models:

```text
Application
  -> Component
      -> Component Deployment

DCS Revision
  -> Source Component Deployment
  -> Destination Component Deployment

Deployment Resource Binding
  -> Component Deployment
  -> Resource
```

This is implemented and remains the current runtime contract. Product/UX design now requires a different deployment boundary: users deploy an Application as a whole, select a normal subset of interactions defined by that Application, and bind source/destination Resources in the context of each selected interaction.

The target must stay KISS-oriented for the first iteration: no Application-definition versioning, no deployment overrides/exceptions and no hard delete.

## Decision

### Application Definition

An Application represents a reusable definition independent of Company/deployment context.

```text
Application Definition
  -> Components
  -> Interaction Definitions
```

An Interaction Definition belongs to one Application Definition and contains:

```text
source Component
destination Component
traffic alternatives: 1+
```

Traffic alternatives support multiple protocols and port/range sets for the same component pair, for example:

```text
TCP (80, 443, 8000-8010)
UDP (443)
```

### Application Deployment

`ApplicationDeployment` is the deployment unit.

```text
Application Deployment
  -> Application Definition
  -> Company / environment / scope context
  -> selected Deployment Interactions
```

A Deployment may select any subset of the Application Definition's Interaction Definitions. Partial selection is normal and is not an error, override or exception.

A selected interaction keeps the Definition semantics unchanged. Source Component, destination Component, protocol and ports are not overridden in Deployment.

If a different communication definition is required, it is represented by another Application Definition in this MVP.

### Interaction-scoped resource bindings

Resource bindings are scoped to one selected interaction and one side of that interaction:

```text
ApplicationDeployment
  -> DeploymentInteraction
      -> InteractionDefinition
      -> Source Resource Bindings[]
      -> Destination Resource Bindings[]
```

The same Component may therefore resolve to different Resource sets in different Deployment Interactions.

Bindings are not copied into Interaction Definition and are not global Component-to-Resource assignments.

### Versioning and overrides

Application Definition versioning is deferred.

A Definition edit changes the current definition used by all active Deployments that select the affected Interaction Definition.

Deployment-specific traffic overrides and exceptions are deferred. No generic overlay/merge mechanism is introduced.

### Lifecycle

Normal product hard delete is absent in this MVP.

Lifecycle is:

```text
Active -> Retired
```

Retirement is terminal.

An entity cannot be retired while any active incoming reference depends on it. The user must first remove or retire active dependants. Retired entities remain persisted for historical/reference integrity and are excluded from normal working lists unless required to explain an existing historical reference.

This rule applies consistently to catalogue entities and relations where retirement exists.

## UI consequence

Applications expose two top-level working sets:

```text
Applications
  Definitions
  Deployments
```

Definition detail exposes `Overview`, `Components`, `Interactions`, `Deployments`.

Deployment detail is centered on one dense connectivity table. One row represents one selected Interaction Definition enriched with source/destination Resource counts:

```text
Source Component | Source Resources | Destination Component | Destination Resources | Traffic
```

Resource collections are always summarized by count (`1 resource`, `327 resources`). The count is the drill-down target; resource names are not concatenated into an unbounded cell. Drill-down opens a server-paged/searchable/filterable resource table.

Large traffic sets use the same progressive disclosure rule: short sets may render inline, otherwise render a compact count/summary with detail on demand.

Potentially unbounded tables use server-side search/filter/sort/paging and fixed compact row presentation.

## Compatibility with current I27 implementation

This ADR intentionally does not rewrite ADR-006 or ADR-009 retroactively. They describe the implemented I27 model accurately.

Implementation must reconcile these current contracts:

- `ComponentDeployment` is currently the deployment identity consumed by downstream Connectivity Requirement, Decision and Access Rule semantics;
- `DcsRevision` currently references source/destination `ComponentDeployment` identities;
- `DeploymentResourceBinding` currently belongs directly to `ComponentDeployment`;
- current Web requirements and screen map expose the I27 hierarchy.

Before code migration, a separate implementation design must define how `ApplicationDeployment`, `InteractionDefinition`, `DeploymentInteraction` and interaction-scoped Resource bindings project into or replace the existing downstream semantic identities without silently rewriting historical policy truth.

## Consequences

Historical I31 consequences were:

- deployment semantics matched the then-selected product mental model: deploy one Application, use any subset of its defined interactions;
- resource realization was contextual to each selected interaction;
- Deployment UI remained compact for hundreds/thousands of interactions and resources;
- no exceptions, overlays, Definition revisions or hard-delete workflow were required in the first implementation;
- the I27 runtime remained valid until the I31 target was implemented.

These target conclusions are superseded by ADR-015. They remain here to explain why the current I31 runtime has its present structure.
