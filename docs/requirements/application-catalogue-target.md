# Application Catalogue as-built requirements

Status: `current as-built product contract`.

## Role

This document defines the user-observable Application Catalogue behavior implemented by the current product. It is retained because the implemented system must be reconstructable from project documentation.

Current target ownership is defined by `application-catalogue-domain-target.md`, the ACC target model and the Application Deployment model. Where this as-built contract differs from that target, this document governs reconstruction of current behavior only and does not redefine target semantic ownership.

The implemented behavior is supported by ADR-012 and ADR-013.

## User model

Applications has two working sets:

```text
Applications
  Definitions
  Deployments
```

An Application Definition describes reusable application structure and communication intent. An Application Deployment represents one use of that Definition in Company/Environment/Scope context.

## Application Definition

A Definition allows an admitted user to maintain:

- name;
- optional description;
- optional domain classification;
- optional owner correlation reference;
- Components;
- Interaction Definitions;
- Application Deployments using the Definition.

Component supports:

- name;
- optional type/classification;
- optional description.

Component type is descriptive rather than a closed behavioral taxonomy.

## Interaction Definition

One Interaction Definition contains:

- source Component;
- destination Component;
- one or more traffic alternatives using vendor-neutral protocol/port semantics.

Both Components belong to the same Application Definition.

The implemented model has no Deployment-specific endpoint or traffic override. An Interaction Definition may be selected by zero, one or many Application Deployments of its Definition.

## Interaction edits

Source or destination Component may be changed only while the Interaction Definition has no Active Deployment Interaction selection.

Traffic may be edited for an Interaction Definition with Active selections only when none of the affected current downstream compatibility identities has an active/effective Connectivity Requirement, final/effective Connectivity Decision or active/effective Access Rule.

A permitted traffic edit updates all Active Deployment Interactions selecting that Definition as one semantic operation. Existing immutable DCS revisions and downstream references remain unchanged.

When an edit is blocked, the UI explains dependency categories/counts and provides bounded drill-downs rather than only a generic conflict.

## Application Deployment

An Application Deployment contains:

- selected Application Definition;
- Company external correlation reference;
- Environment label;
- Responsibility Scope external correlation reference;
- zero or more selected Deployment Interactions.

Company, Environment and Scope do not define Deployment identity and do not grant catalogue or policy authority.

A new Deployment may initially contain zero selected interactions and be populated incrementally. A Deployment may select any subset of the Definition's Active Interaction Definitions; partial selection is normal.

The same Interaction Definition may be selected at most once as an Active Deployment Interaction in one Application Deployment.

## Interaction-scoped Resource sets

Each selected Deployment Interaction has two independently curated Resource sets:

```text
Source Resources
Destination Resources
```

Resource membership is scoped to that Deployment Interaction side. The same Component may therefore map to different Resource sets in different Deployment Interactions.

Resource references are selected through backend-owned Resource discovery in the normal workflow. Membership is temporal/history-preserving according to the ACC binding contract; ending membership does not erase historical truth.

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

The local-first product may accept explicit correlation text where no configured discovery adapter exists. A discovery adapter may replace text entry with selection without changing ACC identity.

Environment is ACC-owned descriptive deployment context and is not Network Environment Operations identity.

## Lifecycle

Application Definition, Component, Interaction Definition, Application Deployment and Deployment Interaction use terminal lifecycle:

```text
Active -> Retired
```

No normal hard-delete action exists.

Retired entities are excluded from normal working lists and remain available where reference explanation requires them.

Retirement is blocked while active dependants/references exist. Required blocker classes are defined by the as-built ACC Tactical model and ADR-013.

For a blocked operation the UI shows grouped dependency counts and lets the user drill into each non-zero group.

## Compatibility behavior

Current authoring does not require users to understand or enter compatibility Component Deployment IDs or DCS revision IDs.

ACC internally projects each Active Deployment Interaction into the downstream `DirectedInteractionIdentity` shape so current Connectivity Requirement, Connectivity Decision, Access Rule and export behavior can consume the current catalogue without identity rewrite.

Existing downstream business records remain valid and are never rewritten because catalogue authoring changes.

Existing compatibility Component Deployments, DCS revisions and bindings that remain referenced are retained as current implementation compatibility truth. They are not automatically converted into Application Deployments because required Company/Environment/Scope and interaction ownership cannot be inferred safely.

The current UI does not present compatibility Component Deployment as the normal deployment unit. Compatibility participants remain available where required for downstream behavior and dependency explanation.

## Authority

Application Catalogue mutation authority remains backend-owned and independently evaluated.

Authenticated identity, owner correlation, Company, Environment, Scope and Resource responsibility are business/context data and do not themselves grant mutation authority.

## Rebuild acceptance

A reconstructed current product must support at least:

1. create a Definition and Components;
2. create Interaction Definitions with multiple traffic alternatives;
3. create an Application Deployment with Company/Environment/Scope context;
4. select only a subset of Definition interactions;
5. curate independent source/destination Resource sets for selected interactions;
6. consume an authored interaction through the current Connectivity/Decision/Access Policy compatibility behavior without downstream identity rewrite;
7. preserve old downstream references after a later permitted Definition traffic change;
8. block unsafe traffic edit or retirement when active dependencies exist and expose dependency counts/drill-down;
9. keep normal lists free of Retired entities and hard-delete actions;
10. keep large lists bounded through server-side paging/search/filter/sort.

These acceptance points define current as-built behavior. They do not constrain the ownership split of the newer target ACC/AD model beyond explicit compatibility requirements.
