# Active execution

Current: `harness-change-lifecycle.md` — isolated Harness lifecycle/context-management design on branch `harness/change-lifecycle`.

Goal: define a coherent stage/gate change lifecycle from need to implementation readiness and a paired context lifecycle that loads only the minimum rules/artifacts required for the current task.

Current task: challenge and refine the upper-level lifecycle/context model before designing detailed per-stage methodologies.

## Working set

Read first:
- `docs/plans/active/harness-change-lifecycle.md`;
- `docs/process/change-lifecycle.md`;
- `.agents/skills/agent-harness-design/SKILL.md`.

Expand only if needed:
- `docs/process/README.md` when changing protocol routing/indexing;
- `docs/process/domain-change-protocol.md` when checking semantic re-entry overlap;
- `docs/process/working-loop.md` when checking checkpoint/session rollover mechanics;
- `docs/process/plan-lifecycle.md` when checking active-state/problem-register ownership;
- `AGENTS.md` when changing repository startup/routing rules.

## Recovery facts

- All current Harness design changes belong only to branch `harness/change-lifecycle`; do not update or merge to `main` unless explicitly requested later.
- `docs/process/change-lifecycle.md` is the current top-level progression model; treat it as a draft to challenge, not as unquestionable truth.
- The model separates Change Lifecycle from Context Lifecycle while keeping them coordinated.
- Gate outcomes are `PASS`, `REWORK`, `REOPEN(stage)` and `BLOCKED`.
- Earlier-stage changes mark dependent downstream stages `DIRTY` until revalidated.
- Missing upstream truth must become an explicit problem/unknown; lower layers must not invent it.
- Repetition without changed evidence/model/problem/decision state is a no-progress blockage, not permission to loop.
- Context loading is progressive: kernel/routing -> current stage protocol -> primary Skill -> minimal working set -> lazy evidence.
- Durable accepted truth, open problems and current execution state must be promoted out of conversation history before rollover.
- Detailed Requirements/DDD/Architecture/Implementation-Readiness methodologies are intentionally deferred until the upper-level model is coherent.

## Blockers

No external blocker. The current design risk is over-expanding rules before the lifecycle/context kernel is stable.

## Gate

Do not proceed to detailed per-stage methodology until the top-level lifecycle has unambiguous progression/re-entry/block semantics, explicit context loading/unloading behavior, non-overlapping ownership with existing process protocols, and recoverability from a fresh session.

## Next

Review the lifecycle as a state-transition model, find contradictions or missing transitions, then make only the smallest alignment changes needed in `AGENTS.md`, `working-loop.md` and `plan-lifecycle.md` before expanding the methodology.
