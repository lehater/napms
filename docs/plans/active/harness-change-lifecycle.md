# Harness change-lifecycle design

## Status

Active on branch `harness/change-lifecycle`. This workstream is intentionally isolated from `main` and is not authorized for merge there unless explicitly requested later.

## Goal

Design and evolve the repository Harness so a change can move from need/requirements to implementation readiness through explicit stages and gates, while loading only the minimal context required for the current task and preserving durable knowledge outside conversation history.

## Inputs

- `AGENTS.md` progressive-startup and no-invention rules;
- existing `docs/process/` protocols;
- `.agents/skills/agent-harness-design/SKILL.md`;
- observed design requirements from current Harness work:
  - stage/gate progression;
  - rework/reopen/block behavior;
  - problem/unknown accumulation without invention;
  - no-progress protection;
  - minimal context loading and reliable rollover.

## Current stage

Harness meta-design: top-level lifecycle and context-management model.

## Current gate

The upper-level Harness model is coherent enough to begin designing individual stage methodologies only when:

- one top-level lifecycle owns stage/gate progression;
- gate outcomes and upstream reopen semantics are unambiguous;
- blocked/unknown handling prevents invention;
- repeated work has a no-progress stop condition;
- context startup, lazy loading, durable promotion and rollover are explicit;
- existing process protocols have non-overlapping ownership under that model;
- a fresh session can recover this workstream without prior conversation history.

## Work packages

### H1 — Lifecycle kernel

Define stages, gates, stage states, PASS/REWORK/REOPEN/BLOCKED, dirty propagation, problem handling and no-progress semantics.

Status: initial protocol captured in `docs/process/change-lifecycle.md`; continue challenging/refining rather than treating the first draft as final.

### H2 — Context lifecycle

Define minimal startup context, stage/task routing, lazy evidence loading, durable promotion/discard and session rollover.

Status: initial model captured in `docs/process/change-lifecycle.md`; needs validation against real workflows.

### H3 — Existing Harness alignment

Align existing protocols/Skills with the lifecycle and remove overlapping progression models.

Status: started. `domain-change-protocol.md` and `agent-harness-design` have been aligned at the top level.

### H4 — Stage methodology design

Only after H1-H3 are coherent, design the internal methods/gates for Requirements, Strategic/Tactical Domain Design, Architecture and Implementation Readiness.

Status: not started by design.

### H5 — Deterministic validation

After the lifecycle format stabilizes, identify which invariants can be checked by `make harness-check`/knowledge validators rather than prose judgement.

Status: not started by design.

## Blockers

No external blocker. The current risk is premature detail: do not expand into per-stage methodology until the upper-level lifecycle/context model survives review.

## Exit criteria

- upper-level Change Lifecycle and Context Lifecycle are coherent and non-overlapping with existing process ownership;
- startup/recovery requires only a minimal capsule plus current protocol/Skill/working set;
- no material Harness state depends on conversation history;
- the model defines how to stop rather than loop when evidence/decisions do not progress;
- applicable Harness checks are identified and executed when the current tool/runtime permits it;
- the next design increment is explicitly selected.

## Next

Review the new top-level lifecycle as a state-transition model, identify contradictions/ambiguities, and decide whether `AGENTS.md`, `plan-lifecycle.md` and `working-loop.md` need small alignment changes before any per-stage methodology is added.
