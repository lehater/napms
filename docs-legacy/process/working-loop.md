# Working loop

Use this protocol for branch execution, checkpoints, validation and session rollover. `change-lifecycle.md` owns stage/gate semantics.

## Persistence model

```text
conversation
    = disposable execution context

docs/plans/active/README.md
    = current execution resume state when relevant

working branch / worktree
    = WIP and coherent checkpoints

current requirements/domain/architecture/engineering/UI docs
    = current project truth

Git history
    = replaced repository state
```

Agents/chats do not commit directly to `main`.

Do not create transcript stores, evidence archives, completed-work catalogs, parked-context registries or supersession documents merely to preserve prior reasoning. If a fact remains important to current behavior or design, absorb it into the smallest current canonical owner.

## Checkpoints

Create a branch checkpoint when a coherent increment is complete, the next task depends on it, a material lifecycle transition occurs, losing WIP would be costly, or the owner explicitly requests persistence.

Do not checkpoint every wording operation.

Before a checkpoint:

1. absorb accepted current product/domain/architecture/engineering/UI truth into its canonical owner;
2. keep unresolved blockers only in the active capsule/plan while they constrain current work;
3. remove replaced statements rather than preserving parallel variants;
4. ensure current docs do not point to deleted historical artifacts;
5. run the smallest applicable deterministic validation available.

Conversation rationale that is not needed to interpret the current contract is discarded. Git history retains previous repository versions.

## Upstream reopen during implementation

When implementation/testing exposes a `REOPEN(S0..S3)` finding:

1. stop the affected implementation scope;
2. revoke its dependent G4 lease;
3. preserve useful WIP on the working branch without treating it as accepted target truth;
4. record the current blocking finding in the active capsule/plan;
5. resolve the owning upstream stage and revalidate dependent stages;
6. resume only after S4/G4 authorizes an applicable scope again.

Independent implementation may continue only when its guarantees do not depend on the reopened truth.

## Session rollover

A fresh session is a normal context-management operation. Prefer rollover when the task/stage changes materially, a `REOPEN` changes the semantic owner, or accumulated conversation/logs/rejected alternatives dominate useful context.

Before rollover:

1. update current canonical artifacts with accepted truth;
2. update the active capsule with current task/stage/basis, blockers, minimal working set and next action when active execution exists;
3. checkpoint coherent branch WIP when losing it would be costly;
4. discard temporary reasoning, rejected alternatives and obsolete task-local context.

Resume current execution in this order:

```text
root AGENTS.md
-> docs/plans/active/README.md
-> nearest scoped AGENTS.md
-> smallest applicable Skill
-> capsule working set
-> additional evidence/process only when demonstrated necessary
```

For an unrelated task:

```text
root AGENTS.md
-> nearest scoped AGENTS.md
-> smallest applicable Skill
-> minimal task working set
```

Do not load the active capsule for an unrelated task unless the task depends on current execution/gate/authorization.

## Parallel/side work

A separate analysis/review chat is read-only by default. Useful accepted outcomes are absorbed by the write owner into current canonical artifacts.

When concurrent writes are genuinely required, use separate branches/worktrees, keep write scopes disjoint, allow only one writer to update the active capsule, and revalidate changed shared inputs before integration.

Do not add multi-agent coordination machinery for ordinary sequential work.

## Validation

Repository-local checks and GitHub Actions are execution surfaces for the same deterministic gates.

Normal loop:

1. run the smallest applicable local check when available;
2. fix known deterministic failures before final hosted validation;
3. inspect `.github/workflows/` for the owning command, trigger and path filters before declaring a gate unavailable;
4. use a manually dispatchable hosted workflow as an intermediate surface when local execution is unavailable and dispatch capability exists;
5. inspect hosted job status/logs before recording PASS.

A capability limitation of the current agent/tool is not evidence that repository CI does not exist.

## Pull-request integration

Keep one PR semantically coherent enough to review and squash. Intermediate branch commits are WIP checkpoints; the squash merge is the integration unit.

When hosted gates are expensive, keep the PR draft while accumulating known changes. Treat `Ready for review` as the request for the final hosted gate rather than a per-fix test button.

Hosted validation covers the complete affected PR scope. A local check of only the last edit is not sufficient final evidence when the PR changes a broader surface.
