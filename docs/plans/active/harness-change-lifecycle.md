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

Status: coherent baseline captured in `docs/process/change-lifecycle.md`. `ACCEPTED` is upstream-relative; `REOPEN` invalidates only dependent downstream guarantees; no-progress and blocking semantics are explicit. Change this kernel only when real stage use exposes a concrete defect.

### H2 — Context lifecycle

Define minimal startup context, stage/task routing, lazy evidence loading, durable promotion/discard and session rollover.

Status: coherent baseline captured and aligned with `AGENTS.md`, `working-loop.md` and `plan-lifecycle.md`. The top-level lifecycle is a transition protocol, not a file to preload for every task. Stage transition/REOPEN is a strong compaction point; fresh-session rollover is the reliable unload mechanism.

### H3 — Existing Harness alignment

Align existing protocols/Skills with the lifecycle and remove overlapping progression models.

Status: aligned. `domain-change-protocol.md` is a focused re-entry helper; `decision-protocol.md` owns known/hypothesis/unknown/conflict semantics; `working-loop.md` owns execution/checkpoint/rollover mechanics; `plan-lifecycle.md` owns durable execution state; review/execution Skills defer stage progression to the lifecycle protocols.

### H4 — Stage methodology design

Design the minimum reusable methods/gates without inflating the always-loaded kernel.

Status: initial pre-code chain captured:
- `problem-evidence-stage.md` — S0/G0;
- `requirements-stage.md` — S1/G1;
- `domain-design-stage.md` — S2/G2 routing;
- `strategic-ddd-convergence.md` — Strategic DDD convergence;
- `tactical-ddd-stage.md` — Tactical DDD coherence;
- `architecture-stage.md` — S3/G3;
- `implementation-readiness-stage.md` — S4/G4.

Stage ownership follows statement meaning rather than file location, so mixed-level legacy/current artifacts can be revalidated incrementally without mass documentation migration.

### H5 — Deterministic validation

Automate only structural invariants that do not require semantic judgement.

Status: started. `tools/validate_harness.py` checks lifecycle-protocol presence/discoverability and key Skill boundaries such as S3 review routing and G4-before-implementation. Semantic gate verdicts remain judgement work.

### H6 — Real-change dry runs

Exercise the lifecycle/context model against representative repository changes and refine only demonstrated gaps.

Status: representative dry runs completed far enough to remove known P1 routing defects. Findings corrected:
- Strategic/Tactical switching inside S2 is an internal reroute, not top-level `REOPEN`;
- Strategic boundary/contract changes force revalidation of dependent Tactical assumptions before G2;
- upstream reopen during implementation suspends the affected slice and requires a fresh G4 before resumption;
- `execute-work-package` cannot bypass S4/G4 to reach `implement-slice`;
- a real `policy_export` peer-domain import case showed that S3 can distinguish a structural architecture leak from a missing semantic contract requiring `REOPEN(S2)`.

Direct S3, direct S4 and S0->S1 paths did not expose additional P1 routing defects: later-stage direct entry is valid only when the required upstream guarantees already exist and remain applicable.

### H7 — Context-cost and recovery audit

Validate that the lifecycle remains usable without context overload and that a fresh session can recover the next task from durable state.

Status: active. Current process files are intentionally lazy-loaded. Stage protocols are roughly 4.6–9.5 KiB each; `change-lifecycle.md` is heavier (~14 KiB) and therefore must remain transition-only. Do not introduce a generic shared stage framework merely to deduplicate prose if doing so forces every stage to load another file.

Audit next:
- fresh-session recovery from root routing + capsule + one Skill;
- whether `Read first` remains minimal after transition work;
- duplicated rules that create conflicting ownership rather than harmless local self-containment;
- whether any validator/file-size budget is justified by repeated evidence rather than arbitrary limits.

## Blockers

No semantic Harness blocker is known. Deterministic `make harness-check` execution is still pending because the current GitHub workflow has no `workflow_dispatch` and the current shell environment cannot obtain the branch through GitHub network resolution.

## Exit criteria

- upper-level Change Lifecycle and Context Lifecycle are coherent and non-overlapping with existing process ownership;
- S0-S4/G0-G4 responsibilities and reopen boundaries work on representative real changes;
- startup/recovery requires only a minimal capsule plus current protocol/Skill/working set;
- no material Harness state depends on conversation history;
- the model stops rather than loops when evidence/decisions do not progress;
- deterministic validators enforce structural routing without pretending to decide semantic gates;
- real-change dry runs reveal no unresolved P0/P1 Harness contradiction;
- context-cost/recovery audit reveals no unresolved P0/P1 progressive-disclosure defect;
- deterministic Harness validation has actually executed before this workstream is declared complete.

## Next

Run a fresh-session recovery/context-cost audit using only the durable startup path. Remove only demonstrated duplication or excessive startup loading. Keep `make harness-check` explicitly pending until an execution surface is available.
