# NAPMS repository agent map

## Purpose

This repository is the source of truth for the new **Network Access Policy Management System (NAPMS)** product.

Legacy/reconstruction evidence lives outside this repository and does not define target behavior.

## Progressive startup

Do not preload the whole repository.

For non-trivial work read, in order:
1. this file;
2. `docs/plans/active/README.md` and the current plan;
3. the nearest scoped `AGENTS.md`;
4. only the canonical domain/requirements/architecture/engineering artifacts needed by the current plan/work package;
5. the smallest applicable Skill under `.agents/skills/`.

Use `docs/process/decision-protocol.md` when a material answer is missing or conflicting.

## Source-of-truth map

- `docs/domain/` — living Strategic/Tactical DDD.
- `docs/requirements/` — accepted product behavior, quality and semantic contracts.
- `docs/architecture/` — current target architecture and ownership constraints.
- `docs/decisions/` — consequential ADRs.
- `docs/engineering/` — implementation contracts/policies and engineering state.
- `docs/plans/active/` — current execution state only.
- `docs/process/` — reusable repository working protocols.
- `docs/baseline/` — accepted snapshots/provenance; not the normal edit target.
- `src/` + `tests/` — current implementation and executable evidence.

When layers disagree materially, do not silently choose the code. Resolve the highest affected canonical truth first.

## Change discipline

- Agents/chats must not commit directly to `main`.
- Work on a branch; checkpoint/WIP/fixup commits are allowed there.
- Integrate one coherent semantic stage through a PR using **squash merge**.
- Keep the PR draft while work is accumulating. Mark it ready only for the final CI gate.
- Ordinary branch pushes must not trigger hosted Actions.
- If material changes are required after the final PR gate, return the PR to draft and gate again when ready.
- Git history is the archive for completed plans/superseded working artifacts.

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
- `make check` — all repository-local checks.

Hosted Actions are the final PR gate, not the branch editing loop.
