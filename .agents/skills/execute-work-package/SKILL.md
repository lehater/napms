---
name: execute-work-package
description: "Use when resuming, continuing, or executing the current non-trivial NAPMS plan/work package. Recover the compact active resume state/gate, keep its artifact and exit condition explicit, route the current uncertainty to the smallest relevant Skill, update durable state, and stop at the local gate. Read the full plan only when coordination or missing context requires it. Do not use for one isolated implementation task when no active plan coordination is needed."
---

# Execute Work Package

## Responsibility

Answer: what are we doing now, what owns closure, what artifact changes, and what must become true before advancing?

This Skill orchestrates the active work package. It does not bypass `docs/process/change-lifecycle.md`: stage/gate transition remains owned by the lifecycle, and code execution is allowed only with the applicable scoped G4 implementation lease.

## Procedure

1. Recover in one order: root `AGENTS.md` -> `docs/plans/active/README.md` -> nearest scoped `AGENTS.md`.
2. Recover current task, lifecycle stage/state/basis, goal, working set, blockers, gate, implementation authorization/scope/basis and next action from the resume capsule.
3. Read the full current plan only for planning/coordination/stage transition, when the capsule explicitly points to it, or when a material fact required for the current task is missing.
4. Read only the canonical truth/code in the current working set; expand deliberately when evidence requires it.
5. Treat capsule facts as recovery summaries only. If they conflict with a canonical owner, use the canonical truth and refresh the capsule.
6. Before routing work, check whether the requested action is permitted by the current lifecycle lease:
   - implementation work without `Lifecycle stage: IMPLEMENTATION` + `Implementation authorization: G4 PASS` -> route to `implementation-readiness-stage.md`, not `implement-slice`;
   - implementation work outside the recorded `Authorized scope` or with missing/stale `Authorization basis` -> return to S4/G4 evaluation;
   - transition/reopen/gate ambiguity -> load `change-lifecycle.md` and resolve the owning stage first;
   - authorized implementation slice -> `implement-slice`;
   - domain semantic/boundary change -> `domain-model-change`;
   - architecture design/rework -> `architecture-stage.md`; use `architecture-review` for judgement-heavy review;
   - one material unresolved To-Be choice -> `resolve-decision`.
7. Apply `docs/process/decision-protocol.md`; never invent a blocking answer.
8. Work against the named artifact/code and re-evaluate the local exit after each semantic increment.
9. Use `docs/process/working-loop.md` for checkpoints, upstream reopen during implementation and context rollover.
10. Update the resume capsule whenever current task, stage/state/basis, implementation authorization, working set, blocker, gate or next action materially changes. Update the full plan only when coordination state or plan structure changes.
11. Stop at the gate; do not start the next stage merely because it is planned.

## Output state

Keep visible: current task, current artifact, lifecycle stage/state/basis, implementation authorization/scope when active, blockers, gate/local exit, semantic result and next action.
