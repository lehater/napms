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

Status: coherent baseline captured in `docs/process/change-lifecycle.md`. `ACCEPTED` is upstream-relative; `REOPEN` invalidates only dependent downstream guarantees; no-progress and blocking semantics are explicit. Continue to change this kernel only when real stage use exposes a concrete defect.

### H2 — Context lifecycle

Define minimal startup context, stage/task routing, lazy evidence loading, durable promotion/discard and session rollover.

Status: coherent baseline captured and aligned with `AGENTS.md`, `working-loop.md` and `plan-lifecycle.md`. The top-level lifecycle is a transition protocol, not a file to preload for every task. Stage transition/REOPEN is a strong compaction point; fresh-session rollover is the reliable unload mechanism.

### H3 — Existing Harness alignment

Align existing protocols/Skills with the lifecycle and remove overlapping progression models.

Status: top-level alignment complete enough for real-use validation. `domain-change-protocol.md` is a focused re-entry helper; `decision-protocol.md` owns known/hypothesis/unknown/conflict semantics; `working-loop.md` owns execution/checkpoint/rollover mechanics; `plan-lifecycle.md` owns durable execution state; review/execution Skills now defer stage progression to the lifecycle protocols.

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

These remain hypotheses to validate through real changes. Existing mixed-level requirements/domain artifacts demonstrated that stage ownership must follow statement meaning rather than file location.

### H5 — Deterministic validation

Automate only structural invariants that do not require semantic judgement.

Status: started. `tools/validate_harness.py` now checks lifecycle-protocol presence/discoverability and key Skill boundaries such as S3 review routing and G4-before-implementation. Do not automate semantic gate verdicts or require draft lifecycle metadata universally before repeated use proves the contract.

### H6 — Real-change dry runs

Exercise the lifecycle/context model against representative repository changes and refine only demonstrated gaps.

Target cases:
- raw/ambiguous need requiring S0 -> S1;
- product behavior change requiring S1 -> S2;
- Strategic DDD boundary/contract change;
- Tactical-only invariant/identity change;
- architecture-only change;
- implementation-only change entering directly at S4;
- lower-stage finding causing multi-stage `REOPEN` and dirty revalidation.

Status: next active design increment.

## Blockers

No external blocker. The primary risk is further rule growth without evidence. New protocols/Skills/validators should now be added only when a dry run demonstrates a concrete gap.

## Exit criteria

- upper-level Change Lifecycle and Context Lifecycle are coherent and non-overlapping with existing process ownership;
- S0-S4/G0-G4 responsibilities and reopen boundaries work on representative real changes;
- startup/recovery requires only a minimal capsule plus current protocol/Skill/working set;
- no material Harness state depends on conversation history;
- the model stops rather than loops when evidence/decisions do not progress;
- deterministic validators enforce structural routing without pretending to decide semantic gates;
- real-change dry runs reveal no unresolved P0/P1 Harness contradiction.

## Next

Run representative real-change dry runs through the lifecycle, record only concrete Harness findings, and refine routing/context budgets/reopen semantics where the runs demonstrate a problem. Do not expand methodology speculatively.
