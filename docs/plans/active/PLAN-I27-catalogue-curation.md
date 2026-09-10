# PLAN — I27 Catalogue Curation

Status: `selected / active planning`.

Date: 2026-09-10.

Owner requirement: `docs/requirements/catalogue-curation.md`.

Ordered roadmap: `docs/engineering/catalogue-curation-roadmap.md`.

## Objective

Close the supported-local product gap where Resource Catalogue and Application Communication Catalogue truth is persisted and consumed but normal users cannot curate that truth through supported product workflows.

Target end-to-end result:

```text
user creates access-domain Resources
    -> adds endpoint/scope/responsibility facts
    -> creates Application/Component/Deployment structure
    -> binds Deployment to Resource
    -> creates valid immutable DCS revision
    -> newly curated data appears in Connectivity
    -> existing Need/Decision/Rule workflow can consume it
```

## Why this increment is selected

Current product behavior demonstrates a concrete catalogue workflow need:

- Connectivity and Checker depend on RC/ACC data;
- demo/local catalogue facts are currently populated by seed/direct persistence mechanisms;
- Web has no `Applications` or `Resources` curation workspaces;
- ACC Strategic DDD owns Application/Component/Deployment/DCS identities, while current persistence/runtime starts largely at Component Deployment;
- current read authority/visibility semantics deliberately do not imply catalogue mutation.

The accepted trigger from `web-ui-requirements.md` — add catalogue workspaces only after concrete user workflows exist — is now satisfied by the local self-service onboarding workflow captured in the I27 requirement.

## Highest affected layers

This is not a Web-only change.

```text
Strategic DDD: mostly stable ownership
Tactical DDD: material ACC/RC write-model closure required
Requirements: new observable self-service behavior
Architecture: mutation/use-case/persistence/transport seams
Implementation: backend + PostgreSQL + Web
```

Use `docs/process/domain-change-protocol.md` and `docs/process/decision-protocol.md` for any newly discovered semantic conflict/unknown.

## P0 — blocking decisions before infrastructure

### P0.1 ACC tactical hierarchy

Resolve canonical Tactical DDD for:

```text
Application
  -> Component
      -> Component Deployment
```

Must decide:

- stable identity form for Application and Component;
- parent/containment invariants;
- whether Component Deployment parent identity is immutable;
- lifecycle/retirement semantics;
- display metadata versus identity;
- compatibility/migration for existing Component Deployment rows that currently have no persisted Application/Component parents.

Do not solve this by nullable foreign keys/UI-only grouping without an explicit migration/semantic rule.

### P0.2 Catalogue lifecycle and deletion

Select lifecycle semantics for locally curated catalogue identities/facts.

Constraint:

- downstream Requirements/Decisions/Rules/history may reference stable catalogue identities;
- destructive deletion must not silently invalidate historical business truth.

Prefer explicit retirement/end-of-validity/version replacement where the domain meaning supports it. Hard deletion is permitted only for facts whose accepted semantics and reference constraints make it safe.

### P0.3 Mutation authority

Define Authority Management actions and scope correlation for:

- Resource Catalogue curation;
- Application Communication Catalogue curation;
- DCS revision creation;
- temporal relation maintenance where different authority is justified.

Avoid one generic `Admin` action unless domain evidence demonstrates that all catalogue mutations share one responsibility boundary.

The selected model must preserve:

```text
catalogue visibility
!= Resource Responsibility
!= ReadScopedConnectivity
!= catalogue mutation authority
```

### P0.4 DCS user-authored contract

Define the supported input model for creating one immutable Directed Communication Specification revision.

The form/application contract must express application communication semantics and validate them server-side. It must not expose raw projection bytes or treat a firewall ACL editor as the ACC domain model.

### P0.5 Local provenance and command identity

Define how locally curated facts receive:

- stable identity/reference;
- provenance reference;
- effective time where applicable;
- idempotency/duplicate-submission behavior.

