# Code Structure Refactoring Roadmap

Status: `selected for I32 execution`.

Date: 2026-09-11.

## Purpose

Incrementally align the physical repository structure with the already accepted modular-monolith / Clean Architecture / ports-and-adapters model, improving code locality for humans and agents without changing product/domain semantics.

Architecture contract: `docs/architecture/code-structure.md`.

## Drivers

Current code already preserves strong semantic modules and inward dependency rules, but outer-layer code is harder to navigate than the architecture implies:

- feature HTTP is split between a very large `runtime/http_api.py` and many feature-specific `runtime/*_http.py` files;
- I31 added additional Catalogue HTTP surface under `runtime/`, increasing that concentration;
- executable composition is divided between `runtime/composition.py` and `composition/*`;
- frontend feature-first direction is sound, but several large page/API files remain later locality hotspots.

The roadmap therefore fixes ownership/locality before file-size cleanup.

## Ordered stages

| Stage | Outcome | Gate |
| --- | --- | --- |
| M0 | canonical code-structure contract, roadmap and active Harness state | harness + knowledge/document consistency |
| M1 | Application Catalogue target HTTP pilot moved from `runtime/` to ACC-owned HTTP adapters; executable boundary guard added | core + PostgreSQL + relevant HTTP/E2E + harness/knowledge |
| M2 | remaining Catalogue HTTP distributed to ACC/RC or explicit composition owners | core + PostgreSQL + relevant Web/E2E + architecture gates |
| M3 | `runtime/http_api.py` decomposed incrementally by semantic owner/read composition until it owns only cross-cutting process HTTP concerns | core + affected integration/E2E gates |
| M4 | runtime/composition/config responsibilities inventoried and consolidated into a small process/bootstrap surface; cross-context query compositions remain explicitly owner-preserving | core + PostgreSQL + Docker/runtime + architecture gates |
| M5 | demonstrated backend locality hotspots decomposed by use case/responsibility, not by arbitrary size threshold | affected core/PostgreSQL gates |
| M6 | demonstrated Web hotspots aligned with existing feature-local API/model/component/page structure | Web + relevant browser journeys |

Each stage is independently reviewable and may revise later stages if evidence shows the proposed target does not improve locality.

## M0 — architecture and execution contract

Responsibility: make the target and migration constraints durable before moving production code.

Outputs:
- `docs/architecture/code-structure.md`;
- this roadmap;
- selected I32 active plan and resume capsule;
- architecture/plans navigation updated;
- explicit statement that architecture/engineering maintenance increments may be selected without inventing a product/domain change when semantics are intentionally unchanged.

Local exit: repository truth and Harness recovery state agree on the target, M1 pilot, gates and non-goals.

## M1 — Application Catalogue HTTP pilot

Responsibility: prove that moving feature HTTP beside its semantic owner improves locality without behavior change.

Initial slice:

```text
src/napms/runtime/catalogue_target_http.py
src/napms/runtime/catalogue_target_retirement_http.py
  -> src/napms/application_catalogue/adapters/http/
```

Outputs:
- imports/tests updated with no API contract change;
- `runtime/composition.py` only assembles the migrated router factories;
- architecture test prevents ACC Domain/Application from depending on HTTP and prevents new ACC target HTTP ownership from returning to `runtime/`;
- existing target-authored J01/downstream acceptance remains green.

Local exit: same observable behavior, no semantic/persistence ownership change, and the next ACC HTTP change can be located from `application_catalogue/` without scanning `runtime/`.

Decision after M1: continue M2 only if the pilot reduces search/ownership ambiguity without creating compensating indirection.

## M2 — Catalogue HTTP completion

Responsibility: remove Catalogue feature ownership from the process runtime package.

Candidates are classified before moving:
- ACC-owned HTTP -> `application_catalogue/adapters/http/`;
- RC-owned HTTP -> `resource_catalogue/adapters/http/`;
- true cross-context/read-composition HTTP -> the explicit composition owner, not arbitrarily into ACC or RC.

Local exit: `runtime/` contains no Catalogue feature endpoint implementation.

## M3 — general HTTP decomposition

Responsibility: dismantle cross-context ownership in `runtime/http_api.py` one coherent slice at a time.

Order is chosen from current dependency/usage evidence; no all-at-once rewrite. Shared process concerns such as authentication/session plumbing, correlation/error envelope policy and readiness may remain process-level when they are genuinely cross-cutting.

Local exit: feature endpoints and feature DTO/mapping logic are owned by their semantic module/composition; the process HTTP surface is small and assembly-oriented.

## M4 — bootstrap/composition cleanup

Responsibility: remove ambiguity between `runtime/composition.py`, `composition/*` and duplicated configuration surfaces.

Before moving files, classify each item as:
- process bootstrap/wiring;
- module adapter;
- explicit cross-context read/application composition;
- migration/seed operational helper.

Only process assembly/configuration moves toward `bootstrap/`. Accepted cross-context read composition must remain visibly outside bounded-context persistence ownership where required.

Local exit: one obvious executable composition root; no misleading owner placement; Docker/local startup and migrations remain unchanged behaviorally.

## M5 — backend granularity

Responsibility: reduce files that demonstrably force unrelated use cases into the same editing/search context.

Candidates include large ACC application/repository files and any other hotspots discovered after M1-M4. Split by use case, aggregate responsibility or adapter role. Do not create generic services/helpers solely to shrink files.

Local exit: each split reduces change coupling and keeps inward dependency direction intact.

## M6 — Web locality

Responsibility: apply the already accepted feature-first Web rule to demonstrated hotspots.

Candidates include root `App.tsx`/`api.ts` responsibilities and large feature pages. Prefer feature-local `api`, `model`, `components`, `pages`; preserve `components/ui` and shared technical `lib` only for demonstrated reuse.

Local exit: representative feature changes remain feature-local and current browser journeys stay green.

## Non-goals

I32 does not:
- change DDD semantic ownership or bounded-context identities;
- introduce microservices or per-context deployments/databases;
- change current API behavior merely to fit folders;
- rewrite persistence models;
- remove legacy business truth;
- introduce global technical-layer directories;
- add `src/napms/modules/`;
- split files based on a numeric size rule alone.

## Completion criterion

I32 is complete when feature code is reliably discoverable from its semantic owner, runtime/bootstrap is assembly-oriented rather than a feature-code container, architecture tests protect the new boundaries, current product journeys remain unchanged, and remaining large files are either locally coherent or explicitly deferred with evidence.
