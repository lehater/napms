# Active-plan lifecycle

## Purpose

`docs/plans/active/README.md` is the single durable pointer to current non-trivial execution.

A new session must be able to recover:
- current plan;
- goal;
- current stage;
- accepted inputs;
- blockers;
- exit criteria;
- next stage.

## Rules

- Keep only current/planned execution artifacts under `docs/plans/active/`.
- One plan is current unless the index explicitly declares independent parallel work.
- A completed plan is absorbed into canonical product/domain/architecture/engineering truth and removed from `active/`.
- Git history preserves completed plan history.
- Do not mirror the current execution pointer in root `AGENTS.md` or other documents.

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
