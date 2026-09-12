# Application Catalogue Target Requirements

Status: `superseded as target by ADR-015; retained as implemented I31 behavior`.

Date: 2026-09-10.

> The accepted future ACC requirements are now `application-catalogue-domain-target.md` and ADR-015. This document remains the observable requirements record for the existing I31 implementation and must not be used to extend `ApplicationDeployment` / `DeploymentInteraction` as the future domain model.

## Purpose

Define the user-observable Application Catalogue behavior selected by ADR-012 and the migration safety constraints closed by ADR-013.

This requirement superseded the I27 Application-side curation UX/structure. Resource Catalogue behavior from I27 remained unchanged unless separately amended.

## User model

Applications has two working sets:

```text
Applications
  Definitions
  Deployments
```

An Application Definition describes reusable application structure and communication intent. An Application Deployment represents one use of that Definition in Company/Environment/Scope context.

## Application Definition

A Definition shall allow an admitted user to maintain:

- name;
- optional description;
- optional domain classification;
- optional owner correlation reference;
- Components;
- Interaction Definitions;
- Application Deployments using the Definition.

Component shall support:

- name;
- optional type/classification;
- optional description.

Component type is not a closed business taxonomy in I31.

## Interaction Definition

One Interaction Definition shall contain:

- source Component;
- destination Component;
- one or more traffic alternatives using vendor-neutral protocol/port semantics.

Both Components belong to the same Application Definition.

A Deployment-specific endpoint or traffic override does not exist in I31.

An Interaction Definition may be selected by zero, one or many Application Deployments of its Definition.

## Interaction edits

Source or destination Component may be changed only while the Interaction Definition has no Active Deployment Interaction selection.

Traffic may be edited for an Interaction Definition with Active selections only when none of the affected current downstream interaction identities has an active/effective Requirement, final/effective Decision or active/effective Access Rule.

A permitted traffic edit updates all Active Deployment Interactions selecting that Definition as one semantic operation. Existing immutable DCS revisions and historical downstream references remain unchanged.

When an edit is blocked, the UI shall explain dependency categories/counts and provide bounded drill-downs rather than expose only a generic conflict.

## Application Deployment

An Application Deployment shall contain:

- selected Application Definition;
- Company external correlation reference;
- Environment label;
- Responsibility Scope external correlation reference;
- zero or more selected Deployment Interactions.

Company, Environment and Scope do not define Deployment identity and do not grant catalogue or policy authority.

A new Deployment may initially contain zero selected interactions and be populated incrementally.

A Deployment may select any subset of the Definition's Active Interaction Definitions. Partial selection is normal.

The same Interaction Definition may be selected at most once as an Active Deployment Interaction in one Application Deployment.

## Interaction-scoped Resource sets

Each selected Deployment Interaction has two independently curated Resource sets:

```text
Source Resources
Destination Resources
```

Resource membership is scoped to that Deployment Interaction side. The same Component may therefore map to different Resource sets in different Deployment Interactions.

Resource references are selected through backend-owned Resource discovery in the normal workflow.

Resource membership remains temporal/history-preserving according to the ACC binding contract; ending a membership does not erase historical truth.

## Deployment connectivity view

Deployment detail is centered on one server-backed connectivity table:

```text
Source Component | Source Resources | Destination Component | Destination Resources | Traffic
```

One row represents one Active Deployment Interaction.

Resource collections render as counts and drill down to a separately paged/searchable/filterable Resource table. Large traffic collections use compact summary plus detail-on-demand.

Potentially unbounded lists use server-side search/filter/stable sort/paging. The client does not load a whole catalogue tree to derive counts, filters or dependency lists.

## Metadata/reference behavior

Application domain and Component type are descriptive classifications. They do not change business identity or authority.

Application owner, Deployment company and Deployment scope are external correlation/reference data. NAPMS does not create Company/Organization/Person/Team/Scope aggregates merely because those fields are entered.

The current local-first product may accept explicit correlation text where no configured discovery adapter exists. Future discovery adapters may replace text entry with selection without changing ACC identity.

Environment is ACC-owned descriptive deployment context and is not Network Environment Operations identity.

## Lifecycle

Application Definition, Component, Interaction Definition, Application Deployment and Deployment Interaction use terminal lifecycle:

```text
Active -> Retired
```

No normal hard-delete action exists.

Retired entities are excluded from normal working lists and are shown only where history/reference explanation requires them.

Retirement is blocked while active dependants/references exist. Required blocker classes are defined by the ACC tactical model and ADR-013.

For a blocked operation the UI shall show grouped dependency counts and let the user drill into each non-zero group.

## Compatibility behavior

Target authoring shall not require users to understand or enter compatibility Component Deployment IDs or DCS revision IDs.

ACC shall internally project each Active Deployment Interaction into the existing downstream `DirectedInteractionIdentity` shape so existing Connectivity Requirement, Connectivity Decision, Access Rule and export semantics do not require identity rewrite.

Historical downstream business records remain valid and are never rewritten because the catalogue UI/model changed.

## Legacy coexistence

Existing pre-I31 Component Deployments, DCS revisions and bindings remain valid ACC/downstream truth.

They are not automatically converted into Application Deployments because Company/Environment/Scope and target Interaction ownership cannot be inferred safely.

Existing Application and Component identities may be reused as Definition/Component identities.

The current UI does not present legacy Component Deployment as the new deployment unit. Active legacy participants remain explainable dependencies until explicitly retired or migrated through a future workflow with sufficient business input.

## Authority

Existing Application Catalogue mutation authority remains authoritative.

Authenticated identity, owner correlation, Company, Environment, Scope and Resource responsibility are business/context data and do not themselves grant mutation authority.

## Historical I31 acceptance

I31 acceptance proved at least:

1. create a Definition and Components;
2. create Interaction Definitions with multiple traffic alternatives;
3. create an Application Deployment with Company/Environment/Scope context;
4. select only a subset of Definition interactions;
5. curate independent source/destination Resource sets for selected interactions;
6. consume a target-authored interaction through existing Connectivity/Decision/Access Policy behavior without downstream identity rewrite;
7. preserve old downstream references after later permitted Definition traffic change;
8. block unsafe traffic edit or retirement when active dependencies exist and expose dependency counts/drill-down;
9. keep normal lists free of Retired entities and hard-delete actions;
10. keep large lists bounded through server-side paging/search/filter/sort.

These are historical I31 acceptance criteria, not ADR-015 target criteria.
