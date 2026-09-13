# Working loop

Use this protocol for branch execution, checkpoints, validation and context/session rollover. It owns execution mechanics; `change-lifecycle.md` owns stage/gate semantics and only points here when a lifecycle transition creates a checkpoint or rollover need.

## Branch discipline

Agents/chats must not commit directly to `main`.

Work on a task-specific branch/worktree. Keep the branch rebased/checked against the relevant current base before final integration when concurrent work may have changed canonical inputs.

## Checkpoints

Write a branch checkpoint when at least one is true:
- a coherent semantic increment is complete;
- the next task depends on the new state;
- the lifecycle stage/gate changes materially;
- the session/workstream is switching;
- losing the work would be costly;
- the author explicitly asks to persist it.

Do not checkpoint every wording/edit operation.

## Upstream reopen during implementation

If implementation or testing exposes a finding that requires `REOPEN(S0..S3)`:

1. stop the affected implementation slice; do not continue semantic-affecting edits while its upstream guarantees are dirty;
2. preserve useful WIP on the working branch when losing it would be costly, but do not treat that WIP as accepted target truth;
3. record the finding and reopen reason in the active capsule/appropriate problem owner;
4. move to the owning upstream stage and revalidate dependent downstream stages in lifecycle order;
5. return to the affected implementation slice only after S4/G4 has been revalidated and implementation is authorized again.

Independent slices may continue only when their guarantees do not depend on the reopened decision and that independence is explicit enough to avoid hidden coupling.

A checkpoint made before upstream re-entry is recoverable WIP, not evidence that the implementation is still valid.

## Context rollover

This section is the canonical execution procedure for session/context rollover. `change-lifecycle.md` defines when lifecycle transitions make rollover useful; it must not grow a second detailed recovery procedure.

Starting a fresh chat/session is a normal context-management operation, not a failure.

Prefer rollover when:
- the semantic/lifecycle stage changes;
- a material `REOPEN` moves work to an earlier stage;
- the conversation becomes costly, stale, repeatedly rereads old context, or has been compacted heavily;
- large logs, diffs, research or rejected alternatives dominate the history;
- the workstream/task is switching and the new task can be stated independently;
- loaded rules/evidence mostly belong to the previous task and would pollute the next working context.

A stage transition is a strong compaction point, not an automatic requirement to start a fresh session. Continue in the same session only when the retained context is still small and directly relevant.

Before rollover:
1. absorb durable product/domain/architecture decisions into their canonical artifacts;
2. persist unresolved material problems in the smallest correct owner: current plan/capsule while active, a bounded-context problem register when parking context-local work, or another existing durable owner when justified;
3. update `docs/plans/active/README.md` with the current task, lifecycle stage/state when material, minimal working set, blockers, gate and next action;
4. checkpoint coherent branch work when losing it would be costly;
5. preserve evidence references needed to resume without preserving full evidence/tool dumps;
6. discard temporary reasoning, duplicated explanations, rejected exploration and task-local rules that no longer apply.

A fresh session recovers in this order:

```text
root AGENTS.md
  -> docs/plans/active/README.md
  -> nearest scoped AGENTS.md
  -> smallest applicable Skill
  -> capsule working set
  -> additional process/evidence only when current work demonstrates need
```

Read the full active plan only when planning/coordination/stage transition or missing material context requires it.

Do not automatically reload the top-level change lifecycle or protocols from completed stages during ordinary work. The resume capsule should carry the resulting stage/gate state; transition protocols are loaded again when routing, gate evaluation, reopen/invalidation or ambiguity requires them.

When a parked context is deliberately resumed, canonical context truth comes first, then its context problem register; any roadmap is secondary and must be revalidated before its ordering is trusted.

## Side chats and parallel work

A second chat opened for analysis, research or review is read-only by default. Its useful result should be returned as findings or absorbed by the write owner into canonical state.

If two chats must write concurrently:
- use separate branches/worktrees;
- keep write scopes disjoint where practical;
- only one writer updates `docs/plans/active/README.md`;
- before integration, re-check the relevant branch base and revalidate any canonical inputs that changed since the task base.

Do not introduce multi-agent coordination machinery for ordinary sequential work.
