# Application Catalogue Target Migration Roadmap

Status: `selected for I31; implementation pending`.

Date: 2026-09-10.

## Purpose

Migrate the implemented I27 Application Communication Catalogue to the accepted Application Definition / Application Deployment target from PR #57 without rewriting existing Connectivity Requirement, Connectivity Decision, Access Rule or policy-export truth.

Canonical target inputs:
- `docs/decisions/ADR-012-application-definition-deployment-model.md`;
- `docs/ui/application-catalogue-target.md`;
- `docs/ui/application-catalogue-wireframes.md`.

Current runtime truth remains the I27 model until the relevant I31 stage is accepted and implemented.

## Current-to-target gap

| Layer | Current runtime | Target | Priority / migration consequence |
| --- | --- | --- | --- |
| Domain identity | `Application -> Component -> ComponentDeployment`; downstream identity is `(sourceComponentDeploymentId, destinationComponentDeploymentId, dcsRevisionId)` | Application Definition owns Components and Interaction Definitions; `ApplicationDeployment` is deployment unit | **P0** — define compatibility projection before code migration; existing downstream identities and historical facts must remain valid |
| Interaction semantics | immutable DCS revision is authored between Component Deployments | Interaction Definition is authored between Components; Deployment selects a subset and inherits traffic | **P0** — define edit/snapshot semantics that preserve historical downstream DCS references |
| Resource binding | temporal binding belongs to Component Deployment | binding belongs to one Deployment Interaction side | **P0** — same Component may resolve to different Resource sets per interaction; old global binding ownership cannot be exposed as target truth |
| Deployment context | Component Deployment has optional display name only | Application Deployment has Company / Environment / Scope context | **P0** — ownership/reference semantics are not yet canonical; I27 explicitly did not introduce Company/Organization ownership |
| Definition metadata | Application has display name only; Component has display name only | wireframes require Application Domain/Owner/description and Component Type/Description | **P0** — accepted UX requires data not currently defined by the canonical domain model |
| Lifecycle | Active -> Retired; parent retirement blockers are structural; Component Deployment may retire with historical references | Active -> Retired; retirement blocked by active incoming references; no hard delete | **P0** — dependency rules and dependency-count read contract must be made consistent for new entities |
| Read API | application list supports page/search; detail returns the full nested component/deployment/binding/DCS tree | separate Definitions/Deployments working sets and server-backed bounded tables | **P1** — replace whole-tree workspace reads with task-oriented paged projections |
| API write model | create Component Deployment, DCS revision between deployments, bind Resource to deployment | create Application Deployment, Interaction Definition, select Deployment Interactions, bind each side | **P1** — new task-oriented commands; compatibility identities remain backend-only |
| Scale contract | `hasMore`; limited filters; nested detail can expand all children | paging/search/filter/sort, exact row counts in wireframes, URL query state | **P1** — add stable sorting/filter contracts and totals where the UI displays totals |
| Web IA | one Applications list plus one monolithic Application tree; status/version/internal IDs visible | Definitions/Deployments, Definition tabs, Deployment connectivity table, count drill-downs | **P1** — replace the user projection rather than restyle the existing tree |
| Interaction authoring UI | selects Component Deployments across catalogue; wrapper authors one protocol + one destination port | selects Components in one Definition and supports traffic alternatives | **P1** — replace authoring flow; reuse existing vendor-neutral traffic value semantics where applicable |
| Retirement UX | generic `409 CatalogueRetirementBlocked` and browser confirms | blocked action explains active dependency counts with drill-down | **P1** — add structured dependency read/error projection |
| Acceptance | J01 asserts old Component -> deployment -> DCS UI; J03 consumes old identity directly | target wireframes plus downstream behavior must remain valid | **P1** — replace J01 and prove the compatibility projection through existing downstream journeys |

## Minimal migration strategy

### Preserve the stable boundary first

The minimum-change direction is to keep the existing downstream semantic triple as a compatibility contract while changing the ACC product model and curation API above it.

Preferred implementation candidate, pending WP-0 acceptance:

```text
Application (existing stable id; presented as Definition)
  -> Component
  -> InteractionDefinition

ApplicationDeployment
  -> DeploymentInteraction
      -> InteractionDefinition
      -> source-side Resource bindings
      -> destination-side Resource bindings

DeploymentInteraction
  -> internal compatibility projection
      -> source ComponentDeployment identity
      -> destination ComponentDeployment identity
      -> immutable DCS revision
      -> existing DirectedInteractionIdentity triple
```

Compatibility Component Deployment identities must be unique per Deployment Interaction side, not merely per Component. Otherwise two interactions using the same Component could not bind different Resource sets as required by ADR-012.

The compatibility projection is an internal adapter/persistence concern. New Application Catalogue Web/API surfaces must not require users to understand or assemble compatibility Component Deployment IDs.

Traffic changes may be represented by a new immutable DCS revision for the current compatibility pair while older DCS revisions remain addressable by historical downstream subjects. Exact edit rules, especially source/destination Component changes on an Interaction Definition already selected by active Deployments, are a blocking WP-0 decision rather than an implementation assumption.

