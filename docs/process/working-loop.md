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

For expensive GitHub Actions, keep the PR draft while work is accumulating. Repository CI is triggered when the PR is marked ready for review, not on ordinary branch pushes. If material changes are needed after that gate, return the PR to draft, change it, then mark ready again for a fresh gate.
