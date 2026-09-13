# Active execution

Current: `harness-change-lifecycle.md`

Goal: validate a coherent stage/gate change lifecycle from problem evidence to implementation readiness together with a paired context lifecycle that loads only the minimum rules/artifacts required for the current task.

Current task: close review findings around durable gate provenance, scoped G4 authorization and lifecycle regression coverage without changing product/domain/runtime code.

Lifecycle stage: `META`

Stage state: `IN_PROGRESS`

Lifecycle basis: Harness architecture review findings on durable gate provenance, scoped G4 authorization and lifecycle regression coverage; current work is isolated to `harness/change-lifecycle`.

Implementation authorization: `none`

Authorized scope: `none`

Authorization basis: `none`

## Working set

Read first:
- `docs/plans/active/harness-change-lifecycle.md`
- `docs/process/plan-lifecycle.md`
- `tools/validate_plans.py`

Expand only if needed:
- `docs/process/change-lifecycle.md` for transition/authorization semantics;
- `.agents/skills/execute-work-package/SKILL.md` and `.agents/skills/implement-slice/SKILL.md` for execution routing;
- lifecycle eval/validator files while adding regression coverage.

## Recovery facts

- All current Harness design changes belong only to branch `harness/change-lifecycle`; do not update or merge to `main` unless explicitly requested later.
- PR #101 exists only as the hosted CI surface for this branch and must remain unmerged unless explicitly requested later.
- Hosted Harness run 34756958245 passed `make harness-check` on head `38baa0b7c53620290094fe8393118493d18f67c8` before the current review-remediation changes.
- The review identified the remaining key P1 class: lifecycle/G4 guarantees were stronger in prose than in durable machine-checked state.
- `plan-lifecycle.md` now defines a compact mandatory lifecycle lease in the capsule.
- G4 authorization is scoped to one implementation slice/scope, requires an explicit basis, and is revoked by applicable upstream reopen/dirty state.
- `IMPLEMENTATION` is an execution mode after G4, not a new semantic design stage.
- `execute-work-package` and `implement-slice` now require the current scoped lease before routing/executing code changes.
- No product/domain/runtime code has been changed by this Harness workstream.

## Blockers

No external blocker. Deterministic validation must be extended and rerun after the lifecycle-lease changes.

## Gate

Do not treat the remediation as accepted until hosted `make harness-check` passes on the final current head with lifecycle-lease validation and transition regression coverage included. No merge to `main` is authorized.

## Next

Extend `validate_plans.py` for the lifecycle lease, add executable transition regression cases, wire them into `make harness-check`, then run PR #101 CI and fix only concrete failures.
