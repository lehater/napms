---
name: execute-work-package
description: "Use only when resuming, continuing, or coordinating the current non-trivial NAPMS plan/work package. Recover the active resume state, identify the current owner/gate, route to the smallest task Skill or protocol, persist changed execution state, and stop at the local gate. Do not use for isolated audit, review, research, or implementation requests that do not depend on current-plan coordination."
---

# Execute Work Package

## Responsibility

Coordinate current plan execution without becoming a second lifecycle, decision or implementation methodology.

Answer only what orchestration needs: what is current, what owns the next work, what gate constrains it, and what durable execution state changed.

## Procedure

1. Read `docs/plans/active/README.md` and recover the current task, lifecycle/gate state, blockers, working set and next action.
2. Confirm the explicit user request actually depends on that current workstream. If it does not, return to task-first routing from root `AGENTS.md` instead of pulling the active plan into an unrelated task.
3. Load the nearest scoped `AGENTS.md`, then the smallest applicable Skill or process protocol for the current uncertainty/work. Do not preload neighboring Skills.
4. Use `docs/process/change-lifecycle.md` only for lifecycle entry/transition, gate, reopen/invalidation or routing ambiguity. Use `docs/process/plan-lifecycle.md` for capsule/lease persistence rules and `docs/process/working-loop.md` for branch/checkpoint/session mechanics.
5. For implementation work, verify the active implementation lease through its canonical capsule/protocol contract before routing to `implement-slice`; do not restate or reimplement the lease state machine here.
6. Read only the canonical artifacts/code in the task working set. Expand when concrete evidence demonstrates a missing dependency or contradiction.
7. Perform or route the current semantic increment, then update the resume capsule only when current task, lifecycle/gate state, authorization, working set, blocker or next action materially changed.
8. Read/update the full active plan only when coordination structure, work-package dependencies or plan-level exit state changed.
9. Stop at the current local gate. Do not start a planned next stage merely because it exists.

## Output state

Keep visible only the orchestration delta: current task, owning Skill/protocol/artifact, blocker or gate, semantic result, durable state updated, and next action.
