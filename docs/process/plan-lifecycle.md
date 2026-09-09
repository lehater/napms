# Active-plan lifecycle

## Purpose

`docs/plans/active/README.md` is the single durable resume capsule for current non-trivial execution.

A fresh session must be able to recover the current task without reading prior conversation history or the full plan. The capsule should provide:
- current plan;
- goal;
- current task/stage;
- minimal working set;
- accepted facts that materially constrain the task;
- blockers;
- current gate;
- next action.

The full `PLAN-*.md` remains the coordination artifact for work-package dependencies, future stages, overall exit criteria and planning decisions. It is not mandatory startup context for ordinary execution.

## Rules

- Keep only current/planned execution artifacts under `docs/plans/active/`.
- One plan is current unless the index explicitly declares independent parallel work.
- Keep the resume capsule compact; it is a startup index, not a second plan.
- The capsule's working set names only the files/code a fresh session should inspect first. Expand beyond it only when the current task requires more evidence.
- When current task, blocker, gate or next action changes materially, update the capsule.
- When a completed plan has been absorbed and the next increment has not yet been selected, the index may state `Current: none.`; in that state no `PLAN-*.md` file remains under `active/`.
- A completed plan is absorbed into canonical product/domain/architecture/engineering truth and removed from `active/`.
- Git history preserves completed plan history.
- Do not mirror the current execution pointer in root `AGENTS.md` or other documents.

## Minimum resume-capsule contract

When `Current` is not `none`, `docs/plans/active/README.md` must make these fields easy to identify:
- `Current:`
- `Goal:`
- `Current task:`
- `## Working set`
- `## Blockers`
- `## Gate`
- `## Next`

Working mode / primary Skill and a compact accepted-facts section are encouraged when they reduce rediscovery.

## Minimum plan contract

Each active plan must contain:
- `Status`;
- `Goal`;
- `Current stage`;
- `Inputs`;
- `Exit criteria`;
- `Blockers`;
- `Next`.

Material work packages may add decision question, primary method, working artifact and local exit.
