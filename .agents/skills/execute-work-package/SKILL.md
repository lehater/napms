---
name: execute-work-package
description: "Use when resuming, continuing, or executing the current non-trivial NAPMS plan/work package. Recover the active plan/gate, keep its artifact and exit condition explicit, route the current uncertainty to the smallest relevant Skill, update durable state, and stop at the local gate. Do not use for one isolated implementation task when no active plan coordination is needed."
---

# Execute Work Package

## Responsibility

Answer: what are we doing now, what owns closure, what artifact changes, and what must become true before advancing?

## Procedure

1. Read root/scoped `AGENTS.md`, then `docs/plans/active/README.md` and the current plan.
2. Recover goal, current stage, inputs, blockers, exit and next.
3. Read only the canonical truth required by the current work package.
4. Route content work:
   - implementation slice -> `implement-slice`;
   - domain semantic/boundary change -> `domain-model-change`;
   - architecture challenge/review -> `architecture-review`;
   - one material unresolved To-Be choice -> `resolve-decision`.
5. Apply `docs/process/decision-protocol.md`; never invent a blocking answer.
6. Work against the named artifact/code and re-evaluate the local exit after each semantic increment.
7. Use `docs/process/working-loop.md` for checkpoints.
8. Update the active plan only when execution state materially changes.
9. Stop at the gate; do not start the next stage merely because it is planned.

## Output state

Keep visible: current plan/stage, current artifact, blockers, local exit and the semantic result.
