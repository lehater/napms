# Web UI requirements — connectivity workspace direction

Status: `accepted product/UX direction through I16A WP-02`.

Date: 2026-09-09.

## Purpose

Define the current NAPMS Web UI product/UX requirements.

This file owns product-facing Web UI behavior and information architecture. Detailed cross-context overview semantics are owned by docs/requirements/scoped-connectivity-inventory.md. docs/ui/ owns implementation-oriented visual handoff. Runtime/API mechanics remain engineering concerns.

## Product boundary

The Web UI is a human-facing outer adapter over accepted NAPMS application/domain capabilities. It is not a second source of business truth.

The UI may compose read models across bounded contexts when that composition has an explicit accepted contract. It must not duplicate or redefine Resource Catalogue, Application Communication Catalogue, Connectivity Requirements, Connectivity Decision, Access Policy, or later realization-context truth.

Backend routes/DTOs follow accepted application use cases and read compositions rather than generic database CRUD.

## Primary user model

The default user experience is responsibility- and resource-centric:

    Login
      -> Connectivity
      -> selected responsibility scope
      -> local Resources
      -> bound Component Deployments
      -> connectivity relationships
      -> Need / Decision / Policy
      -> Realization later

The user must understand the landscape without learning NAPMS bounded-context names or manually reconstructing one relationship across several pages.

## Authority and scope

The authenticated session supplies actor identity. The client never supplies trusted actor_id.

The selected scope is the workspace responsibility context. It determines the local/my side and is an input to admitted actions.

The backend remains authoritative for every domain action. UI hiding/disabling is presentation only.

Existing action-specific authority remains independent, including Connectivity Requirements actions, ProposeConnectivity, DecideConnectivity / ReadConnectivityDecision, ReadAccessRule, Rule state/effective-window mutation and ReadEffectiveDesiredPolicy.

Ownership/responsibility must not be treated as implicit permission. Authority Management remains authoritative.

I16A accepts the local-side relation:

    Resource Catalogue:
    Resource -> Resource Scope Affiliation -> selected Responsibility Scope

    Authority Management:
    Actor -> ReadScopedConnectivity -> selected Responsibility Scope

Resource membership and actor authority remain independent. `ReadScopedConnectivity` admits the coarse owner workspace but does not imply protected Requirement/Decision/Rule details or mutation actions.

## Current catalogue visibility baseline

For the current increment, authenticated users may read catalogue information needed to understand both sides of connectivity:

- Resource Catalogue Resources/Endpoints;
- ACC Applications/Components/Component Deployments;
- DCS labels/traffic semantics;
- DeploymentResourceBindings.

Foreign catalogue objects are therefore visible as remote-side context and are read-only unless a separately admitted action exists.

This global catalogue visibility does not grant global read access to protected Requirement, Decision or Access Rule details.

Fine-grained discover/read visibility for foreign catalogue objects is deferred. Future visibility policy remains independent from domain-action authority and object identity.

## Primary workspace — Connectivity

After Login, the primary route is Connectivity.

Purpose:

> Show all local Resources in the selected responsibility scope, the application Component Deployments bound to them, their incoming/outgoing connectivity relationships, the remote side, access semantics and independent Need/Decision/Policy states.

Canonical detailed requirements: docs/requirements/scoped-connectivity-inventory.md.

### Primary presentation

The first implementation is a full-width resource-centric hierarchical table/tree-grid:

    Resource
      -> Component Deployment
        -> Connectivity Relationship

It must show Resources/Components even when they have zero connectivity.

Useful columns:

- My Resource;
- Component;
- Direction;
- Access;
- Remote Component;
- Remote Resource;
- Need;
- Decision;
- Policy;
- later Realization.

Do not collapse Need/Decision/Policy/Realization into one generic status.

### Direction

Direction is shown relative to local/my side: outgoing or incoming.

Canonical source/destination identities remain available in technical details.

### Access presentation

Use readable DCS/service meaning as primary text.

Protocol/ports are secondary/optional technical information and may be exposed through a second line, details or column chooser.

### Remote side

Remote Component and Resource data are visible under the current catalogue visibility baseline even when they belong to another responsibility scope.

### Empty resources/components

A local Resource/Component with no connectivity must still be visible and may expose Add connectivity when the backend admits the operation.

## Add Connectivity

Compose Connectivity is no longer a primary sidebar destination. Proposal composition becomes a contextual action started from the Connectivity workspace or another relevant detail page.

Typical flow:

    local Resource/Component already known
      -> Add connectivity
      -> select remote side
      -> select structurally valid DCS/access
      -> applicability/justification where required
      -> Request access

The UI reuses known context and does not ask the user to re-enter selected scope/local Resource/local Component.

Remote/DCS options come from trusted backend catalogue/use-case discovery. The UI must not assemble arbitrary stable-ID combinations.

At product level, Request access may compose accepted backend stages such as Requirement declaration/resolution, proposal, Decision and Allowed Rule materialization. Backend ownership boundaries do not become mandatory user navigation.

## Connectivity Decision workflow

Connectivity Decision remains an immutable final business result:

    Allowed | NotAllowed

Do not add Pending, Approved, Rejected, UnderReview or Revoked to Connectivity Decision.

There is now a product need to represent submitted connectivity that may be awaiting a final decision. Before such a state becomes durable UI semantics, I16A/I16B must decide whether it belongs to an application workflow without independent business identity or a distinct domain process/entity with its own lifecycle.

Until that decision is accepted, the UI must not invent a persistent waiting lifecycle.

## Specialized workspaces

