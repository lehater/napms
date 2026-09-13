# Active execution

Current: `harness-change-lifecycle.md`

Goal: validate a coherent stage/gate change lifecycle from problem evidence to implementation readiness together with a paired context lifecycle that loads only the minimum rules/artifacts required for the current task.

Current task: close review findings around durable gate provenance, scoped G4 authorization and lifecycle regression coverage without changing product/domain/runtime code.

Lifecycle stage: `META`

Stage state: `GATE_FAILED`

Lifecycle basis: Hosted Harness run `34757515972` executed the remediation and failed only the active-plan context budget because the temporary `Read first` set exceeded 24 KiB.

Implementation authorization: `none`

Authorized scope: `none`

Authorization basis: `none`

## Working set

Read first:
- `docs/plans/active/harness-change-lifecycle.md`
- `tools/validate_plans.py`

Expand only if needed:
- `docs/process/plan-lifecycle.md` when changing lifecycle-lease semantics;
- `docs/process/change-lifecycle.md` for transition/authorization semantics;
- `.agents/skills/execute-work-package/SKILL.md` and `.agents/skills/implement-slice/SKILL.md` for execution routing;
- lifecycle eval/validator files while diagnosing regression coverage.

## Recovery facts

- All current Harness design changes belong only to branch `harness/change-lifecycle`; do not update or merge to `main` unless explicitly requested later.
- PR #101 exists only as the hosted CI surface for this branch and must remain unmerged unless explicitly requested later.
- Hosted Harness run `34756958245` passed the pre-remediation baseline on head `38baa0b7c53620290094fe8393118493d18f67c8`.
- Review remediation introduced a mandatory compact lifecycle lease, scoped/revocable G4 authorization and transition regression coverage.
- `execute-work-package` and `implement-slice` require the current scoped lease before routing/executing code changes.
- `validate_plans.py` now mechanically rejects IMPLEMENTATION without G4 and G4 outside IMPLEMENTATION.
- `validate_lifecycle_transitions.py` covers PASS/REWORK/BLOCKED/direct-entry/REOPEN/dirty/G4-revocation invariants and runs under `make harness-check`.
- Hosted run `34757515972` passed `validate_harness.py`; `validate_plans.py` correctly rejected the remediation capsule because its three `Read first` files totaled 30,741 bytes against the 24 KiB budget.
- The fix is to keep `plan-lifecycle.md` lazy for this validator/CI task rather than weakening the context budget.
- No product/domain/runtime code has been changed by this Harness workstream.

## Blockers

No external blocker. The deterministic gate must be rerun after the context-budget correction.

## Gate

Do not treat the remediation as accepted until hosted `make harness-check` passes on the final current head with lifecycle-lease validation and transition regression coverage included. No merge to `main` is authorized.

## Next

Rerun PR #101 Harness CI on this reduced working set, inspect the complete result/logs, and fix only concrete failures. If green, record acceptance and rerun once on the final recorded head.
