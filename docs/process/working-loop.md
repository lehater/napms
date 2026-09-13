# Working loop

Use this protocol for branch execution, checkpoints, validation and context/session rollover. It owns execution mechanics; `change-lifecycle.md` owns stage/gate semantics and only points here when a lifecycle transition creates a checkpoint or rollover need.

## Persistence model

```text
active conversation
    = disposable execution context

consequential stakeholder evidence
    = durable source evidence when worth preserving, non-authoritative by itself

docs/plans/active/README.md
    = durable resume state for the current task

working branch / worktree
    = durable code checkpoints/WIP/fixups as needed

main
    = curated semantic history through squash merge
```

Agents/chats must not commit directly to `main`.

Stakeholder evidence is preserved more aggressively than interpretations but loaded more conservatively than canonical truth. Normal startup must not preload historical evidence. Search/load only evidence relevant to the current problem, contradiction or synthesis task.

## Checkpoint triggers

Write a branch checkpoint when at least one is true:
- a coherent semantic increment is complete;
- the next task depends on the new state;
- the lifecycle stage/gate changes materially;
- the session/workstream is switching;
- losing the work would be costly;
- the author explicitly asks to persist it.

Do not checkpoint every wording/edit operation.

At a checkpoint, harvest the active discussion before discarding temporary reasoning:
- accepted product/domain/architecture truth goes to its canonical owner;
- consequential stakeholder evidence is preserved separately enough to be reinterpreted later;
- unresolved material discoveries remain explicitly non-authoritative;
- candidate journeys/use cases/capability or boundary clues are preserved only when losing them would harm later work.

A stakeholder answer or example may contain evidence beyond the immediate question it resolved. Check for additional problem/goal/usage/workaround/risk/edge-case information before discarding the conversation. Do not persist conversation dumps, duplicated canonical truth or every incidental example.

Route preserved evidence/discovery to the smallest existing durable owner. If a growing evidence set is repeatedly reused across workstreams or no existing owner can contain it without becoming a mixed archive, treat that as a signal to design a dedicated evidence owner deliberately; do not invent an ad-hoc repository path during ordinary checkpointing.

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
2. harvest consequential stakeholder evidence and unresolved discoveries from the active discussion; preserve compact source observations separately from their current interpretation when later reinterpretation may matter;
3. persist only material unresolved problems/discoveries in the smallest correct owner: current plan/capsule while active, a bounded-context problem register when parking context-local work, or another existing durable owner when justified;
4. update `docs/plans/active/README.md` with the current task, lifecycle stage/state when material, minimal working set, blockers, gate and next action;
5. checkpoint coherent branch work when losing it would be costly;
6. preserve evidence references needed to resume or later synthesize without preserving full transcript/tool dumps;
7. discard temporary reasoning, duplicated explanations, rejected exploration, non-consequential candidate ideas and task-local rules that no longer apply.

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

Do not automatically reload the top-level change lifecycle, protocols or historical evidence from completed stages during ordinary work. The resume capsule should carry the resulting stage/gate state; transition protocols and source evidence are loaded again only when routing, gate evaluation, reopen/invalidation, ambiguity or explicit synthesis requires them.

When a parked context is deliberately resumed, canonical context truth comes first, then its context problem register; any roadmap/evidence corpus is secondary and must be revalidated before its ordering or interpretation is trusted.

## Side chats and parallel work

A second chat opened for analysis, research or review is read-only by default. Its useful result should be returned as findings or absorbed by the write owner into canonical state/source evidence as appropriate.

If two chats must write concurrently:
- use separate branches/worktrees;
- keep write scopes disjoint where practical;
- only one writer updates `docs/plans/active/README.md`;
- before integration, re-check the relevant branch base and revalidate any canonical inputs that changed since the task base.

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