Avoid requiring users to manually manufacture internal provenance strings/UUIDs unless they are intentionally importing an external authoritative identity.

## P1 — implementation stages

### Stage 0 — canonical semantic closure

Deliverables:

- ACC Tactical DDD artifact under `docs/domain/`;
- Resource Catalogue write semantics added to the smallest owning canonical artifact;
- ubiquitous-language adjustments only where needed;
- authority actions documented in the owning domain/requirements layer;
- architecture delta for command/application/persistence composition;
- executable core tests describing selected invariants before infrastructure.

Exit criterion:

- all P0 decisions accepted;
- no unresolved semantic conflict blocks command implementation;
- `make knowledge-check` expected to remain satisfiable after canonical edits.

### Stage 1 — Authority Management

Implement selected catalogue mutation actions and admission tests.

Exit criterion:

- positive and negative authority behavior is executable;
- actor identity remains server owned;
- selected scope/subject semantics cannot be substituted by the caller.

### Stage 2 — Resource Catalogue Domain/Application/Ports

Implement the minimum task-oriented command/read set required by the Resources workflow.

Expected use-case responsibilities:

- register Resource;
- read/list/search Resources;
- add/end current realization version;
- add/end Resource Scope Affiliation;
- add/end Resource Responsibility assignment;
- expose trusted selection data to other catalogue forms.

Exact class/command names follow the accepted Tactical DDD rather than this plan text.

Tests first at Domain/Application level.

### Stage 3 — ACC Domain/Application/Ports

Implement/complete:

- Application and Component identities/relations;
- Component Deployment hierarchy relation;
- list/search/detail projections;
- create/retire semantics selected in Stage 0;
- Deployment Resource Binding command semantics;
- DCS immutable revision command.

Ensure existing Access Rule / Requirement identity triples continue using stable Component Deployment + DCS identities without semantic rewrite.

### Stage 4 — PostgreSQL migration/persistence

Only after Stages 0-3 contracts are stable.

Tasks:

- add Application/Component persistence required by selected model;
- migrate existing seeded Component Deployments deterministically according to accepted compatibility rule;
- implement command repositories for RC/ACC;
- preserve temporal constraints/history;
- implement optimistic/idempotent behavior selected in P0.5;
- prove migration replay/startup compatibility.

No generic repository `save-any-row` API.

### Stage 5 — HTTP API

Add authenticated task-oriented catalogue endpoints and DTOs.

Required API capabilities:

- list/search/detail read models;
- command routes for selected mutations;
- backend-owned discovery for Resource/Application/Component/Deployment/DCS form references;
- authority checks before mutation;
- explicit 4xx mapping for authorization, validation, missing reference and semantic conflict;
- no trusted `actorId` from request bodies.

Update `docs/engineering/http-api-contract.md` when route contracts stabilize.

### Stage 6 — Resources UI

Read `web/AGENTS.md` before implementation.

Add:

```text
CATALOGS
  Resources
```

Minimum screen flow:

```text
Resources list
  -> Resource detail
      -> identity/provenance
      -> endpoints/realizations
      -> scope affiliations
      -> responsibility/contact
      -> contextual mutations
```

First slice favors complete single-entity workflows over bulk editing.

### Stage 7 — Applications UI

Add:

```text
CATALOGS
  Applications
```

Minimum screen flow:

```text
Applications list
  -> Application
      -> Component
          -> Deployment
              -> Resource bindings
              -> DCS / communication specs
```

Provide create flows using backend discovery. Do not require users to paste UUIDs for normal relationships.

### Stage 8 — integration with existing product

Prove new data is immediately available through existing owner-preserving compositions.

At minimum:

- Resource appears in scope-focused Connectivity after effective affiliation;
- bound Component Deployment appears under the Resource;
- DCS interaction can become the subject of existing Add connectivity / Requirement flow;
- Checker/other read surfaces continue to preserve visibility/authority boundaries;
- existing demo seed remains usable.

