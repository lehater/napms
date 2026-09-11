# Target Code Structure Migration Roadmap

Status: `completed through M7`.

Date: 2026-09-11.

Architecture decision: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.
Canonical current structure: `docs/architecture/code-structure.md`.

This roadmap is retained as migration history. It no longer defines active work or current architecture.

## Goal

Move NAPMS to the final physical taxonomy without product/domain semantic change:

```text
backend/src/napms/
  contexts/
  workflows/
  platform/

web/src/
  app/
  features/
  components/ui/
  lib/
```

## Completed sequence

### M0 — Canonical target and execution state

ADR-014, the canonical code-structure contract, migration roadmap and execution plan were established before production moves began.

### M1 — Repository backend boundary

Python packaging, backend tests and Docker ownership moved under `backend/` while the root Makefile remained the stable repository command surface.

### M2 — Bounded contexts to final paths

All accepted bounded contexts moved under `backend/src/napms/contexts/<context>/` with context-local `domain / application / infrastructure / presentation` layers as applicable. Legacy top-level context packages were removed.

### M3 — Workflows and generic composition removal

The five accepted cross-context orchestrations moved under `workflows/`. Generic `composition/` was drained into workflow/context infrastructure or process bootstrap ownership and then removed.

### M4 — Platform consolidation

Process concerns moved under `platform/bootstrap`, `platform/auth`, `platform/database` and `platform/http`. Legacy top-level `bootstrap/` and `runtime/` packages were removed. A follow-up CI path-filter correction ensured future context migrations/changes trigger the appropriate hosted gates.

### M5 — Capability-oriented internals

Application Catalogue was split where change-locality evidence justified `curation / discovery / target`. Resource Catalogue was deliberately left unsplit because its responsibilities were not independent enough to justify additional package boundaries.

### M6 — Web final locality

The Web application converged on `app / features / components/ui / lib`. Root `api.ts`, root application files and feature-specific root components were removed; semantic DTO/API ownership became feature-local.

### M7 — Compatibility purge and final enforcement

Structural migration compatibility debt was removed:
- the pre-M5 Application Catalogue curation facade was deleted;
- transitional dependency-port fallbacks were removed in favor of final summary/page contracts;
- vacuous legacy structure checks were replaced by generic taxonomy enforcement;
- canonical architecture documentation was aligned with the actual repository.

Accepted product/domain compatibility behavior, including the ACC compatibility projection and transactional dependency recheck, was intentionally preserved.

## Final enforcement

Executable architecture tests protect at least:
- backend top-level taxonomy `contexts / workflows / platform`;
- context/workflow layer locality;
- absence of generic `adapters/` and `composition/` buckets;
- Clean Architecture dependency direction;
- bounded-context isolation and application-contract-based cross-context interaction;
- context-owned PostgreSQL schema isolation;
- workflow persistence boundaries;
- generic `platform/http` ownership;
- Application Catalogue capability boundaries;
- Web source locality and absence of the former root API facade.

## Validation

Each milestone was integrated only after its applicable local and hosted gates passed. The final migration exit requires backend, Web, Harness, Knowledge, PostgreSQL, Docker/runtime and browser-journey validation as applicable to the closing PR.

For all new work, use `docs/architecture/code-structure.md` and ADR-014 rather than this historical migration sequence.
