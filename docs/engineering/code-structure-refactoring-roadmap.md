# Code Structure Refactoring Roadmap

Status: `historical / superseded structural snapshot; completed through I32`.

Date: 2026-09-11.

This document records the repository state reached after I32. Its references to `napms.bootstrap`, root `web/src/api.ts`, root `App.tsx` and the former `adapters/` taxonomy are historical and must not be used as current architecture guidance. The current structure is defined by `docs/architecture/code-structure.md` and `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.

## Purpose

Align the physical repository structure with the accepted context-first modular-monolith / Clean Architecture / ports-and-adapters model, improving code locality for humans and agents without changing product/domain semantics.

Current architecture successor: `docs/architecture/code-structure.md` and ADR-014.

## Completion result

| Stage | Integration | Durable outcome |
| --- | --- | --- |
| M0 | PR #64 | canonical code-structure contract, roadmap and executable architecture/planning guards |
| M1-M4 | PR #65 (`a90b866`) | feature HTTP moved beside semantic owners; active runtime HTTP reduced to process assembly; `napms.bootstrap` established as the executable composition root; composition/config ownership made explicit |
| M5 | PR #66 (`62c77f6`) | demonstrated ACC Application/Component mutation hotspot split by responsibility; no second backend split selected merely by size |
| M6 Requirements | PR #67 (`e59bb4d`) | Connectivity Requirements Web API implementation localized under `features/requirements` |
| M6 Decisions | PR #68 (`a8eb8c0`) | Connectivity Decisions Web API implementation localized under `features/decisions` |
| M6 Rules | PR #69 (`e38ffb3`) | Access Rules Web query/mutation/detail implementation localized under `features/rules`; shared `RuleDto` intentionally remains shared |
| M6 final | PR #70 | Policy and scoped Connectivity Web API implementation localized under their feature owners; I32 active execution cleared |

## Durable backend structure

The bounded context remains the primary physical axis, with Clean/Hexagonal layers inside it:

```text
backend/src/napms/<semantic-owner>/
  domain/
  application/
  adapters/
    http/        # when the owner exposes HTTP
    postgres/    # when the owner owns persistence adapters
```

Process bootstrap/wiring is separate from semantic modules. `napms.bootstrap` is the executable composition root. Cross-context read/application compositions remain explicitly outside bounded-context persistence ownership where required; they are not mechanically moved into a peer adapter package.

`runtime/` is not a feature-code container. Process-level HTTP/error/session/readiness concerns may remain process-level when genuinely cross-cutting.

M5 confirmed that size alone is not a split criterion. `application_catalogue.application.structure_curation` had real Application-vs-Component change coupling and was split; `deployment_curation` and `binding_curation` were evaluated and retained because each is cohesive around one lifecycle responsibility.

## Durable Web structure

The Web UI remains feature-first:

```text
web/src/features/<feature>/
  api.ts         # feature-specific HTTP DTO/query/command implementation when present
  model.ts       # feature-local model when useful
  components/
  pages / feature entry components

web/src/lib/     # genuinely shared technical utilities
web/src/components/ui/  # reusable visual primitives
```

The root `web/src/api.ts` is now a compatibility/shared boundary rather than the owner of Requirements, Decisions, Rules, Policy or scoped Connectivity endpoint implementations. It intentionally retains:
- genuinely cross-feature DTOs such as proposal/catalogue interaction shapes and `RuleDto` where multiple features consume them;
- authentication/session operations used by root application bootstrap/logout orchestration;
- Access Rule proposal capability because it is consumed by both the Proposals and Connectivity flows;
- compatibility re-exports so existing pages do not require unrelated churn during structural migration.

`App.tsx` remains the root route/application composition surface. Its size alone is not evidence that feature ownership is misplaced.

Executable locality tests prevent localized feature endpoint implementation from drifting back into the root API facade.

## Validation

Each structural slice preserved product/domain semantics and was accepted only with the applicable hosted gates. The final I32 completion head is required to pass:
- Core;
- Web build;
- Harness;
- Docker local runtime;
- browser journey.

Earlier M1-M5 slices additionally used the applicable PostgreSQL/integration/architecture gates for their backend scope.

## Non-goals retained

I32 did not:
- change DDD semantic ownership or bounded-context identities;
- introduce microservices or per-context deployments/databases;
- change API behavior merely to fit folders;
- rewrite persistence models;
- introduce global technical-layer directories or `backend/src/napms/modules/`;
- split files based on a numeric size threshold;
- force genuinely shared/application-level Web responsibilities under a single feature.

## Completion criterion

Satisfied. Feature code is discoverable from semantic owners; runtime/bootstrap is assembly-oriented rather than a feature-code container; architecture/locality tests protect the boundaries; current product journeys remain unchanged; remaining large files are either locally coherent or require new evidence before further refactoring.

Future structural work requires a new selected architecture/engineering increment with concrete locality or ownership evidence rather than continuation of I32 by inertia.
