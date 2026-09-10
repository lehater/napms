# PLAN — I27 Catalogue Curation

Status: `selected / active implementation`

Date: 2026-09-10.

Owner requirement: `docs/requirements/catalogue-curation.md`.

Ordered roadmap: `docs/engineering/catalogue-curation-roadmap.md`.

## Goal

Close the supported-local product gap where Resource Catalogue and Application Communication Catalogue truth is consumed by Connectivity and related workflows but cannot be curated through normal product paths.

Target journey:

```text
create Resources
    -> add realization / scope affiliation / responsibility
    -> create Application / Component / Deployment structure
    -> bind Deployments to Resources
    -> create immutable DCS
    -> observe the relationship in Connectivity
    -> declare the existing Connectivity Requirement / Need
```

The increment is catalogue curation for access-domain truth, not a generic CMDB/application portfolio product.

## Inputs

Canonical inputs:
- `docs/requirements/catalogue-curation.md` — observable I27 behavior and non-goals;
- `docs/domain/` — Resource Catalogue and ACC ownership/identity/lifecycle semantics;
- `docs/architecture/current-architecture.md` — dependency and composition boundaries;
- `docs/engineering/catalogue-curation-roadmap.md` — ordered I27 capability increments;
- `docs/engineering/catalogue-curation-http-api-contract.md` — selected `/api/v1/catalogues/**` transport contract;
- relevant I27 ADRs, especially external correlation reference handling.

Repository process inputs:
- root/scoped `AGENTS.md`;
- `docs/process/domain-change-protocol.md` and `docs/process/decision-protocol.md` when material truth is missing/conflicting;
- repository core/PostgreSQL/Web/harness/knowledge/docker gates.

## Semantic constraints

I27 preserves these distinctions:

```text
catalogue visibility
!= Resource Scope Affiliation
!= Resource Responsibility
!= ReadScopedConnectivity
!= catalogue mutation authority
```

Further constraints:
- Application, Component, Component Deployment and Resource are stable access-domain identities, not UI grouping keys;
- temporal realization/affiliation/responsibility/binding facts are created/ended/replaced rather than historically rewritten;
- DCS is immutable application-communication semantics, not a firewall-rule editor;
- NAPMS-owned cross-entity identities use backend discovery in normal UI paths;
- external Responsibility Scope / Person / Team correlation references follow ADR-011 and do not establish identity or authority;
- mutation actor, action time, authority context, generated identity/provenance and idempotency handling remain backend owned;
- existing Requirement/Decision/Rule semantic identities continue to use stable Component Deployment + DCS identities.

## Execution stages

### Stage 0 — semantic closure

Resolved and implemented:
- first-class `Application -> Component -> Component Deployment` Tactical DDD;
- Active/Retired lifecycle with auditable retirement provenance;
- temporal fact end/replacement provenance;
- separate `CurateApplicationCatalogue` and `CurateResourceCatalogue` authority actions;
- ACC-owned DCS authoring semantics;
- server-owned command identity/provenance/idempotency rules.

### Stage 1 — authority

Implemented:
- fail-closed owner-specific curation authority adapters;
- server-selected catalogue scopes `application-catalogue` and `resource-catalogue`;
- negative tests proving caller-selected scope/Resource Responsibility/read visibility do not grant curation authority.

### Stage 2 — Resource Catalogue core

Implemented Domain/Application/Ports for:
- Resource create/rename/retire;
- owner list/detail reads;
- realization create/replace;
- Resource Scope Affiliation create/end;
- Resource Responsibility create/end;
- optimistic concurrency, idempotency and audit/provenance rules.

### Stage 3 — Application Communication Catalogue core

Implemented Domain/Application/Ports for:
- Application/Component/Component Deployment create and lifecycle maintenance;
- owner hierarchy/detail/participant reads;
- immutable typed DCS revision creation;
- temporal Deployment Resource Binding create/end;
- cross-BC Resource target check through an RC-owned projection port.

### Stage 4 — PostgreSQL

Implemented additive persistence:
- Application/Component hierarchy and mandatory Deployment parent;
- deterministic compatibility backfill preserving existing Deployment/DCS identities;
- Resource lifecycle and temporal curation persistence;
- command receipts and optimistic versions;
- separate ACC/RC curation repositories;
- transaction policy distinguishing known pre-commit failure from ambiguous commit acknowledgement;
- migration replay/backfill tests and parent-aware legacy integration fixtures.

### Stage 5 — HTTP

