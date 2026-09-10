# Catalogue Curation Roadmap

Status: `I27 selected / planning`.

Date: 2026-09-10.

## Purpose

Provide the ordered implementation path that makes the supported local NAPMS product self-service for the Resource Catalogue and Application Communication Catalogue truth already consumed by Connectivity and related workflows.

Accepted observable behavior is owned by `docs/requirements/catalogue-curation.md`.

I27 is not generic catalogue CRUD. It completes owner-controlled domain/application mutation seams first and exposes task-oriented Web workflows only after the semantic model is closed.

## Starting state

Known current state:

- Resource Catalogue persists Resource identities, endpoint/realization history and Resource Scope Affiliation; I26 also established Resource Responsibility read semantics;
- Application Communication Catalogue persists Component Deployments, DCS revisions and Deployment Resource Bindings;
- Strategic DDD already assigns Application/Component/Deployment/DCS identities to ACC;
- normal local catalogue population still depends on seed/direct persistence paths rather than supported user-facing mutation use cases;
- Web currently consumes catalogue truth through Connectivity, Checker and other projections but has no Applications or Resources curation workspace;
- `ReadScopedConnectivity`, catalogue read visibility and Resource Responsibility do not imply catalogue mutation authority.

## Ordered roadmap

### C0 — Domain re-entry and catalogue mutation contract

Resolve the blocking semantic decisions before opening infrastructure work.

Deliverables:

- ACC Tactical DDD for Application, Component, Component Deployment, DCS revision and Deployment Resource Binding;
- explicit identity and lifecycle rules, including how retirement/replacement works and what is immutable;
- Resource Catalogue write semantics for Resource identity, realization versions, Resource Scope Affiliation and Resource Responsibility;
- catalogue mutation authority model and scope correlation;
- local curation provenance and command/idempotency semantics;
- accepted DCS authoring input model separated from normalized firewall-rule representation;
- updates to ubiquitous language/semantic ownership only where the clarified tactical model requires them.

Gate:

- no PostgreSQL migration, HTTP write route or Web mutation form before these decisions are canonical and knowledge checks are satisfiable.

### C1 — Authority Management mutation actions

Implement explicit catalogue mutation actions selected by C0.

Requirements:

- actor identity remains server/session owned;
- Resource and ACC actions are independently admitted according to the accepted granularity;
- read visibility, responsibility/contact and `ReadScopedConnectivity` do not confer write authority;
- tests prove allow/deny, effective-time and scope behavior.

### C2 — Resource Catalogue command/use-case slice

Implement Domain/Application/Ports for supported local Resource curation.

Minimum application capabilities:

- register Resource identity;
- read Resource detail/current projection;
- add/end/replace Resource realization versions according to C0 semantics;
- add/end Resource Scope Affiliations;
- add/end Resource Responsibility assignments;
- list/search data needed by the Resources workspace and selection forms.

Preserve temporal history rather than implementing generic row updates.

### C3 — Application Communication Catalogue hierarchy and command slice

Complete ACC tactical/runtime support for the accepted hierarchy:

```text
Application
  -> Component
      -> Component Deployment
```

Minimum application capabilities:

- register and inspect Application;
- register and inspect Component within its accepted parent relation;
- register and inspect Component Deployment;
- list/search hierarchy for UI discovery;
- maintain time-qualified Deployment Resource Bindings;
- preserve stable identities referenced by existing Requirement/Decision/Rule semantics.

This stage closes the current gap where persisted runtime starts at Component Deployment while Strategic DDD already owns Application and Component identities.

### C4 — DCS authoring and immutable revision commands

Implement one safe local user-authored DCS path.

The path shall:

- select supported source/destination participants through ACC-owned discovery;
- accept validated service/protocol/port semantics selected in C0;
- encode the existing immutable projection payload behind the application boundary;
- create a new immutable DCS revision rather than rewrite referenced truth;
- provide label/display metadata without making labels identity.

Do not expose raw projection bytes or normalized vendor/firewall rule editing as the primary authoring model.

### C5 — PostgreSQL persistence and migrations

Open the infrastructure gate only after C0-C4 domain/application contracts are tested.

Implement module-owned persistence for the selected write model:

- Resource Catalogue repositories/migrations as required by new command seams;
- ACC Application/Component persistence and parent relations;
- any lifecycle/version/provenance/idempotency persistence selected by C0;
- constraints that preserve temporal/reference invariants;
- migration compatibility with existing local seeded data.

Existing Component Deployment/DCS/binding identities must remain readable and migratable without silent semantic rebinding.

