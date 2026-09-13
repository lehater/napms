# Active-plan lifecycle

## Purpose

`docs/plans/active/README.md` is the single durable resume capsule for current non-trivial execution.

A fresh session must be able to recover the current task without reading prior conversation history or the full plan. The capsule should provide:
- current plan;
- goal;
- current task;
- minimal working set;
- compact recovery facts that materially constrain the task;
- blockers;
- current lifecycle stage/state and basis;
- current gate;
- implementation authorization when code execution is active;
- next action.

The full `PLAN-*.md` is the coordination artifact for work-package definitions/dependencies, overall goal, plan-level inputs, blockers, exit criteria and future stages. It does not own the mutable current-task pointer and is not mandatory startup context for ordinary execution.

## Context problem registers, roadmaps and active plans

Three planning artifacts serve different purposes and must not be collapsed into one.

```text
docs/engineering/context-problems/<context>.md
    = durable record of unresolved context-local problems, gaps, questions and blockers

docs/engineering/roadmaps/<context>.md
    = optional durable sequence only when an evidence-backed ordering is worth preserving

docs/plans/active/PLAN-*.md
    = only the work package being executed now
```

### Context problem register — default parking artifact

After discovery/revalidation of a bounded context, preserve unresolved work primarily as a **context problem register** rather than inventing a roadmap.

A problem register records what remains unresolved without asserting a total execution order. It may capture only causal dependencies that are actually known.

Use it to preserve:
- accepted/fixed starting constraints needed to understand the gaps;
- open design/domain/architecture problems;
- open questions or decisions;
- known target-versus-current gaps;
- actual dependencies between problems;
- implementation blockers/gates;
- evidence still needed;
- revisit triggers.

A problem register is not domain truth, not prioritization and not current execution state. Semantic decisions belong in their canonical domain/requirements/architecture/decision owner first; the register then removes or updates the corresponding open item.

Do not encode speculative sequencing such as `P1 -> P2 -> P3` merely because the questions were discovered in that order. Record `P2 depends on P1` only when solving P2 genuinely requires P1.

The context-problem registry and naming convention live in `docs/engineering/context-problems/README.md`.

### Context roadmap — optional, not default

Create a context roadmap only when there is a durable, evidence-backed reason to preserve an ordered sequence, for example:
- hard technical or semantic dependencies impose an order;
- an accepted migration must cross explicit compatibility stages;
- rollout/rollback constraints require staged execution;
- a committed delivery sequence remains useful current engineering truth.

A roadmap is expected to become stale more readily than a problem register. Revalidate its assumptions before using it to select work. If its sequence is no longer justified, collapse durable unresolved content back into the context problem register and remove/supersede the roadmap rather than maintaining fictional order.

Do not create a roadmap merely to list all known future work.

### Active plan — current execution only

`docs/plans/active/` contains only selected current/planned execution artifacts. A parked context does not keep an active `PLAN-*.md` merely to remember unresolved work.

When switching away from a context:
1. absorb accepted semantic decisions into their canonical owners;
2. update its context problem register with remaining gaps/questions/dependencies/blockers;
3. update an existing roadmap only if its ordering remains justified;
4. remove the context's active `PLAN-*.md` after current execution state no longer needs it;
5. update the active resume capsule to the newly selected workstream or `Current: none.`.

When resuming a context:
1. read its canonical context truth first;
2. read its problem register to recover unresolved work;
3. revalidate affected dependencies/evidence because they may have changed while parked;
4. consult a context roadmap only if one exists and its ordering is still valid;
5. select the concrete problem/increment to execute;
6. create/select a new active `PLAN-*.md` for that work;
7. update `docs/plans/active/README.md`.

### Project-wide planning

A project-wide roadmap may use context problem registers as planning inputs to choose priorities and cross-context sequencing.

Project-wide prioritization owns the order in which contexts/problems are tackled. It should reference context-local problem detail instead of copying it. A global priority does not automatically become a context-local roadmap, and a context problem register never makes work active.

Do not create empty problem-register or roadmap placeholders merely to mirror the list of bounded contexts. Create a register after concrete unresolved work has been discovered; create a roadmap only after concrete sequencing has been justified.

## Rules

