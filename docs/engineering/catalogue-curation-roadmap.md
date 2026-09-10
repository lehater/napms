# Catalogue Curation Roadmap

Status: `I27 complete and absorbed`.

Date: 2026-09-10.

## Purpose

Record the completed I27 path that made the supported local NAPMS product self-service for Resource Catalogue and Application Communication Catalogue truth already consumed by Connectivity and related workflows.

Observable behavior is owned by `docs/requirements/catalogue-curation.md`. Current runtime truth is summarized in `docs/engineering/current-state.md`; architecture is owned by `docs/architecture/catalogue-curation-boundary.md` and `docs/architecture/current-architecture.md`.

## Completion summary

All ordered stages are complete:

| Stage | Outcome |
| --- | --- |
| C0 | ACC/RC tactical curation semantics, lifecycle, provenance, idempotency and DCS authoring contract accepted |
| C1 | explicit `CurateApplicationCatalogue` / `CurateResourceCatalogue` Authority actions implemented |
| C2 | Resource command/read slice implemented, including temporal realization/scope/responsibility maintenance |
| C3 | first-class `Application -> Component -> Component Deployment` hierarchy and commands implemented |
| C4 | immutable vendor-neutral DCS authoring implemented with Active participant discovery |
| C5 | additive PostgreSQL persistence/migrations, deterministic legacy backfill, concurrency/idempotency receipts implemented |
| C6 | authenticated task-oriented `/api/v1/catalogues/**` HTTP boundary implemented |
| C7 | Resources Web workspace implemented |
| C8 | Applications Web workspace implemented |
| C9 | fresh catalogue data proven through existing Connectivity/Requirement flow |
| C10 | acceptance, hardening and durable absorption completed |

## Accepted product boundary

I27 remains deliberately narrower than generic CMDB/application portfolio management.

```text
Resource Catalogue
  owns Resource + temporal realization/scope/responsibility facts

Application Communication Catalogue
  owns Application -> Component -> Deployment
  owns temporal Deployment Resource Binding
  owns immutable DCS revisions

Authority Management
  owns mutation admission
```

Catalogue visibility, selected Responsibility Scope, Resource Scope Affiliation, Resource Responsibility/contact, `ReadScopedConnectivity` and catalogue mutation authority remain independent concerns.

Responsibility Scope and Person/Team are external correlation references for this local-first slice; I27 does not introduce Company/Organization identity or directory ownership.

Historical identities/facts are retired/ended/replaced according to domain semantics rather than hard-deleted or rewritten for UI convenience.

## Acceptance evidence

The completed increment contains executable evidence for:
- RC/ACC domain/application lifecycle, temporal, validation, authority, concurrency and idempotency semantics;
- PostgreSQL migration replay, deterministic legacy parent backfill and transaction-failure policy;
- authenticated HTTP session/idempotency/validation/trust boundaries;
- backend discovery for normal cross-reference selection;
- Resource workspace paging/search/scope filtering/current completeness projection;
- Web Applications/Resources workflows;
- a fresh-data journey from catalogue curation through Scoped Connectivity to Connectivity Requirement state `Required`;
- authenticated catalogue read with mutation denied `403 CatalogueAuthorityDenied` and no persisted change when curation authority is absent;
- local demo hierarchy and authority assertions.

Pre-absorption hosted validation passed all repository gates on the I27 branch: core, PostgreSQL persistence, Web, harness, knowledge and Docker local runtime.

## Deferred candidates

The following remain outside I27 and require a new accepted requirement/target:
- bulk import/edit;
- external CMDB/application/directory synchronization;
- organization/company hierarchy management;
- delegated stewardship derived from a future explicit governance relation;
- fine-grained foreign catalogue visibility;
- arbitrary custom catalogue fields/tags;
- generic CMDB inventory;
- real provider/device discovery;
- catalogue approval workflow;
- rich graph visualization.

## Completion criterion

Satisfied: an admitted local user can onboard the minimum Resource + Application + Component + Deployment + Binding + DCS structure through supported Web/API use cases and immediately consume it in the existing Connectivity/access workflow; unauthorized mutation is backend-denied; existing stable identities and historical/immutable semantics remain correct.