### C6 — Authenticated task-oriented HTTP API

Expose catalogue application use cases through authenticated routes.

Requirements:

- transport DTOs only;
- backend authority checks on every mutation;
- server-backed paging/search/discovery;
- explicit domain/authorization/conflict/transport error mapping;
- task-oriented commands instead of generic table CRUD;
- no caller-supplied trusted actor identity;
- form discovery endpoints/read models prevent the Web client from assembling arbitrary cross-context IDs.

### C7 — Resources Web workspace

Add `CATALOGS -> Resources` to the normal product shell.

First end-to-end UI slice:

- paged/searchable Resource list;
- Resource detail;
- register Resource;
- maintain endpoint/realization history;
- maintain Responsibility Scope affiliations;
- maintain Resource Responsibility/contact assignments;
- render missing current relations explicitly;
- hide/disable mutation affordances according to backend capability hints where useful, while relying on backend enforcement.

The screen remains a Resource Catalogue workflow, not a generic asset-management UI.

### C8 — Applications Web workspace

Add `CATALOGS -> Applications`.

First end-to-end UI slice:

- Application list/search;
- Application -> Component -> Deployment drill-down;
- create supported hierarchy entities;
- bind deployments to Resources through trusted discovery;
- inspect bindings and DCS revisions;
- create a supported immutable DCS revision through a validated form.

Stable IDs/provenance remain available in details but human-readable names/structure lead the normal workflow.

### C9 — Connectivity integration and fresh-data journey

Prove that freshly curated catalogue data feeds the existing product without a parallel projection or manual seed editing.

Journey:

```text
Resources / Applications curation
    -> Deployment Resource Binding
    -> DCS revision
    -> Connectivity inventory
    -> Add connectivity / Needs
    -> existing Decision / Rule path
```

Requirements:

- Connectivity sees newly curated effective Resources/Deployments through existing owner-preserving composition;
- no Web-only duplicate catalogue truth is introduced;
- current local demo seed may remain for immediate startup/demo, but the same semantic structure can be recreated through supported product workflows.

### C10 — Acceptance, hardening and absorption

Acceptance must cover:

- fresh PostgreSQL volume;
- authenticated admitted curation path for both catalogues;
- denied mutation for an authenticated actor lacking the selected authority;
- temporal replacement/end semantics where applicable;
- migration/startup compatibility with current demo seed;
- full fresh-data journey into Connectivity and one existing access workflow;
- backend/core tests, PostgreSQL integration, Web check, harness/knowledge checks and Docker local runtime gate.

After completion:

- absorb durable semantic truth into domain/requirements/architecture/current-state/UI owners;
- mark this roadmap complete;
- remove the active PLAN after absorption according to repository policy.

## Dependency sequence

```text
C0 semantic closure
  -> C1 authority contract
  -> C2 Resource commands
  -> C3 ACC hierarchy/commands
  -> C4 DCS commands
  -> C5 persistence
  -> C6 HTTP
  -> C7 Resources UI
  -> C8 Applications UI
  -> C9 existing-workflow integration
  -> C10 acceptance/absorption
```

C2-C4 may be implemented as separate coherent code stages after C0/C1, but infrastructure remains downstream from their accepted contracts.

## Product constraints

- Local-first remains the selected target.
- PostgreSQL remains the supported local catalogue source of truth.
- No external CMDB/application registry/directory integration is required.
- No real firewall/network lab is required.
- Responsibility Scope remains an opaque correlation reference in I27; do not invent Company/Organization hierarchy.
- Resource Responsibility is operational/contact truth, not authority.
- Catalogue visibility is independent from catalogue mutation authority.
- Existing Requirement/Decision/Rule semantic identities must not be rewritten by catalogue curation.
- Historical/immutable catalogue facts must not be implemented as destructive scalar CRUD merely for UI convenience.

## Explicit deferred candidates

The following do not block I27 and require a later concrete requirement:

- bulk import/edit;
- external source synchronization;
- organization/company hierarchy management;
- fine-grained foreign catalogue visibility;
- arbitrary custom fields/tags;
- generic CMDB inventory;
- real provider/device discovery;
- catalogue approval workflow;
- rich graph visualization.

## Completion criterion

I27 is complete when a local user with the proper authority can onboard the minimum Resource + Application + Deployment + Binding + DCS structure through supported Web/API use cases and immediately use that truth in the existing Connectivity/access-policy journey, while unauthorized mutation is backend-denied and historical/semantic identities remain correct.