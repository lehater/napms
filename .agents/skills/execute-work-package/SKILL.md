---
name: execute-work-package
description: "Use when resuming, continuing, or executing the current non-trivial NAPMS plan/work package. Recover the compact active resume state/gate, keep its artifact and exit condition explicit, route the current uncertainty to the smallest relevant Skill, update durable state, and stop at the local gate. Read the full plan only when coordination or missing context requires it. Do not use for one isolated implementation task when no active plan coordination is needed."
---

# Execute Work Package

## Responsibility

Answer: what are we doing now, what owns closure, what artifact changes, and what must become true before advancing?

## Procedure

1. Read root/scoped `AGENTS.md`, then `docs/plans/active/README.md`.
2. Recover current task, goal, working set, blockers, gate and next action from the resume capsule.
3. Read the full current plan only for planning/coordination/stage transition, when the capsule explicitly points to it, or when a material fact required for the current task is missing.
4. Read only the canonical truth/code in the current working set; expand deliberately when evidence requires it.
5. Route content work:
   - implementation slice -> `implement-slice`;
   - domain semantic/boundary change -> `domain-model-change`;
   - architecture challenge/review -> `architecture-review`;
   - one material unresolved To-Be choice -> `resolve-decision`.
6. Apply `docs/process/decision-protocol.md`; never invent a blocking answer.
7. Work against the named artifact/code and re-evaluate the local exit after each semantic increment.
8. Use `docs/process/working-loop.md` for checkpoints and context rollover.
9. Update the resume capsule whenever current task, working set, blocker, gate or next action materially changes. Update the full plan only when coordination state or plan structure changes.
10. Stop at the gate; do not start the next stage merely because it is planned.

## Output state

Keep visible: current task, current artifact, blockers, gate/local exit, semantic result and next action.
