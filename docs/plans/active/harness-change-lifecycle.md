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
  - minimal context loading and reliable rollover;
  - durable gate provenance and scoped implementation authorization;
  - executable lifecycle regression coverage.

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

Status: active and previously validated. `tools/validate_harness.py` checks lifecycle-protocol presence/discoverability and key Skill boundaries; `tools/validate_plans.py` enforces resume locality/context budget. Hosted Harness run `34756958245` passed the pre-review baseline on head `38baa0b7c53620290094fe8393118493d18f67c8`.

Current remediation extends this layer with lifecycle-lease validation and `tools/validate_lifecycle_transitions.py`. Semantic gate verdicts still remain judgement work; validators enforce only states/transitions that can be checked deterministically.

### H6 — Real-change dry runs

Exercise the lifecycle/context model against representative repository changes and refine only demonstrated gaps.

Status: representative dry runs completed far enough to remove known routing defects. Findings corrected:
- Strategic/Tactical switching inside S2 is an internal reroute, not top-level `REOPEN`;
- Strategic boundary/contract changes force revalidation of dependent Tactical assumptions before G2;
- upstream reopen during implementation suspends the affected slice and requires a fresh G4 before resumption;
- `execute-work-package` cannot bypass S4/G4 to reach `implement-slice`;
- a real `policy_export` peer-domain import case showed that S3 can distinguish a structural architecture leak from a missing semantic contract requiring `REOPEN(S2)`.

Direct S3, direct S4 and S0->S1 paths did not expose additional routing defects: later-stage direct entry is valid only when the required upstream guarantees already exist and remain applicable.

### H7 — Context-cost and recovery audit

Validate that the lifecycle remains usable without context overload and that a fresh session can recover the next task from durable state.

Status: passed manual/repository-structure review with no known P0/P1 progressive-disclosure defect.

Results:
- stage protocols remain lazy-loaded; each is roughly 4.6–9.5 KiB;
- `change-lifecycle.md` is heavier (~14 KiB) and remains transition-only;
- no generic shared stage framework was introduced because it would add a mandatory indirection/load to every stage;
- fresh-session recovery succeeds from root routing -> capsule -> primary Skill -> minimal `Read first` without loading `change-lifecycle.md` for ordinary work;
- `Read first` no longer repeats the primary Skill, and plan validation prevents routed AGENTS/Skill duplication;
- local self-containment inside one stage protocol is preferred over cross-file DRY when it reduces working-context fan-out;
- manual review of `execute-work-package`, `implement-slice` and `architecture-review` found no remaining known lifecycle bypass at that baseline.

### H8 — Review remediation: gate provenance and executable lifecycle

Close the key defects found by the Harness architecture review: prose-only G4 authorization, weak durable provenance and missing transition regressions.

Status: in progress.

Implemented in this increment:
- mandatory compact lifecycle lease in `docs/plans/active/README.md` for current non-trivial work;
- `IMPLEMENTATION` execution mode only after G4, without adding a new semantic design stage;
- scoped `G4 PASS` authorization with explicit `Authorized scope` and `Authorization basis`;
- automatic conceptual revocation of that lease on applicable upstream reopen/dirty assumptions;
- `execute-work-package` and `implement-slice` require the scoped lease before code execution;
- root `AGENTS.md` implementation order now requires that lease rather than merely "accepted behavior";
- `tools/validate_plans.py` rejects implementation state without a valid scoped lease and rejects G4 authorization outside implementation;
- `backend/tests/evals/lifecycle-transition-cases.json` captures PASS/REWORK/BLOCKED/direct-entry/REOPEN/dirty/G4-revocation cases;
- `tools/validate_lifecycle_transitions.py` executes those transition invariants;
- `make harness-check` and Harness workflow path filters include the new regression surface.

Remaining closure: run hosted Harness CI on the final remediation head and fix only concrete failures.

## Blockers

No external blocker. The current remediation is not accepted until deterministic Harness validation passes on its final head.

## Exit criteria

- upper-level Change Lifecycle and Context Lifecycle are coherent and non-overlapping with existing process ownership;
- S0-S4/G0-G4 responsibilities and reopen boundaries work on representative real changes;
- startup/recovery requires only a minimal capsule plus current protocol/Skill/working set;
- no material Harness state depends on conversation history;
- the model stops rather than loops when evidence/decisions do not progress;
- deterministic validators enforce structural routing without pretending to decide semantic gates;
- G4 implementation permission is scoped, durable, revocable and mechanically distinguishable from pre-code states;
- lifecycle transition regressions cover the key direct-entry/reopen/dirty paths;
- real-change dry runs reveal no unresolved P0/P1 Harness contradiction;
- context-cost/recovery audit reveals no unresolved P0/P1 progressive-disclosure defect;
- deterministic Harness validation has executed successfully on the final remediation head before this workstream is treated as accepted.

## Next

Run hosted `make harness-check` on PR #101 for the current remediation head, inspect the complete result/logs, fix only concrete failures, and rerun until green. Keep PR #101 draft except when toggling Ready specifically to request the hosted gate. Do not merge to `main` unless explicitly requested.
