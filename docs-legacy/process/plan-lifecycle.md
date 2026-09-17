# Active-plan lifecycle

## Purpose

`docs/plans/active/README.md` is the single durable pointer to current execution state.

The working tree is not an execution archive. Completed plans, prior roadmaps, superseded work packages and parked historical notes are removed after any still-current truth has been absorbed into its canonical owner. Git history is the archive.

## Current execution model

When no workstream is active:

```text
Current: none.
```

No `PLAN-*.md` file remains under `docs/plans/active/`.

When a non-trivial workstream is active, `docs/plans/active/README.md` points to exactly one current `PLAN-*.md`. The plan owns coordination for that selected increment only. It is removed when completed or abandoned after durable current outcomes are absorbed into requirements/domain/architecture/engineering truth.

Do not create durable parking registries or historical roadmaps merely to remember future work. A still-current unresolved constraint belongs in the highest canonical owner it constrains. A speculative or no-longer-selected idea belongs in Git history or a future fresh analysis, not the working knowledge base.

## Resume capsule

For active work the capsule provides the minimum information needed to resume safely:

- current plan and task;
- goal;
- lifecycle stage/state and basis;
- implementation authorization, scope and basis;
- a small working set;
- blockers;
- current gate;
- next action.

Canonical requirements/domain/architecture/engineering truth wins over capsule summaries.

## Lifecycle execution lease

Required fields when `Current` is not `none`:

```text
Lifecycle stage: `S0|S1|S2|S3|S4|IMPLEMENTATION|META`
Stage state: `NOT_STARTED|IN_PROGRESS|BLOCKED|GATE_FAILED|ACCEPTED|DIRTY`
Lifecycle basis: <concise current canonical references / gate evidence / trigger>
Implementation authorization: `none|G4 PASS`
Authorized scope: `none|<stable scope or slice reference>`
Authorization basis: `none|<G4/upstream references establishing authorization>`
```

Rules:

- `S0`..`S4` are the semantic stages from `change-lifecycle.md`.
- `IMPLEMENTATION` is permitted only after G4.
- `META` is for Harness/process work outside product S0-S4.
- `G4 PASS` is scoped, never repository-wide permission.
- outside `IMPLEMENTATION`, authorization/scope/basis are `none`;
- reopening an upstream stage revokes any G4 lease immediately;
- a different implementation slice requires its own G4 authorization.

## Context budget

When `Current` is not `none`:

- the capsule is at most 6 KiB;
- `Read first` contains at most 5 existing repository files;
- their total tracked size is at most 24 KiB;
- expand context only when the task demonstrates need.

## Minimum active-capsule contract

When `Current` is not `none`, the capsule contains:

```text
Current:
Goal:
Current task:
Lifecycle stage:
Stage state:
Lifecycle basis:
Implementation authorization:
Authorized scope:
Authorization basis:
## Working set
Read first:
## Blockers
## Gate
## Next
```

## Minimum active-plan contract

Each current `PLAN-*.md` contains:

- `Status`;
- `## Goal`;
- `## Inputs`;
- `## Exit criteria`;
- `## Blockers`;
- `## Next`.

Mutable current task/stage lives only in the capsule. Completed or superseded plans must not remain under `active/`.
