# NAPMS repository agent map

## Purpose

This repository contains only current NAPMS project truth. Git history is the sole archive; completed, replaced or obsolete design material must not remain in the working tree as reference documentation.

## Task-first startup

Start from the explicit user task and load only the context required to perform it safely.

For non-trivial work:
1. read this file;
2. read the nearest scoped `AGENTS.md` for the area being changed;
3. load the smallest applicable Skill under `.agents/skills/`;
4. read only the current canonical artifacts, code and executable evidence required by the task.

Load `docs/plans/active/README.md` when the task resumes current execution, depends on lifecycle/gate state or needs implementation authorization. Do not inherit the active workstream for unrelated audits or questions.

Load process protocols on demand:
- `docs/process/change-lifecycle.md` — lifecycle and gates;
- `docs/process/decision-protocol.md` — material missing/conflicting answers;
- `docs/process/working-loop.md` — branch/checkpoint/validation mechanics;
- `docs/process/plan-lifecycle.md` — active-plan persistence rules.

## Source of truth

- `docs/requirements/` — current accepted product behavior and quality contracts.
- `docs/domain/` — current Strategic/Tactical DDD and semantic ownership.
- `docs/architecture/` — current accepted target structure and architecture constraints.
- `docs/decisions/` — only decisions that are still binding and not fully absorbed elsewhere.
- `docs/engineering/` — current operational/implementation contracts.
- `docs/ui/` — current reusable UI guidance.
- `docs/plans/active/` — current execution state only.
- `docs/process/` — reusable repository working protocols.
- `backend/src/` + `backend/tests/` — backend implementation and executable evidence.
- `web/` — React outer adapter; apply `web/AGENTS.md` before Web UI work.
- `.github/workflows/` — executable hosted CI gates and their exact triggers/commands.

If a document describes only a completed migration, previous model, supersession chain, audit result or old milestone, delete it after its still-valid outcome is represented in the current owner. Do not create archive folders in the working tree.

When current documentation and implementation disagree materially, do not silently treat old runtime shape as product truth. Resolve the highest affected canonical layer first.

## Change discipline

- Never commit directly to `main`; work on a branch and integrate through a PR using squash merge.
- Keep a PR draft while material work is accumulating; use Ready for review for the final hosted gate.
- Ordinary branch pushes must not be used merely to trigger hosted Actions.
- Git history is the only archive for completed plans and replaced project truth.

## CI execution map

Repository CI is part of the Harness execution surface.

- Inspect the applicable workflow and exact command/trigger before claiming a check cannot be executed.
- Prefer local checks during editing when available.
- When hosted CI is used as evidence, inspect run/job status and relevant logs before claiming PASS.
- If the connected capability cannot dispatch a workflow, state the tool limitation rather than treating CI as absent.

## Architecture guardrails

Never invent product/domain truth to make implementation convenient. A Bounded Context is not automatically a service, database, team or deployment unit.

- modular application with explicit semantic modules and ports/adapters;
- dependencies point inward: Domain <- Application/Ports <- Adapters/Composition;
- Domain has no framework, database, transport, configuration, logging or DI-container dependencies;
- Application consumes explicit ports owned by the consuming module;
- constructor injection; no service locator/global mutable dependency registry;
- business provenance is domain truth; operational logs do not replace it;
- technical realization changes do not silently redefine domain identity.

Before non-trivial production-code edits, load the active capsule and verify the applicable implementation authorization. No G4 lease means no production-code implementation.

## Validation

Use the smallest check matching the touched area:
- `make test` — product/core tests;
- `make harness-check` — AGENTS/Skills/process/plans/routing/lifecycle checks;
- `make knowledge-check` — domain-model knowledge invariants;
- `make check` — backend/core + harness + knowledge checks;
- `make web-check` — Web TypeScript/build check.
