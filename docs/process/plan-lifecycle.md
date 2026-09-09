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
