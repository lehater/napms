# NAPMS development process

This directory contains the minimal reusable protocols used by repository agents and humans.

Read only what the current task requires:

- `change-lifecycle.md` — top-level stage/gate progression from need to implementation readiness, including reopen/block handling and minimal-context lifecycle. Load for routing/transitions/gate work, not every ordinary task.
- `requirements-stage.md` — S1 Requirements methodology and G1 guarantees. Load only while requirements work or G1 evaluation is active.
- `working-loop.md` — branch/checkpoint/squash semantics for evolving work.
- `decision-protocol.md` — no-invention and unknown-resolution rules.
- `domain-change-protocol.md` — focused domain re-entry guidance when implementation findings may change accepted semantics.
- `plan-lifecycle.md` — how current execution state is persisted/resumed, how unresolved bounded-context problems are parked, and when an ordered roadmap is justified.

Do not preload all protocols. Start from the repository agent map and active resume capsule, then load only the applicable Skill, current-stage protocol when needed, and minimal working set. Expand evidence only when the current task demonstrates the need.

Project truth belongs in the domain/requirements/architecture/engineering areas, not here.
