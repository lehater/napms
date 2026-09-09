# Working loop

## Persistence model

```text
active conversation / worktree
    = mutable working state

working branch
    = durable checkpoints/WIP/fixups as needed

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

## Integration

One PR should represent one coherent semantic stage. Accumulate branch commits freely enough for safety/review, then squash merge.

For expensive GitHub Actions, keep the PR draft while work is accumulating. Repository CI is triggered when the PR is marked ready for review, not on ordinary branch pushes.

Treat `Ready for review` as a request for the final hosted gate, not as a per-fix test button:
- before marking ready, run the applicable repository-local checks and batch known fixes;
- if a deterministic gate failure requires material changes, return the PR to draft once, batch the corrections, rerun the applicable local checks, then mark ready once for a fresh gate;
- if an isolated hosted job fails for a transient/flaky infrastructure reason and no repository change is required, rerun the failed job/workflow instead of toggling Draft/Ready;
- avoid repeated Draft -> Ready cycles for individual fixes: each cycle reevaluates the accumulated PR path diff and can restart every applicable hosted gate.

Hosted gates validate the complete affected PR scope. Local editing may use the smallest applicable checks, but the final gate must not rely only on the last commit delta.
