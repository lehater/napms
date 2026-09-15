# Change lifecycle

## Purpose

Route a non-trivial change from need to implementation without allowing a later layer to invent unresolved earlier-layer truth.

Use this protocol for stage entry, gate evaluation, reopen/dirty propagation and implementation authorization. Detailed work inside a stage belongs to the stage-specific protocol/Skill.

## Lifecycle

```text
S0 Problem / Evidence -> G0
S1 Requirements       -> G1
S2 Domain Design      -> G2
S3 Architecture       -> G3
S4 Implementation Readiness -> G4
IMPLEMENTATION for the exact G4-authorized scope
```

This is not a waterfall. Enter at the earliest layer whose current accepted truth may need to change:

- implementation impact/slicing only -> S4;
- architecture realization -> S3;
- domain meaning/ownership -> S2;
- observable product behavior -> S1;
- unclear need/conflicting evidence -> S0.

Starting later is valid only when required earlier guarantees already exist and remain applicable.

## Core invariants

1. A stage never resolves uncertainty owned by an earlier stage merely to keep moving.
2. Downstream work relies only on current upstream guarantees that passed their gate.
3. A material upstream change makes dependent downstream acceptance `DIRTY` until revalidated.
4. A blocking unknown stops at the gate that requires it.
5. Repeating reasoning without new evidence/model/problem/decision state is not progress.
6. G4 authorizes only the exact implementation scope it evaluated.
7. Reopening a guarantee used by an implementation lease revokes that lease immediately.

## Stage states

```text
NOT_STARTED
IN_PROGRESS
BLOCKED
GATE_FAILED
ACCEPTED
DIRTY
```

- `BLOCKED` — required knowledge/decision is not currently derivable.
- `GATE_FAILED` — the current stage owns a correctable deficiency.
- `DIRTY` — previously accepted output must be revalidated because a dependency changed; it is not automatically wrong.
- `ACCEPTED` — the stage gate passed against its current inputs.

## Gate outcomes

### PASS

The stage provides the guarantees required by the next stage. Mark it `ACCEPTED`, record a concise current basis in the active capsule when work is active, and continue only to required/dirty downstream work.

### REWORK

The deficiency belongs to the current stage. Record the concrete P0/P1 finding, mark `GATE_FAILED`, rework only the affected delta and evaluate the gate again.

### REOPEN(Sx)

A later stage exposed missing or invalid truth owned by an earlier stage.

1. revoke any dependent G4 lease;
2. move the owning stage to `IN_PROGRESS` or `BLOCKED`;
3. mark actually dependent downstream acceptances `DIRTY`;
4. resolve the owning stage;
5. revalidate dirty downstream stages in dependency order.

Strategic/Tactical routing inside S2 is internal to S2 rather than a top-level reopen.

### BLOCKED

Required truth cannot be derived from current canonical evidence. Record the blocking question in the current active plan/capsule, obtain the required evidence/owner decision, and do not pass the gate while it remains unresolved.

Do not create a permanent problem archive for a temporary blockage. A still-current semantic constraint belongs in its canonical owner; obsolete or superseded problem state is removed from the working tree and remains available through Git history.

## Problem classification

For a material unknown record only what current work needs:

- question/contradiction;
- owning lifecycle stage;
- why it blocks or constrains the current gate;
- evidence already checked;
- next resolution action.

Classify it as:

- `blocking` — required by the current gate;
- `later-required` — current accepted boundary that a known later stage must address;
- `non-required` — outside the current change; do not expand context to solve it.

A `later-required` constraint survives only in the current canonical owner it constrains or, while active, the current plan. Do not create roadmap/problem-history documents solely for retention.

## No-progress rule

Another iteration is justified only when it is expected to change evidence, accepted truth, problem state, decision state or the scope of uncertainty. Otherwise stop and require new evidence or an owner decision.

## Severity at gates

- P0 — contradictory/impossible; gate cannot pass.
- P1 — material unresolved ownership/behavior/boundary/readiness issue; gate cannot pass.
- P2 — non-blocking improvement/clarification.
- P3 — cosmetic/local polish.

P0/P1 affecting gate guarantees prevent PASS. P2/P3 may remain when the guarantees are otherwise satisfied.

## Context rule

Use progressive disclosure:

```text
repository routing
-> current transition/stage protocol when needed
-> primary Skill
-> minimal current project working set
-> additional evidence only on demonstrated need
-> ephemeral conversation analysis
```

At a material transition, persist current canonical truth and current execution state before dropping conversational context. `working-loop.md` owns checkpoint/session mechanics; `plan-lifecycle.md` owns the active capsule.

## Exit to implementation

G4 creates a scoped implementation lease, never repository-wide permission.

After G4 PASS the active capsule must contain:

```text
Lifecycle stage: IMPLEMENTATION
Implementation authorization: G4 PASS
Authorized scope: <exact implementation slice>
Authorization basis: <current G4/upstream evidence>
```

Implementation must not begin when the lease is missing, outside the requested scope, based on dirty/stale upstream truth, or when implementation evidence exposes a new upstream decision.

If an upstream guarantee changes, revoke the lease, reopen the owning stage, revalidate dependencies and issue a new applicable G4 lease before resuming that scope.

## Protocol ownership

- stage-specific documents own S0–S4 methods and gate guarantees;
- `decision-protocol.md` owns unknown/decision classification;
- `domain-change-protocol.md` owns focused domain re-entry;
- `working-loop.md` owns branch/checkpoint/validation/session mechanics;
- `plan-lifecycle.md` owns current active execution state.

This file owns lifecycle routing, gate outcomes, dirty propagation and scoped implementation authorization.
