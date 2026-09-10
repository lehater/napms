# Working loop

## Persistence model

```text
active conversation
    = disposable execution context

docs/plans/active/README.md
    = durable resume state for the current task

working branch / worktree
    = durable code checkpoints/WIP/fixups as needed

main
    = curated semantic history through squash merge
```

Agents/chats must not commit directly to `main`.

## Checkpoint triggers

Write a branch checkpoint when at least one is true:
- a coherent semantic increment is complete;
- the next task depends on the new state;
- the session/workstream is switching;
- losing the work would be costly;
- the author explicitly asks to persist it.

Do not checkpoint every wording/edit operation.

## Context rollover

Starting a fresh chat/session is a normal context-management operation, not a failure.

Prefer rollover when:
- the semantic phase changes (for example domain closure -> implementation or implementation -> review);
- the conversation becomes costly, stale, repeatedly rereads old context, or has been compacted heavily;
- large logs, diffs, research or rejected alternatives dominate the history;
- the workstream is switching and the new task can be stated independently.

Before rollover:
1. absorb durable product/domain/architecture decisions into their canonical artifacts;
2. update `docs/plans/active/README.md` with the current task, minimal working set, blockers, gate and next action;
3. checkpoint coherent code on the working branch when losing it would be costly;
4. preserve only durable constraints/results, not full reasoning trails, tool output or rejected exploration.

A fresh session recovers in this order:

```text
root AGENTS.md
  -> docs/plans/active/README.md
  -> nearest scoped AGENTS.md
  -> smallest applicable Skill
  -> capsule working set
```

Read the full active plan only when planning/coordination/stage transition or missing material context requires it.

## Side chats and parallel work

A second chat opened for analysis, research or review is read-only by default. Its useful result should be returned as findings or absorbed by the write owner into canonical state.

If two chats must write concurrently:
- use separate branches/worktrees;
- keep write scopes disjoint where practical;
- only one writer updates `docs/plans/active/README.md`;
- before integration, re-check current `main` and revalidate any canonical inputs that changed since the task base.

Do not introduce multi-agent coordination machinery for ordinary sequential work.

## Validation execution

Repository-local checks and GitHub Actions are two execution surfaces for the same deterministic repository gates.

Normal editing loop:
1. run the smallest applicable local check when the agent environment supports it;
2. fix known failures before requesting the final hosted gate;
3. use the applicable workflow's `workflow_dispatch` as an intermediate fallback only when local execution is unavailable and the current GitHub capability can dispatch it;
4. inspect hosted run/job status and logs before recording PASS evidence.

Before declaring a gate unexecutable, inspect `.github/workflows/` to determine:
- which workflow owns the affected area;
- its exact command;
- its path filters and event trigger;
- whether `workflow_dispatch` is available.

Do not confuse capability absence with CI absence. If the current connector/runtime can read Actions but cannot start a new workflow, record that tool limitation explicitly and preserve the pending gate in the active capsule.

## Integration

One PR should represent one coherent semantic stage. Accumulate branch commits freely enough for safety/review, then squash merge.

For expensive GitHub Actions, keep the PR draft while work is accumulating. Repository CI is triggered when the PR is marked ready for review, not on ordinary branch pushes.

Treat `Ready for review` as a request for the final hosted gate, not as a per-fix test button:
- before marking ready, run the applicable repository-local checks and batch known fixes;
- if local execution is unavailable, an explicit `workflow_dispatch` run of the same gate may provide the intermediate evidence without changing PR review state;
- if a deterministic gate failure requires material changes, return the PR to draft once, batch the corrections, rerun the applicable local checks, then mark ready once for a fresh gate;
- if an isolated hosted job fails for a transient/flaky infrastructure reason and no repository change is required, rerun the failed job/workflow instead of toggling Draft/Ready;
- avoid repeated Draft -> Ready cycles for individual fixes: each cycle reevaluates the accumulated PR path diff and can restart every applicable hosted gate.

Hosted gates validate the complete affected PR scope. Local editing may use the smallest applicable checks, but the final gate must not rely only on the last commit delta.
