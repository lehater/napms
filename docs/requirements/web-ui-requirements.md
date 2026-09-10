# Web UI requirements

Status: `accepted current product/UX direction through I27 Catalogue Curation`.

Date: 2026-09-10.

## Purpose

Define current product-facing Web behavior and information architecture. The Web UI is an outer adapter over accepted NAPMS application/domain capabilities; it is not a second source of catalogue, policy, decision, requirement, evidence or realization truth.

Detailed feature semantics remain owned by their requirement/domain/architecture artifacts. HTTP/runtime mechanics remain engineering concerns.

## Primary user model

The normal user journey is responsibility- and resource-centric:

```text
Login
  -> Connectivity / Checker
  -> selected responsibility scope when relevant
  -> Resources and bound application deployments
  -> Need / Decision / Policy / Realization
```

I27 also makes the catalogue truth behind those workflows self-service:

```text
CATALOGUES
  Applications
  Resources
```

These are task-oriented catalogue workspaces, not generic CMDB/application-portfolio CRUD.

## Authority, scope and visibility

The authenticated session supplies actor identity. The client never supplies trusted `actorId` or chooses authoritative catalogue curation scopes.

Backend application use cases remain authoritative for every protected read or mutation. UI hiding/disabling is presentation only.

The following remain distinct:

```text
catalogue visibility
!= selected Responsibility Scope
!= Resource Scope Affiliation
!= Resource Responsibility/contact
!= ReadScopedConnectivity
!= catalogue mutation authority
```

I27 catalogue mutation uses explicit backend-enforced Authority Management actions:

```text
CurateApplicationCatalogue @ application-catalogue
CurateResourceCatalogue    @ resource-catalogue
```

The current catalogue-read visibility baseline remains broad enough for authenticated users to understand both sides of connectivity: Resources/Endpoints, Applications/Components/Component Deployments, DCS presentation/traffic semantics and Deployment Resource Bindings may be visible as remote context. Readability does not grant mutation or protected Requirement/Decision/Rule access.

Fine-grained foreign catalogue visibility remains deferred unless separately required.

## Information architecture

Current primary navigation:

```text
OVERVIEW
  Connectivity
  Checker

CATALOGUES
  Applications
  Resources

POLICY
  Needs
  Decisions
  Rules
  Effective
  Export

OPERATIONS
  Realization
```

Do not present implemented areas as Planned. Future navigation may appear only when backed by accepted scope, explicitly marked Planned and unable to perform fake actions or display fabricated data.

## Connectivity

Connectivity remains the normal resource-centric workspace.

Purpose: show Resources in the selected responsibility scope, bound Component Deployments, incoming/outgoing connectivity relationships, remote side, access semantics and independent Need/Decision/Policy state.

Canonical hierarchy:

```text
Resource
  -> Component Deployment
      -> Connectivity Relationship
```

Resources/Deployments with zero connectivity remain visible. Direction is relative to the local side. Human-readable DCS/service meaning leads; protocol/ports and stable IDs are secondary technical details.

Need, Decision, Policy and Realization must never be collapsed into one generic status.

Contextual Add connectivity reuses known local scope/resource/deployment and uses backend discovery for valid remote/DCS choices. The UI must not assemble arbitrary stable-ID combinations.

## Checker

Checker is the technical-entry workspace for a traffic tuple. It presents owner-preserving Resource/Application context, policy summaries, unordered Network Context candidates, stored configured Technical Access Evidence and Resource Responsibility/contact information.

It must preserve ambiguous/historical/unknown address resolution, missing evidence and candidate-set uncertainty. Candidate membership is not shown as a proven network path and configured evidence is not shown as authorization.

## Applications catalogue

Applications exposes the accepted hierarchy:

```text
Application
  -> Component
      -> Component Deployment
          -> Resource Bindings
          -> Directed Communication Specifications
```

