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
- current gate;
- next action.

The full `PLAN-*.md` is the coordination artifact for work-package definitions/dependencies, overall goal, plan-level inputs, blockers, exit criteria and future stages. It does not own the mutable current-task pointer and is not mandatory startup context for ordinary execution.

## Context roadmaps versus active plans

A bounded context may have a durable context-specific roadmap even when no work on that context is currently active.

Use:

```text
docs/engineering/roadmaps/<context>.md
    = durable ordered future work for one bounded context

docs/plans/active/PLAN-*.md
    = only the work package being executed now
```

A context roadmap is appropriate when discovery/design has identified a useful ordered sequence of unresolved design, migration or implementation work that must survive a workstream switch. It is not domain truth and must link to the canonical domain/requirements/architecture/decision artifacts that own semantics.

A context roadmap may be `active`, `parked` or `complete` as an engineering planning artifact. `parked` means:
- the roadmap remains valid future guidance;
- its next stage/re-entry point is recorded;
- its implementation/design gates remain explicit;
- no active `PLAN-*.md` is kept merely to remember the parked work;
- `docs/plans/active/README.md` points to another current plan or to `Current: none.`.

When switching away from a context:
1. absorb accepted semantic decisions into their canonical owners;
2. update the context roadmap with current state, next stage and any revisit trigger;
3. remove the context's active `PLAN-*.md` after the current execution state no longer needs it;
4. update the active resume capsule to the newly selected workstream or `Current: none.`.

When resuming a parked context:
1. read its canonical context truth first;
2. read the context roadmap to recover ordered future work and the recorded next stage;
3. revalidate any upstream dependencies that may have changed;
4. create/select a new active `PLAN-*.md` for the stage actually being executed;
5. update `docs/plans/active/README.md` to that active stage.

Project-wide roadmaps and context roadmaps are different planning levels. A later project-wide roadmap may use context roadmaps as inputs to prioritize or sequence work across bounded contexts; it does not make every context roadmap active and does not replace their local detail.

Do not create empty roadmap placeholders merely to mirror the list of bounded contexts. Add a context roadmap when concrete unresolved work has been identified and preserving its sequence has value.

The context-roadmap registry and naming convention live in `docs/engineering/roadmaps/README.md`.

## Rules

- Keep only current/planned execution artifacts under `docs/plans/active/`.
- One plan is current unless the index explicitly declares independent parallel work.
- `docs/plans/active/README.md` is the only owner of the current task/stage.
- Keep the resume capsule compact; it is a startup index, not a second plan.
- The capsule's `Read first` working set names only the files a fresh session should inspect before doing the current task. Expand beyond it only when evidence requires more context.
- Capsule recovery facts are non-authoritative summaries. Canonical domain/requirements/architecture/engineering artifacts win on conflict; refresh a stale capsule immediately.
- When current task, blocker, gate or next action changes materially, update the capsule.
- When a completed plan has been absorbed and the next increment has not yet been selected, the index may state `Current: none.`; in that state no `PLAN-*.md` file remains under `active/`.
- A completed plan is absorbed into canonical product/domain/architecture/engineering truth and removed from `active/`.
- Git history preserves completed plan history.
- Do not mirror the current execution pointer in root `AGENTS.md` or other documents.

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
- `## Working set`
- `Read first:`
- `## Blockers`
- `## Gate`
- `## Next`

Working mode / primary Skill and a compact recovery-facts section are encouraged when they reduce rediscovery.

## Minimum plan contract

Each active plan must contain:
- `Status`;
- `Goal`;
- `Inputs`;
- `Exit criteria`;
- `Blockers`;
- `Next`.

Material plans may define ordered work packages, decision questions, primary methods, working artifacts and local exits. The active capsule selects which work package/task is current.