### Do not infer target meaning from legacy I27 rows

Existing I27 Component Deployments, DCS revisions and bindings remain valid historical/runtime facts. Migration must not infer Application Deployment context, Interaction Definition ownership or Company/Environment/Scope from display names.

Some existing DCS rows can legally connect participants across Applications, while the target Interaction Definition belongs to one Application Definition. Therefore automatic promotion of arbitrary legacy DCS rows into target editable entities is unsafe. A later explicit migration/import workflow may be added only if it has sufficient business input.

### Distinguish business versioning from concurrency

ADR-012 defers Application Definition versioning. Existing integer `version` fields may remain as technical optimistic-concurrency tokens where needed; they are not user-facing Definition revisions and should not be rendered as catalogue metadata.

## Ordered stages

| Stage | Outcome | Main gate |
| --- | --- | --- |
| M0 — contract closure | compatibility identity projection, metadata/context ownership, interaction edit semantics and retirement dependencies are canonical and implementation-ready | no blocking unknown/conflict; `knowledge-check` + `harness-check` |
| M1 — domain/application | target entities, invariants, commands, query ports and compatibility-projection port exist without transport/persistence coupling | domain/application tests + architecture/core gate |
| M2 — persistence/projection | additive PostgreSQL schema persists target entities and selected compatibility mapping while preserving all legacy IDs/facts | migration replay + PostgreSQL integration + downstream projection tests |
| M3 — HTTP/read models | bounded Definitions/Deployments/Components/Interactions/resource-set APIs support server paging/search/filter/sort and structured retirement dependencies | HTTP contract/security/integration tests |
| M4 — Web target | accepted wireframes implemented: Definitions/Deployments, Definition tabs, one Deployment connectivity table and count drill-downs | `make web-check` + deterministic browser target journey |
| M5 — compatibility acceptance/absorption | target-authored data works through Connectivity/Decision/Access Policy; representative screenshot regressions protect layout; canonical current-state docs absorbed | J01 replacement + relevant J03/downstream regressions + Docker/hosted final gates |

Each stage is one coherent semantic integration stage and should use its own draft PR/squash merge. Do not combine M0 through M5 into one implementation PR.

## M0 blocking decisions

1. **Downstream compatibility identity.** Accept or replace the preferred internal projection while preserving every existing downstream identity and historical reference.
2. **Interaction edit boundary.** Define whether source/destination Components are mutable after an Interaction Definition has active Deployment selections; define how traffic edits produce immutable downstream snapshots.
3. **Application Definition metadata.** Define ownership and validation for `description`, `domain`, and `owner`, or explicitly amend the accepted wireframes before implementation.
4. **Component metadata.** Define ownership and allowed vocabulary/reference semantics for `type` and `description`, or explicitly amend the wireframes.
5. **Application Deployment context.** Define Company, Environment and Scope as owned identities or external correlation/value data. Do not create a Company/Organization aggregate only to satisfy the UI.
6. **Retirement dependencies.** Define active incoming references for Application, Component, Interaction Definition, Application Deployment and Deployment Interaction, including the shape returned for blocked-retirement drill-down.

## API/read-model direction after M0

Prefer extending the existing catalogue boundary rather than creating a second parallel catalogue API. `Application` may retain its stable ID and route as the Definition identity if M0 accepts that mapping.

Required capabilities are:
- paged Definition list with target columns/counts, filters, sort and total;
- Definition overview plus separately paged Components, Interaction Definitions and Deployments;
- paged global Application Deployment list;
- Application Deployment overview plus paged selected-interaction connectivity rows;
- paged/searchable/filterable Resource set for one Deployment Interaction side;
- task commands for Interaction Definition, Application Deployment, Deployment Interaction selection and side bindings;
- structured retirement dependency discovery;
- compatibility Component Deployment/DCS identities kept behind ACC-owned ports/adapters.

Do not retain the current full nested Application workspace as the primary target read contract merely to minimize frontend changes; it conflicts with the accepted scale model.

## Web direction after M3

The target Web adapter should follow `docs/ui/application-catalogue-wireframes.md` literally for information architecture and actions:
- `Applications -> Definitions | Deployments`;
- dense bounded tables rather than card trees;
- no ordinary Status column/badge for Components or normal Retired rows;
- no user-facing optimistic-concurrency version or implementation UUID noise;
- one connectivity table per Application Deployment;
- Resource collections rendered as counts and opened through bounded drill-down tables;
- inherited traffic read-only in Deployment;
- no hard-delete path.

## Completion criterion

I31 is complete when an admitted user can create/edit an Application Definition, Components and Interaction Definitions, create an Application Deployment, select any subset of its interactions, curate source/destination Resource sets, and consume the resulting interaction through existing Connectivity/Decision/Access Policy semantics without changing historical downstream identities; the accepted target layout is protected by deterministic browser/screenshot regression evidence.