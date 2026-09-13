# Harness change-lifecycle design

Status: `active`

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

## Work packages

### H1 — Lifecycle kernel

Define stages, gates, stage states, PASS/REWORK/REOPEN/BLOCKED, dirty propagation, problem handling and no-progress semantics.

Status: coherent baseline captured in `docs/process/change-lifecycle.md`. `ACCEPTED` is upstream-relative; `REOPEN` invalidates only dependent downstream guarantees; no-progress and blocking semantics are explicit. Continue to change this kernel only when stage-methodology use exposes a concrete defect.

### H2 — Context lifecycle

Define minimal startup context, stage/task routing, lazy evidence loading, durable promotion/discard and session rollover.

Status: coherent baseline captured and aligned with `AGENTS.md`, `working-loop.md` and `plan-lifecycle.md`. The top-level lifecycle is a transition protocol, not a file to preload for every task. Stage transition/REOPEN is a strong compaction point; fresh-session rollover is the reliable unload mechanism.

### H3 — Existing Harness alignment

Align existing protocols/Skills with the lifecycle and remove overlapping progression models.

Status: top-level alignment complete enough for the next increment. `domain-change-protocol.md` is a focused re-entry helper; `decision-protocol.md` owns known/hypothesis/unknown/conflict semantics; `working-loop.md` owns execution/checkpoint/rollover mechanics; `plan-lifecycle.md` owns durable execution state; `agent-harness-design` routes lifecycle design work.

### H4 — Stage methodology design

Design the internal methods/gates for Requirements, Strategic/Tactical Domain Design, Architecture and Implementation Readiness without inflating the always-loaded kernel.

Status: started. Use Requirements as the first real test of the stage-methodology boundary. Add a dedicated protocol only because no existing requirements methodology owns this work; defer a new Skill until repeated judgement-heavy routing demonstrates one is needed.

### H5 — Deterministic validation

After the lifecycle/stage formats stabilize through real use, identify which invariants can be checked by `make harness-check`/knowledge validators rather than prose judgement.

Status: not started by design. Existing validators remain authoritative for their current contracts; do not prematurely encode draft lifecycle fields as mandatory.

## Blockers

No external blocker. The main risk is turning every stage methodology into global startup context. New stage protocols must remain lazy-loaded and must not duplicate project truth.

## Exit criteria

- upper-level Change Lifecycle and Context Lifecycle are coherent and non-overlapping with existing process ownership;
- startup/recovery requires only a minimal capsule plus current protocol/Skill/working set;
- no material Harness state depends on conversation history;
- the model defines how to stop rather than loop when evidence/decisions do not progress;
- each major pre-code stage has a clear responsibility, method boundary and gate without duplicating canonical product truth;
- applicable Harness checks are identified and executed when the current tool/runtime permits it;
- deterministic validation additions are justified by stable repeated invariants rather than draft prose.

## Next

Design the Requirements stage protocol as the first stage-methodology increment: define its inputs, responsibility, working loop, outputs, gate guarantees, reopen/block behavior and minimal context contract. Then challenge it against the top-level lifecycle before moving to Domain Design.