Required current behavior:
- list/search Applications;
- create Application and drill into bookmarkable detail;
- create Components and Component Deployments under their accepted parents;
- discover existing Resources from backend data and create/end Deployment Resource Bindings;
- inspect current/historical bindings as provided by the backend;
- discover Active ACC participants for DCS authoring;
- create immutable DCS revisions from validated vendor-neutral protocol/service/port semantics;
- show stable IDs/provenance progressively, with readable labels/structure leading normal work.

Normal flows do not require the user to paste NAPMS-owned UUID combinations.

## Resources catalogue

Resources is a dense operational catalogue workspace over Resource Catalogue truth.

Required current behavior:
- server-backed paging and search;
- effective Responsibility Scope filter;
- search across Resource reference/display data and current responsibility/contact presentation;
- current-fact completeness indicators for realization, scope affiliation, responsibility and contact;
- create Resource and open bookmarkable Resource detail;
- rename/retire supported Resource identity state according to backend lifecycle semantics;
- create/replace endpoint realization versions without rewriting history;
- create/end Resource Scope Affiliations;
- create/end Resource Responsibility/contact assignments;
- represent missing current relations explicitly rather than hide/fabricate them.

Responsibility Scope and Person/Team values may currently be explicit external correlation references where no registry adapter exists. The UI must not imply that entering such a reference creates organization identity or action authority.

## Needs

Needs presents authoritative Connectivity Requirements and derived requirement-to-policy alignment. Readable participants/DCS lead; stable IDs/provenance remain available in detail. Requirement lifecycle remains `Active | Retired`; alignment remains `Covered | Uncovered | NotCurrent | Unknown`. `Uncovered` is never labelled Denied.

## Decisions

Decisions presents immutable final Connectivity Decisions `Allowed | NotAllowed` for admitted subjects/scopes. It supports direct recording, protected reason/evidence/provenance and explicit immutable supersession. No Pending/approval lifecycle is invented.

## Rules

Rules presents authoritative Access Rules admitted through their own read authority. Readable source/destination/DCS lead; IDs, governance scope, Decision correlation, operational state and effective windows are progressively disclosed. Rule state remains `Active | Inactive`.

## Effective and Export

Effective answers what desired policy applies for an authorized scope/time. Export exposes the normalized technical representation while preserving correlation, realization, DCS semantics, `asOf` and provenance. Neither surface invents configured/device state.

## Realization

Realization is an implemented read/operator workspace. It shows stage availability across desired policy, placement, configured evidence, reconciliation, rendering and available operation result. Missing inputs/history remain `NotAvailable`/`Unknown`; transport acceptance is never presented as semantic verification.

## Catalogue mutation UX

Forms must:
- use backend discovery for NAPMS-owned relationships;
- prevent accidental duplicate submission;
- keep backend/domain validation authoritative while performing obvious client-side structural validation;
- distinguish authorization, validation/conflict and transport failures;
- distinguish rename/retire, create-new-version, end-relation and immutable-revision behavior rather than flatten them into generic edit/delete;
- confirm destructive/history-ending actions when accidental execution is plausible;
- never trust client actor identity, provenance, command time or catalogue authority scope.

## Interaction and layout baseline

The UI remains desktop-first control-plane software with a dark collapsible sidebar, light working area, restrained accent, dense operational tables/forms and WCAG 2.2 AA target.

Potentially unbounded data uses server-side paging/filter/search where required; shareable query state belongs in the URL where reasonable. Loading, genuine empty, filtered-empty, authorization-limited and retryable-failure states are distinct. Status must not rely on color alone.

Responsive baseline:
- `>=1280px`: full desktop shell;
- `768..1279px`: compact/collapsed navigation and horizontally scrollable dense tables as needed;
- `<768px`: functional navigation/forms/details; mobile is not the primary optimization target.

## Non-goals

Current Web direction does not introduce:
- generic CMDB/application portfolio management;
- Company/Organization hierarchy solely to decorate Responsibility Scope references;
- automatic ownership/responsibility-to-authority mapping;
- fine-grained foreign catalogue visibility policy;
- bulk catalogue import/edit as the first workflow;
- vendor firewall configuration authoring inside catalogue forms;
- fabricated graph/path semantics;
- fake metrics/dashboard data;
- duplicated business truth in frontend state.