- Keep only current/planned execution artifacts under `docs/plans/active/`.
- One plan is current unless the index explicitly declares independent parallel work.
- `docs/plans/active/README.md` is the only owner of the mutable current task/stage/state pointer and current implementation authorization.
- Keep the resume capsule compact; it is a startup index, not a second plan or a serialized process history.
- The capsule's `Read first` working set names only repository files not already loaded by routing that a fresh session should inspect before doing the current task. Do not repeat root/scoped `AGENTS.md` or the primary Skill there; secondary Skills/protocols belong under lazy expansion until the task demonstrates need.
- Expand beyond `Read first` only when evidence requires more context.
- Capsule recovery facts are non-authoritative summaries. Canonical domain/requirements/architecture/engineering artifacts win on conflict; refresh a stale capsule immediately.
- When current task, stage/state, lifecycle basis, implementation authorization, blocker, gate or next action changes materially, update the capsule.
- When a completed plan has been absorbed and the next increment has not yet been selected, the index may state `Current: none.`; in that state no `PLAN-*.md` file remains under `active/`.
- A completed plan is absorbed into canonical product/domain/architecture/engineering truth and removed from `active/`.
- Git history preserves completed plan history.
- Do not mirror the current execution pointer in root `AGENTS.md` or other documents.

## Lifecycle execution lease

For every current non-trivial workstream, the capsule carries a small machine-readable lifecycle lease. It is intentionally not a serialized workflow engine.

Required fields when `Current` is not `none`:

```text
Lifecycle stage: `S0|S1|S2|S3|S4|IMPLEMENTATION|META`
Stage state: `NOT_STARTED|IN_PROGRESS|BLOCKED|GATE_FAILED|ACCEPTED|DIRTY`
Lifecycle basis: <concise canonical references / gate evidence / trigger proving this state>
Implementation authorization: `none|G4 PASS`
Authorized scope: `none|<stable scope or slice reference>`
Authorization basis: `none|<G4/upstream references establishing the authorization>`
```

Rules:

- `S0`..`S4` are the semantic lifecycle stages from `change-lifecycle.md`.
- `IMPLEMENTATION` is an execution mode entered only after G4; it is not a new semantic design stage.
- `META` is reserved for Harness/process work that is itself outside the product S0-S4 lifecycle.
- `Lifecycle basis` must be sufficient for a fresh session to locate why the current stage/state is valid. It should reference canonical artifacts, accepted decision IDs, gate evidence or an explicit current trigger rather than restating long reasoning.
- `Implementation authorization: G4 PASS` is a scoped execution lease, not a global permission to edit arbitrary code.
- A G4 lease requires a non-`none` `Authorized scope` and non-`none` `Authorization basis`, and the lifecycle stage must be `IMPLEMENTATION`.
- Outside `IMPLEMENTATION`, implementation authorization, authorized scope and authorization basis are `none`.
- A `REOPEN(S0..S3)` or any upstream change that makes the authorized assumptions dirty immediately revokes the G4 lease: move out of `IMPLEMENTATION`, set authorization/scope/basis to `none`, and re-enter the owning upstream stage.
- A different implementation slice requires its own applicable G4 authorization; authorization for slice A must not be reused for slice B merely because both are in the same plan.
- The lease records current authority to proceed. Historical stage-by-stage provenance remains in canonical artifacts, ADRs, the active plan where useful, and Git history rather than being duplicated into the capsule.

This closes the gap between prose gates and executable routing: implementation Skills may rely on a visible scoped lease, while validators can reject code-execution state with no G4 authorization.

## Context budget

When `Current` is not `none`:
- the resume capsule must remain at most 6 KiB;
- `Read first` contains at most 5 existing repository files;
- the total tracked size of `Read first` files must remain at most 24 KiB;
- larger or secondary evidence belongs under lazy `Expand only if needed` guidance.

The budget is a guardrail for startup locality, not a limit on how much evidence an agent may inspect after the task demonstrates the need.

## Minimum resume-capsule contract

When `Current` is not `none`, `docs/plans/active/README.md` must make these fields easy to identify:
- `Current:`
- `Goal:`
- `Current task:`
- `Lifecycle stage:`
- `Stage state:`
- `Lifecycle basis:`
- `Implementation authorization:`
- `Authorized scope:`
- `Authorization basis:`
- `## Working set`
- `Read first:`
- `## Blockers`
- `## Gate`
- `## Next`

The lifecycle lease is mandatory because it controls whether lower-layer execution is authorized. Keep values compact; detailed reasoning belongs in the canonical owner or active plan.

## Minimum plan contract

Each active plan must contain:
- `Status`;
- `Goal`;
- `Inputs`;
- `Exit criteria`;
- `Blockers`;
- `Next`.

Material plans may define ordered work packages, decision questions, primary methods, working artifacts and local exits. The active capsule selects which work package/task is current.
