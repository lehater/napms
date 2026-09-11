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

Status: `implementation complete; awaiting architectural review` on branch `refactor/m4-platform-consolidation`.

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

Target moves:

```text
napms/runtime/auth.py
  -> napms/platform/auth/local.py
napms/runtime/enterprise_identity.py
  -> napms/platform/auth/enterprise_identity.py
napms/runtime/http_api.py
  -> napms/platform/http/api.py
napms/runtime/http_support.py
  -> napms/platform/http/support.py

napms/bootstrap/composition.py
  -> napms/platform/bootstrap/http_process.py
napms/bootstrap/config.py
  -> merge into napms/platform/bootstrap/config.py
napms/bootstrap/main.py
  -> napms/platform/bootstrap/main.py
napms/bootstrap/local_seed.py
  -> napms/platform/bootstrap/local_seed.py
napms/bootstrap/migrations.py
  -> napms/platform/database/cli.py
```

Update package entrypoints, all consumers/tests, CI/Compose references and architecture guards in the same milestone. Do not introduce compatibility shims unless a concrete integration need appears.

## Exit criteria

M4 closes when legacy top-level `napms.bootstrap` and `napms.runtime` are absent; process shell is fully under `napms.platform`; platform contains no authoritative feature/domain behavior; core code does not import platform; local/full/PostgreSQL checks pass; and the final M4 PR passes required hosted gates.

## Blockers

None.

## Next

Perform final M4 architectural review. Do not start M5 or create the PR before that review.
