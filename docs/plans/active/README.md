# Active execution

Current: `harness-change-lifecycle.md`

Goal: validate a coherent stage/gate change lifecycle from problem evidence to implementation readiness together with a paired context lifecycle that loads only the minimum rules/artifacts required for the current task.

Current task: preserve the validated Harness lifecycle/context baseline on `harness/change-lifecycle` and change it only when a new real use exposes a concrete defect or extension need.

Lifecycle stage: Harness meta-design / validated baseline.

Stage state: `ACCEPTED`.

## Working set

Read first:
- `docs/plans/active/harness-change-lifecycle.md`
- `.github/workflows/harness.yml`

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
- Hosted Harness run 34756842433 found the first capsule syntax defect (`Current:` was not an exact pointer).
- Hosted Harness run 34756887237 found the second capsule syntax defect (`Read first` bullets had trailing semicolons).
- Hosted Harness run 34756922628 on head `d2b8e2b08be15817599fad0975687c64f660ee68` passed `make harness-check` completely: `validate_harness.py`, `validate_plans.py`, and `validate_skill_routing.py` all passed.
- No product/domain/runtime code has been changed by this Harness workstream.

## Blockers

No known Harness blocker.

## Gate

Deterministic Harness gate passed on hosted run 34756922628 for the current validated baseline. Any future Harness change must rerun the applicable gate before being treated as validated. No merge to `main` is authorized.

## Next

Keep PR #101 in draft and continue using `harness/change-lifecycle` as the isolated Harness workstream. Reopen lifecycle design only when a real task demonstrates a concrete routing, context-loading, gate or methodology gap.
