# Active execution

Current: `harness-change-lifecycle.md` — isolated Harness lifecycle/context-management design on branch `harness/change-lifecycle`.

Goal: validate a coherent stage/gate change lifecycle from problem evidence to implementation readiness together with a paired context lifecycle that loads only the minimum rules/artifacts required for the current task.

Current task: hold the lifecycle/context design stable and execute the deterministic Harness gate when an execution surface is available; change the model only if that gate or a new real use exposes a concrete defect.

Lifecycle stage: Harness meta-design / deterministic validation.

Stage state: `BLOCKED`.

## Working set

Read first:
- `docs/plans/active/harness-change-lifecycle.md`;
- `.github/workflows/harness.yml`.

Expand only if needed:
- `tools/validate_harness.py` and `tools/validate_plans.py` when diagnosing a deterministic failure;
- `docs/process/change-lifecycle.md` only if a new transition/reopen defect is demonstrated;
- the one affected Skill/protocol when a validation failure points to it.

## Recovery facts

- All current Harness design changes belong only to branch `harness/change-lifecycle`; do not update or merge to `main` unless explicitly requested later.
- S0-S4/G0-G4, Strategic/Tactical S2 routing, upstream reopen/dirty propagation and G4-before-code semantics have passed representative manual dry runs with no known P0/P1 Harness defect.
- Fresh-session/context-cost audit passed manual review: stage protocols are lazy-loaded, `change-lifecycle.md` is transition-only, and `Read first` does not duplicate routed AGENTS/Skill content.
- `execute-work-package`, `implement-slice` and `architecture-review` have been checked for lifecycle bypasses; none remain known.
- `tools/validate_harness.py` checks structural lifecycle routing/discoverability; `tools/validate_plans.py` checks resume locality/context budget. They do not decide semantic gate correctness.
- `.github/workflows/harness.yml` now exposes `workflow_dispatch` and runs `make harness-check`.
- The current GitHub connector can inspect/re-run existing workflow runs but cannot dispatch a new one.
- The current shell environment previously could not resolve `github.com`, so it could not obtain the branch for local execution.
- No product/domain/runtime code has been changed by this Harness workstream.

## Blockers

The only known blocker is deterministic execution of `make harness-check` on this branch. Repository capability now exists through `workflow_dispatch`, but the current connected GitHub tool cannot initiate a new workflow run and the current shell checkout path is unavailable.

Do not claim the gate passed until it actually executes.

## Gate

Keep this workstream open until `make harness-check` has executed successfully on `harness/change-lifecycle`. Any failure must be fixed in this branch and rechecked. No merge to `main` is authorized.

## Next

When an execution surface becomes available, run the Harness workflow (or local `make harness-check`) against `harness/change-lifecycle`, inspect failures/logs, fix only concrete issues, and record the result here. Until then, do not expand the lifecycle speculatively.
