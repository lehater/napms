# NAPMS repository agent map

## Purpose

This repository is the source of truth for the new **Network Access Policy Management System (NAPMS)** product.

Legacy/reconstruction evidence lives outside this repository and does not define target behavior.

## Task-first startup

Start from the explicit user task, then load only the repository context required to perform it safely.

For non-trivial work:
1. read this file;
2. read the nearest scoped `AGENTS.md` for the area being changed;
3. load the smallest applicable Skill under `.agents/skills/` when the task matches a reusable workflow;
4. read only the canonical artifacts, code and evidence required by that task.

Load `docs/plans/active/README.md` only when the task is to resume/continue current execution, depends on the current lifecycle/gate state, or needs implementation authorization. An unrelated audit, review, research task or isolated repository question must not inherit the active workstream merely because one exists.

When the capsule is loaded, treat it as a non-authoritative recovery cache. Canonical domain/requirements/architecture/engineering owners win on conflict and the capsule must be refreshed.

Read the full current `PLAN-*.md` only for planning/coordination/stage transition, when the capsule explicitly directs you there, or when a material fact required for the current task is missing. Do not load future work packages by default.

Do not scan `docs/baseline/` or completed historical Wave-1 material unless the task explicitly requires history or provenance.

Load process protocols on demand:
- `docs/process/change-lifecycle.md` for lifecycle entry/routing, gates, reopen or invalidation;
- `docs/process/decision-protocol.md` for a material missing/conflicting answer;
- `docs/process/working-loop.md` for branch/checkpoint/validation/session mechanics;
- `docs/process/plan-lifecycle.md` for active-plan/capsule persistence rules.

## Task precedence

The explicit user request selects the task, scope and desired output. Repository instructions and accepted project truth constrain how that task is performed; they do not redirect an unrelated task into the active plan.

A Skill or process protocol may broaden context, reroute work or stop execution only for a concrete repository invariant, a blocking unknown/conflict, or a dependency of the requested task. Make that reason explicit rather than following workflow prose mechanically.

## Source-of-truth map

- `docs/domain/` — living Strategic/Tactical DDD.
- `docs/requirements/` — accepted product behavior, quality and semantic contracts.
- `docs/architecture/` — current target architecture and ownership constraints.
- `docs/decisions/` — consequential ADRs.
- `docs/engineering/` — implementation contracts/policies and engineering state.
- `docs/engineering/context-problems/` — durable bounded-context problem/gap registers for unresolved future work; not domain truth, prioritization or current execution state.
- `docs/ui/` — implementation-oriented UI guidance derived from accepted requirements.
- `docs/plans/active/` — current execution state only.
- `docs/process/` — reusable repository working protocols.
- `docs/baseline/` — accepted snapshots/provenance; not the normal edit target.
- `backend/src/` + `backend/tests/` — backend implementation and executable evidence.
- `web/` — React outer adapter; apply `web/AGENTS.md` before Web UI work.
- `.github/workflows/` — executable hosted CI gates and their exact triggers/commands.

When layers disagree materially, resolve the highest affected canonical truth first rather than silently choosing code.

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
- The hosted gates are intentionally trigger-controlled; do not assume every push or squash runs them.
- `Ready for review` requests the final hosted PR gate for affected paths.
- Workflows exposing `workflow_dispatch` are valid intermediate deterministic fallbacks when local execution is unavailable.
- Prefer local checks during the editing loop when available; do not toggle Draft/Ready merely to obtain an intermediate run.
- When hosted CI is used as evidence, inspect the resulting run/job status and relevant logs before claiming PASS.
- If the connected GitHub capability cannot dispatch a workflow, state that tool gap rather than treating CI as absent.

## No-invention and architecture guardrails

Never invent unsupported product/domain truth to make implementation convenient. A Bounded Context is not automatically a service, database, team or deployment unit.

Architecture invariants:
- modular application with explicit semantic modules and ports/adapters;
- dependencies point inward: Domain <- Application/Ports <- Adapters/Composition;
- Domain has no framework, database, transport, configuration, logging or DI-container dependencies;
- Application consumes explicit ports owned by the consuming module;
- constructor injection; no service locator/global mutable dependency registry;
- business audit/provenance is domain truth; operational logs do not replace it;
- technical realization changes do not silently redefine domain identity.

Before non-trivial production-code edits, load the active capsule and verify the applicable implementation authorization. `docs/process/change-lifecycle.md`, `docs/process/plan-lifecycle.md` and the implementation Skill own the detailed lease semantics; do not duplicate that state machine here.

## Skills

Reusable judgement-heavy workflows live in `.agents/skills/`.

Use the smallest applicable Skill. Extend an existing Skill before creating an overlapping one. Project truth belongs in `docs/`, not Skill bodies. Deterministic invariants belong in validators rather than prose-only Skills.

## Validation

Use the smallest check matching the touched area:
- `make test` — product/core tests;
- `make harness-check` — AGENTS/Skills/process/plans/routing/lifecycle transitions;
- `make knowledge-check` — living domain-model invariants;
- `make check` — backend/core + harness + knowledge checks;
- `make web-check` — Web TypeScript/build check.

Hosted Actions are the final PR gate; applicable `workflow_dispatch` runs are an intermediate execution fallback when local execution is unavailable.
