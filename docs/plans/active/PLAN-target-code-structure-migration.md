# PLAN — Target Code Structure Migration

Status: `active`

## Goal

Move NAPMS to the accepted final physical taxonomy without product/domain semantic change:

```text
backend/src/napms/
  contexts/
  workflows/
  platform/
```

## Inputs

- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`
- `docs/decisions/ADR-014-target-code-structure-taxonomy.md`

## Execution order

```text
M1 backend repository boundary
-> M2 bounded contexts + final Clean layers
-> M3 workflows + remove generic composition
-> M4 platform consolidation
-> M5 capability-oriented internals where justified
-> M6 Web final locality
-> M7 compatibility purge + final enforcement
```

## Completed milestones

- M1 — complete in `f0e281e`.
- M2 — complete in PR #74, squash merge `91eb009c2338697458ba3874836c93cc044f753a`.
- M3 — complete in PR #75, squash merge `18787e3f790368dec8d57078b47c7b6454e85b5d`; all required hosted gates passed.

## M4 — Platform consolidation

Status: `implementation and architectural review complete; final hosted PR gates pending` on branch `refactor/m4-platform-consolidation`.

Goal: remove legacy top-level `napms.bootstrap` and `napms.runtime`, leaving process/runtime mechanics only under `napms.platform`.

Accepted ownership:
- authentication/session and enterprise identity mechanics -> `platform/auth/`;
- generic HTTP shell, public HTTP support, correlation/error/logging/session endpoints -> `platform/http/`;
- executable assembly, process configuration and HTTP entrypoint -> `platform/bootstrap/`;
- migration runner and migration CLI -> `platform/database/`;
- existing M3 wiring modules already under `platform/bootstrap/` remain there;
- local demo seeding remains an explicit local-dev bootstrap utility; it is fixture/operational setup, not authoritative product/domain behavior;
- no context/workflow core may import platform;
- platform may depend outward on concrete context/workflow adapters for executable assembly but owns no feature/domain truth.

Implemented target:

```text
napms/platform/
  auth/
  bootstrap/
  database/
  http/
```

Legacy top-level `napms.bootstrap`, `napms.runtime`, and `napms.composition` are absent. Production package top level is only `contexts / workflows / platform` plus package metadata. Test taxonomy was aligned under `tests/platform` and old `tests/bootstrap`, `tests/runtime`, and `tests/composition` locations were removed.

Validation before final PR:
- targeted auth: 13 passed;
- platform + architecture: 183 passed;
- `make test`: 807 passed, 141 deselected;
- `make harness-check`: passed;
- `make knowledge-check`: passed;
- PostgreSQL 16 `make postgres-test`: 141 passed, no skipped;
- `docker compose config`: passed;
- `docker compose build`: passed.

Final architectural review confirms:
- `platform/http` imports no bounded context or workflow modules;
- feature HTTP wiring/error registration lives in `platform/bootstrap/http_process.py`;
- context domain/application and workflow application code do not import `napms.platform`;
- console entrypoints use final platform namespaces;
- process/runtime mechanics are fully consolidated under `napms.platform` without compatibility shims.

## Exit criteria

M4 closes when the final milestone PR passes all required hosted gates and is squash-merged to `main`.

## Blockers

None.

## Next

Open the final M4 milestone PR, run required hosted gates, and squash-merge if green. Do not start M5 or make material changes after the final gate without returning the PR to draft and gating again.
