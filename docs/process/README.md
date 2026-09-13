# NAPMS development process

This directory contains the minimal reusable protocols used by repository agents and humans.

Read only what the current task requires:

- `change-lifecycle.md` — top-level stage/gate progression from need to implementation readiness, including reopen/block handling and minimal-context lifecycle. Load for routing/transitions/gate work, not every ordinary task.
- `problem-evidence-stage.md` — S0 problem/evidence framing and G0. Load only when the trigger/problem is not yet sufficiently framed for Requirements.
- `requirements-stage.md` — S1 Requirements methodology and G1 guarantees. Load only while requirements work or G1 evaluation is active.
- `domain-design-stage.md` — S2 Domain Design routing and final G2 guarantees.
- `strategic-ddd-convergence.md` — Strategic DDD convergence. Load only when context ownership/boundary/relationship is actually under question.
- `tactical-ddd-stage.md` — Tactical DDD identity/lifecycle/invariant methodology. Load only for tactical work inside an accepted context boundary.
- `architecture-stage.md` — S3 architecture design methodology and G3 guarantees. Load only while architecture work/gate is active.
- `implementation-readiness-stage.md` — S4 pre-code impact/slicing/test/migration methodology and G4 authorization gate.
- `working-loop.md` — branch/checkpoint/squash semantics for evolving work.
- `decision-protocol.md` — no-invention and unknown-resolution rules.
- `domain-change-protocol.md` — focused domain re-entry guidance when implementation findings may change accepted semantics.
- `plan-lifecycle.md` — how current execution state is persisted/resumed, how unresolved bounded-context problems are parked, and when an ordered roadmap is justified.

Do not preload all protocols. Start from the repository agent map and active resume capsule, then load only the applicable Skill, current-stage protocol when needed, and minimal working set. Expand evidence only when the current task demonstrates the need.

Project truth belongs in the domain/requirements/architecture/engineering areas, not here.
