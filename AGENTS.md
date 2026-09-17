# NAPMS repository agent map

## Purpose

This repository contains the canonical NAPMS design specification plus implementation and executable evidence. Current design truth is owned by accepted anchors under `docs-v2/`; the old `docs/` tree is retired migration evidence and is not a competing source of truth.

## Task-first startup

Start from the explicit user task and load only the context required to perform it safely.

For non-trivial design, architecture, implementation-planning or Harness work:
1. read this file;
2. read `docs-v2/meta/workstream-state.yaml`;
3. read `docs-v2/meta/roadmap.yaml` when lifecycle/program context is required;
4. load only directly applicable `docs-v2/spec/**` contracts and accepted design anchors;
5. follow semantic references for affected truth rather than scanning implementation or retired documentation.

The durable workstream state, not chat history, determines where design work resumes.

## Source of truth

- `docs-v2/migration/revalidated/` — canonical accepted/revalidated NAPMS design anchors and validation evidence.
- `docs-v2/spec/` — Documentation System / Harness contracts.
- `docs-v2/meta/` — roadmap and durable workstream/process state.
- `docs-v2/horizontal/` and migration material — supporting retained redesign/migration evidence or projections; accepted anchors remain authoritative for owned semantics.
- `docs/` — RETIRED, frozen pre-cutover migration evidence only; never use it to override accepted `docs-v2/` truth and do not write new design truth there.
- `backend/src/` + `backend/tests/` — backend implementation and executable evidence, not product/domain/architecture design authority.
- `web/` — frontend implementation/evidence; apply its scoped instructions when authorized frontend implementation work is performed.
- `.github/workflows/` — executable hosted CI gates and their exact triggers/commands.

## Design and implementation discipline

Never invent product/domain truth to make implementation convenient. A Bounded Context is not automatically a service, database, team or deployment unit.

The accepted first-MVP design currently reaches G4 implementation readiness, but implementation readiness is not implementation authorization. Before changing production code or product tests, verify explicit authorization for that exact work. Product code/tests must not be used to reconstruct missing product, domain or architecture semantics.

Preserve accepted architecture unless an explicit design change or contradictory evidence reopens affected anchors: browser frontend, one HTTP/JSON OpenAPI application boundary, modular-monolith backend with in-process module contracts, one PostgreSQL database with module-owned persistence, and backend session identity plus Authority Management admission.

## Documentation changes

Write current design truth only under `docs-v2/`. Preserve semantic ownership and derivation links, revalidate changed/affected design, and keep Harness bookkeeping internal unless it is independently meaningful to design.

Do not reverse-sync accepted corrections into retired `docs/`. Historical provenance belongs in Git history or explicitly marked migration evidence, not in a second current truth store.

## Change discipline

- Never commit directly to `main`; work on a branch and integrate through a PR using squash merge.
- Merge remains a separately authorized action.
- Inspect applicable workflow commands and run/job status before claiming hosted CI PASS.
- Prefer the smallest validation matching the touched area.

## Architecture guardrails

- dependencies point inward: Domain <- Application/Ports <- Adapters/Composition;
- Domain has no framework, database, transport, configuration, logging or DI-container dependencies;
- Application consumes explicit ports owned by the consuming module;
- constructor injection; no service locator/global mutable dependency registry;
- business provenance is domain truth; operational logs do not replace it;
- technical realization changes do not silently redefine domain identity.