The resource-centric Connectivity workspace is the normal entry point. Specialized workspaces remain available for focused work and explainability.

### Needs

Purpose: inspect and manage authoritative Connectivity Requirements admitted for the actor.

Presentation rules:

- readable Source/Destination/DCS labels first;
- stable IDs secondary;
- applicability;
- lifecycle Active | Retired;
- justification;
- derived alignment Covered | Uncovered | NotCurrent | Unknown;
- independent admitted mutations.

Uncovered is never labelled Denied.

Primary page title/navigation label is Needs; canonical domain term Connectivity Requirement remains available in details/help.

### Decisions

Purpose: inspect final Connectivity Decisions and, after I16B, support real decision-participant work if accepted by workflow semantics.

Decision details require corresponding backend read authority.

Before I16B implementation this navigation item may be shown only as a clearly disabled Planned item.

### Rules

Purpose: inspect authoritative Access Rules admitted through ReadAccessRule.

Show readable source/destination/access labels first; technical IDs, Rule Governance Scope, Decision correlation and provenance progressively.

Rule state remains Active | Inactive. Read authority does not imply mutation authority.

### Effective

Purpose: inspect SelectEffectiveDesiredPolicy(scope, asOf, actor).

The page must communicate what desired policy applies for this scope/time rather than expose application-method naming.

### Export / normalized technical view

Normalized Policy remains a valid technical/export representation, but it is not required to be a top-level primary navigation label.

When exposed, present it as an export/technical view while preserving all normalized semantics and provenance.

## Information architecture

Baseline sidebar:

    OVERVIEW
      Connectivity

    POLICY
      Needs
      Decisions        Planned until implemented
      Rules
      Effective

    TECHNICAL
      Realization      Planned
      Evidence         Planned
      Enforcement      Planned

Add catalogue/admin workspaces only after concrete user workflows exist:

    CATALOGS
      Applications
      Resources

    ADMINISTRATION
      Authorities

### Planned navigation rule

Roadmap-backed future areas may be visible to validate the complete information architecture only when:

- explicitly marked Planned;
- visually distinct from active workspaces;
- unable to perform fake actions or show fabricated data;
- not mistaken for implemented functionality;
- backed by accepted roadmap/product scope.

Do not add arbitrary placeholder navigation outside accepted product direction.

## Labels and language

Navigation and primary table labels should be short and user-oriented.

Prefer Connectivity, Needs, Decisions, Rules, Effective, Resources, Component, Access and Remote.

Avoid internal use-case/navigation labels such as Compose Connectivity, Policy Views, Requirement-to-Policy Alignment and Normalized Policy.

Canonical DDD terminology and stable UUIDs remain visible in technical details, help and explainability views.

## Interaction details

Opening one connectivity relationship should progressively expose:

- Need;
- Decision;
- Policy;
- Local side;
- Remote side;
- technical identifiers/DCS;
- provenance/history where separately admitted;
- Realization later.

Protected Decision/Rule/Requirement details must not be leaked by the overview merely because underlying catalogue objects are globally visible.

## Existing business-state requirements

### Connectivity Requirements

Lifecycle remains Active -> Retired. No Requirement Pending/Approved/Rejected.

### Requirement-to-Policy Alignment

Status remains Covered | Uncovered | NotCurrent | Unknown. No configured/observed claim.

### Connectivity Decision

Outcome remains Allowed | NotAllowed. NotAllowed is a valid business result, not an HTTP/security error.

### Access Rule

Operational state remains Active | Inactive. EffectiveWindow semantics remain explicit half-open [start,end).

## Layout and density

The UI remains desktop-first enterprise/control-plane software.

Accepted baseline:

- dark navy collapsible sidebar;
- light working area;
- restrained blue accent;
- dense operational tables/forms;
- borders/restrained elevation;
- React + TypeScript + Tailwind + shadcn/ui;
- WCAG 2.2 AA target.

Operational inventories/tables use available viewport width. Do not place the primary Connectivity tree-grid inside a narrow marketing-style max-width container.

Focused forms/details may use bounded readable widths.

## Table/tree-grid requirements

- potentially unbounded data uses server-side paging/filter/search where required;
- shareable query state belongs in URL where reasonable;
- tree expansion/collapse is keyboard accessible;
- statuses never rely on color alone;
- loading, genuine empty, filtered-empty, authorization-limited and retryable failures are distinct;
- Resource/Component group rows are not duplicated merely to fit a flat-table abstraction;
- technical column selection may expose protocol/ports/IDs without changing semantic truth.

## Forms and mutations

- server/domain remains authoritative;
- obvious structural validation may happen client-side;
- prevent duplicate mutation submission;
- field errors appear near fields;
- request/domain errors are distinct from transport errors;
- destructive/security-significant actions require confirmation when accidental execution is plausible.

## Authentication/session UX

Current local/test runtime remains login + password with explicit logout.

No public/anonymous access or enterprise SSO is implied by this UI revision.

## Responsive baseline

- >= 1280px: full desktop shell;
- 768..1279px: collapsed sidebar by default; dense tree-grid may scroll horizontally;
- < 768px: functional overlay navigation and usable forms/details; mobile is not the primary optimization target.

## Non-goals of the next UI slice

- generic CMDB/application portfolio CRUD;
- new Connectivity Overview bounded context;
- fine-grained foreign catalogue visibility;
- invented persistent Access Request lifecycle;
- adding waiting states to Connectivity Decision;
- graph as the first implementation;
- configured/reconciliation UI before I17-I20;
- vendor-specific rendering/device execution;
- fake metrics/dashboard cards;
- duplicating business truth in frontend state.
