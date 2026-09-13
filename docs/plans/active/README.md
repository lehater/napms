# Active execution

Current: `harness-change-lifecycle.md`

Goal: validate a coherent stage/gate change lifecycle from problem evidence to implementation readiness together with a paired context lifecycle that loads only the minimum rules/artifacts required for the current task.

Current task: fix the concrete Harness CI failure in active-plan validation, then rerun the hosted Harness gate on PR #101 without changing product/domain/runtime code.

Lifecycle stage: Harness meta-design / deterministic validation.

Stage state: `GATE_FAILED`.

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
- `.github/workflows/harness.yml` exposes `workflow_dispatch` and runs `make harness-check`.
- PR #101 exists only to exercise hosted CI for this branch; it must not be merged to `main` unless explicitly requested later.
- Hosted Harness run 34756842433 executed `make harness-check`: `validate_harness.py` passed; `validate_plans.py` failed because the capsule `Current:` line contained descriptive text after the backticked plan filename, violating its exact syntax contract.
- The concrete fix is to keep `Current:` as an exact pointer and move descriptive context elsewhere in the capsule.
- No product/domain/runtime code has been changed by this Harness workstream.

## Blockers

No external blocker. The current deterministic gate failed on a concrete active-plan format defect that is being corrected in this branch.

## Gate

Keep this workstream open until `make harness-check` executes successfully on the current `harness/change-lifecycle` head. Any failure must be fixed in this branch and rechecked. No merge to `main` is authorized.

## Next

Rerun the hosted Harness gate after this active-plan correction, inspect the complete result/logs, and fix only concrete failures. If the gate passes, record the successful run and return the PR to draft while Harness design work remains open.
