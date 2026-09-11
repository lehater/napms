# NAPMS repository agent map

## Purpose

This repository is the source of truth for the new **Network Access Policy Management System (NAPMS)** product.

Legacy/reconstruction evidence lives outside this repository and does not define target behavior.

## Progressive startup

Do not preload the whole repository. Conversation history is execution history, not project state.

For non-trivial work read, in order:
1. this file;
2. `docs/plans/active/README.md` as the compact resume capsule;
3. the nearest scoped `AGENTS.md`;
4. the smallest applicable Skill under `.agents/skills/`;
5. only the canonical artifacts and code named by the capsule/current task.

Read the full current `PLAN-*.md` only when the task concerns planning/coordination/stage transition, the resume capsule explicitly directs you there, or a material fact required for the current task is missing. Do not load future work packages by default.

The resume capsule is a non-authoritative recovery cache. If a capsule summary conflicts with its canonical domain/requirements/architecture/engineering owner, the canonical owner wins and the capsule must be refreshed.

Do not scan `docs/baseline/` or completed historical Wave-1 material unless the task explicitly requires history or provenance.

Use `docs/process/decision-protocol.md` when a material answer is missing or conflicting.

## Source-of-truth map

- `docs/domain/` — living Strategic/Tactical DDD.
- `docs/requirements/` — accepted product behavior, quality and semantic contracts.
- `docs/architecture/` — current target architecture and ownership constraints.
- `docs/decisions/` — consequential ADRs.
- `docs/engineering/` — implementation contracts/policies and engineering state.
- `docs/ui/` — current implementation-oriented UI guidance derived from accepted requirements.
- `docs/plans/active/` — current execution state only.
- `docs/process/` — reusable repository working protocols.
- `docs/baseline/` — accepted snapshots/provenance; not the normal edit target.
- `backend/src/` + `backend/tests/` — backend implementation and executable evidence.
- `web/` — React outer adapter; apply `web/AGENTS.md` before Web UI work.
- `.github/workflows/` — executable hosted CI gates and their exact triggers/commands.

When layers disagree materially, do not silently choose the code. Resolve the highest affected canonical truth first.

## Change discipline

- Agents/chats must not commit directly to `main`.
- Work on a branch; checkpoint/WIP/fixup commits are allowed there.
- Integrate one coherent semantic stage through a PR using **squash merge**.
- Keep the PR draft while work is accumulating. Mark it ready only for the final CI gate.
- Ordinary branch pushes must not trigger hosted Actions.
- If material changes are required after the final PR gate, return the PR to draft and gate again when ready.
- Git history is the archive for completed plans/superseded working artifacts.

## CI execution map

Repository CI is part of the Harness execution surface, not hidden repository plumbing.

- Before claiming a required check cannot be executed, inspect the applicable workflow under `.github/workflows/` and its exact command/trigger.
- The current hosted gates are intentionally trigger-controlled; do not assume every push or squash runs them.
- `Ready for review` requests the final hosted PR gate for affected paths.
- Workflows that expose `workflow_dispatch` may be used as an intermediate deterministic execution fallback when the current agent environment cannot run the same repository-local command.
- Prefer local checks during the editing loop when available; do not toggle Draft/Ready merely to obtain an intermediate run.
- When hosted CI is used as evidence, inspect the resulting run/job status and relevant logs before claiming the gate passed.
- If the connected GitHub capability cannot dispatch a new workflow, state that capability gap explicitly rather than treating CI as absent.

See `docs/process/working-loop.md` for the local-vs-hosted validation loop.

## No-invention / domain re-entry

Never invent unsupported product/domain truth to make implementation convenient.

Use:
- `docs/process/decision-protocol.md` for known/hypothesis/unknown/conflict handling;
- `docs/process/domain-change-protocol.md` when code/new requirements may change accepted behavior, Tactical DDD, Strategic DDD or architecture.

A Bounded Context is not automatically a service, database, team or deployment unit.

## Architecture guardrails

- Modular application; explicit semantic modules and ports/adapters.
- Dependencies point inward: Domain <- Application/Ports <- Adapters/Composition.
- Domain has no framework, database, transport, configuration, logging or DI-container dependencies.
- Application consumes explicit ports owned by the consuming module.
- Constructor injection; no service locator/global mutable dependency registry.
- Business audit/provenance is domain truth; operational logs do not replace it.
- Technical realization changes do not silently redefine domain identity.

## Implementation order

For accepted behavior:
1. Domain + Application + Ports;
2. core/architecture tests;
3. core gate;
4. infrastructure only when the active plan permits it;
5. integration/acceptance proof.

The current plan owns whether the infrastructure gate is open or closed; do not duplicate dynamic plan status here.

## Skills

Reusable operational workflows live in `.agents/skills/`.

Use the smallest applicable Skill. Extend an existing Skill before creating an overlapping one. Project truth belongs in `docs/`, not Skill bodies.

## Validation

Use the check matching the touched area:
- `make test` — product/core tests;
- `make harness-check` — AGENTS/Skills/process/plans/routing;
- `make knowledge-check` — living domain-model invariants;
- `make check` — backend/core + harness + knowledge checks;
- `make web-check` — Web TypeScript/build check.

Hosted Actions are the final PR gate; applicable `workflow_dispatch` runs are an execution fallback for intermediate deterministic checks when local execution is unavailable.
