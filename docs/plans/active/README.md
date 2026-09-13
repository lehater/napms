# Active execution

Current: `harness-change-lifecycle.md`

Goal: validate a coherent stage/gate change lifecycle from problem evidence to implementation readiness together with a paired context lifecycle that loads only the minimum rules/artifacts required for the current task.

Current task: preserve the reviewed Harness lifecycle/context baseline on `harness/change-lifecycle` and reopen it only when a real task exposes a concrete defect or extension need.

Lifecycle stage: `META`

Stage state: `ACCEPTED`

Lifecycle basis: H8 in `docs/plans/active/harness-change-lifecycle.md` plus the PR #101 Harness gate for the current branch head; the review-remediation design has no known P0/P1 defect.

Implementation authorization: `none`

Authorized scope: `none`

Authorization basis: `none`

## Working set

Read first:
- `docs/plans/active/harness-change-lifecycle.md`
- `.github/workflows/harness.yml`

Expand only if needed:
- `docs/process/change-lifecycle.md` when a real transition/reopen defect is demonstrated;
- `docs/process/plan-lifecycle.md` when lifecycle-lease semantics need revision;
- the affected validator/Skill/protocol only when a concrete failure points to it.

## Recovery facts

- All Harness design changes belong only to branch `harness/change-lifecycle`; do not update or merge to `main` unless explicitly requested later.
- PR #101 exists only as the hosted CI surface for this branch and must remain unmerged unless explicitly requested later.
- The Harness lifecycle is S0 Problem/Evidence -> S1 Requirements -> S2 Domain Design -> S3 Architecture -> S4 Implementation Readiness -> scoped G4 -> IMPLEMENTATION execution mode.
- `REOPEN(stage)` targets one top-level semantic owner stage; dependent downstream acceptances become dirty and affected G4 authorization is revoked.
- The active capsule now carries a mandatory machine-readable lifecycle lease: stage, state, lifecycle basis, implementation authorization, authorized scope and authorization basis.
- Code execution requires `Lifecycle stage: IMPLEMENTATION`, `Implementation authorization: G4 PASS`, matching `Authorized scope` and non-stale `Authorization basis`.
- `validate_plans.py` rejects invalid lease combinations and continues to enforce the capsule/working-set context budget.
- `validate_lifecycle_transitions.py` executes 15 regression cases covering PASS/REWORK/BLOCKED/direct entry/REOPEN/dirty propagation/G4 revocation and invalid transitions.
- Hosted run `34757555810` passed all four Harness checks on the remediation content before final accepted-state metadata was recorded.
- Hosted run `34757515972` demonstrated that the 24 KiB `Read first` budget catches real context regressions; the budget was preserved rather than weakened.
- No product/domain/runtime code has been changed by this Harness workstream.

## Blockers

No known P0/P1 Harness blocker.

## Gate

The accepted branch baseline is valid only while the Harness check on PR #101 is green for the current branch head. Any future Harness change makes that evidence stale and must rerun `make harness-check`. No merge to `main` is authorized.

## Next

Keep PR #101 in draft after the current-head Harness gate is green. Preserve this branch as the isolated Harness workstream and reopen design only when a real task demonstrates a concrete routing, context-loading, gate, provenance or methodology defect.