Implemented task-oriented authenticated catalogue routes:
- catalogue list/detail/discovery/create operations;
- Resource realization replacement and scope/responsibility end operations;
- binding create/end;
- immutable DCS authoring with Active participant discovery;
- required `Idempotency-Key` for mutations;
- session actor/runtime action time and backend authority context;
- stable catalogue error mappings and 422 domain-validation safety net.

The selected contract is `docs/engineering/catalogue-curation-http-api-contract.md` and extends the base HTTP conventions.

### Stage 6 — Resources workspace

Implemented:
- `CATALOGUES -> Resources` navigation;
- paged/searchable create/list/detail workflow;
- effective Responsibility Scope filter;
- current responsibility/contact search;
- missing current realization/scope/responsibility/contact indicators;
- realization create/replace;
- scope affiliation create/end;
- responsibility/contact create/end.

### Stage 7 — Applications workspace

Implemented:
- `CATALOGUES -> Applications` navigation;
- Application list/create/detail;
- Component and Deployment creation;
- Resource discovery, binding and unbinding;
- DCS authoring through backend Active Application/Component/Deployment participant discovery;
- stable IDs remain secondary technical information rather than required manual relationship input.

### Stage 8 — existing-product integration

Executable evidence is present for:
- fresh Resource scope affiliation appearing in Scoped Connectivity;
- bound Deployment appearing under that Resource;
- newly curated DCS becoming the exact interaction consumed by existing Connectivity Requirement declaration;
- requirement state changing from no current Need to `Required` without direct catalogue SQL/seed edits;
- local demo hierarchy and curation authority remaining usable.

### Stage 9 — validation and absorption

Hosted gate iterations are in progress. Core/PostgreSQL/Web/knowledge/docker have reached green on the accumulated implementation; remaining harness-plan-format fixes are being applied under draft PR state and must be re-gated on the final head.

After a green implementation gate:
- absorb durable outcomes into current-state/architecture/UI owners where materially changed;
- mark `docs/engineering/catalogue-curation-roadmap.md` complete;
- remove this active PLAN after absorption;
- set `docs/plans/active/README.md` to the repository's no-active-plan form;
- re-run any gate required by material absorption changes;
- squash-merge PR #51 only after final green validation.

## Risks

### P0 — accidental CMDB expansion

Control: keep catalogue fields and workflows limited to access-domain identity, realization, responsibility, binding and communication semantics required by existing product flows.

### P0 — historical reference breakage

Control: stable identity plus retirement/end/replacement semantics; no generic hard delete or mutable DCS revision.

### P1 — ownership/visibility becomes authority

Control: dedicated Authority Management actions and negative backend acceptance.

### P1 — cross-context leakage

Control: consuming ports/adapters; ACC does not read Resource Catalogue tables directly for binding admission.

### P1 — migration compatibility

Control: additive migrations, immutable old migration checksums, deterministic orphan-only hierarchy backfill, preserved existing Deployment/DCS UUIDs and PostgreSQL integration coverage.

### P2 — external identity over-modeling

Control: ADR-011 keeps Responsibility Scope / Person / Team references external until an accepted registry/domain requirement exists.

## Exit criteria

I27 is complete only when all are true:
- Resources and Applications workspaces support the accepted fresh-data journey without direct catalogue SQL/seed edits;
- RC/ACC write semantics remain Domain/Application owned and PostgreSQL-backed;
- catalogue mutation authority is explicit, backend-enforced and separate from read visibility/responsibility/scope affiliation;
- historical/immutable identity semantics and existing downstream references are preserved;
- fresh curated data participates in Scoped Connectivity and existing Requirement/Need flow;
- read-allowed/mutation-denied acceptance passes;
- core, PostgreSQL persistence, Web, harness, knowledge and local Docker runtime gates are green on the final implementation head;
- durable documentation/current-state is absorbed and active execution artifacts are retired according to repository process.

## Blockers

No unresolved product/domain blocker is known.

Current blocker is repository validation only: the active plan/capsule must satisfy the current harness schema and the resulting final head must pass the hosted gates.

## Next

1. Keep PR #51 draft while this plan-schema correction is committed.
2. Mark PR #51 ready again and inspect all hosted workflows on the new head SHA.
3. Fix any remaining executable gate failure under draft state and re-gate.
4. After an all-green implementation gate, perform Stage 9 durable-state absorption and retire active execution artifacts.
5. Run any final gate required after absorption, then squash-merge PR #51.