### Stage 9 — acceptance and absorption

Run/tighten:

- focused domain/application tests;
- PostgreSQL integration/migration tests;
- authenticated HTTP tests;
- Web tests/build;
- `make test`;
- `make harness-check`;
- `make knowledge-check`;
- `make web-check`;
- Docker local runtime acceptance required by current repository practice.

Acceptance scenario must start from catalogue curation rather than pre-seeded business objects for the newly proven path.

After final gate:

- update `docs/engineering/current-state.md`;
- update `docs/architecture/current-architecture.md` if runtime structure changed materially;
- update `docs/requirements/web-ui-requirements.md` / `docs/ui/` to reflect implemented catalogue workspaces;
- mark roadmap complete;
- remove this PLAN and reset `docs/plans/active/README.md` after durable outcomes are absorbed.

## Candidate file impact

Expected backend areas:

```text
src/napms/application_catalogue/domain/
src/napms/application_catalogue/application/
src/napms/application_catalogue/adapters/postgres/
src/napms/resource_catalogue/domain/
src/napms/resource_catalogue/application/
src/napms/resource_catalogue/adapters/postgres/
src/napms/authority_management/
src/napms/runtime/http_api.py
src/napms/composition/
```

Expected Web areas:

```text
web/src/App.tsx
web/src/api.ts
web/src/components/layout/AppShell.tsx
web/src/features/resources/
web/src/features/applications/
```

Expected documentation owners:

```text
docs/domain/
docs/requirements/catalogue-curation.md
docs/requirements/web-ui-requirements.md
docs/architecture/current-architecture.md
docs/engineering/http-api-contract.md
docs/engineering/current-state.md
docs/ui/
```

The exact touched set follows semantic need; do not mechanically edit every listed artifact.

## Risk register

### P0 — UI drives accidental domain model

Risk: implementing `Applications` as a convenient nested frontend structure before resolving Application/Component identities creates schema/API semantics that conflict with Strategic DDD.

Control: Stage 0 closes Tactical DDD first.

### P0 — destructive editing breaks historical references

Risk: generic update/delete endpoints can invalidate Requirement/Decision/Rule provenance or historical interpretation.

Control: explicit lifecycle/version/end semantics; no generic hard-delete UX.

### P1 — authority collapses into ownership

Risk: selected scope, Resource Responsibility or visible catalogue data gets treated as write permission.

Control: explicit Authority Management mutation actions and negative acceptance tests.

### P1 — DCS becomes ACL editor

Risk: user-facing communication authoring leaks technical/vendor policy concerns into ACC.

Control: domain DCS input contract and immutable backend encoding.

### P1 — current seed becomes migration obstacle

Risk: existing deployments lack Application/Component parent rows.

Control: explicit deterministic compatibility/migration decision in P0.1 before schema change.

### P2 — scope/company hierarchy pressure

Risk: catalogue UI tries to solve company/org hierarchy because Responsibility Scope is currently an opaque reference.

Control: I27 only consumes existing Responsibility Scope references; organization hierarchy requires separate requirement/domain work.

### P2 — too much catalogue scope

Risk: feature expands into CMDB, bulk import, custom fields and external synchronization.

Control: acceptance journey remains the minimum access-domain onboarding flow.

## Definition of done

I27 is done when all are true:

- catalogue curation requirements are implemented without generic CMDB semantics;
- Application/Component/Deployment tactical hierarchy is canonical and persisted;
- RC and ACC mutation use cases are domain/application owned;
- mutation authority is explicit and backend-enforced;
- Resources and Applications workspaces support the minimum fresh-data journey;
- no direct SQL/seed edit is required to onboard the proven Resource/Application/DCS structure;
- newly curated data participates in existing Connectivity/access flow;
- historical/immutable identity semantics are preserved;
- required repository gates pass;
- durable outcomes are absorbed and this active PLAN is retired.