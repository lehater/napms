# Active execution

Current: `PLAN-I21-configuration-rendering.md`

Goal: complete I21 Configuration Rendering with exact Cisco ASA first-slice semantics and no I22 execution leakage.

Current task: S5 final hosted gate and absorption.

## Working set

Read first:
- `docs/plans/active/PLAN-I21-configuration-rendering.md`
- `docs/requirements/configuration-rendering.md`
- `docs/domain/access-policy-realization/rendering-tactical-model.md`
- `docs/architecture/configuration-rendering-boundary.md`
- `src/napms/access_policy_realization/application/render.py`

Expand only if the gate failure points to another owner or implementation file.

## Blockers

Hosted PR gates must be green before I21 is absorbed and squash-merged. No semantic blocker is currently known.

## Gate

PR #45 is the final hosted gate. Required checks include core, harness, knowledge, PostgreSQL persistence and Docker local runtime.

## Next

Resolve any gate failure on `i21-configuration-rendering`. When all checks are green, absorb I21 into canonical engineering/roadmap state, remove the completed PLAN, set `Current: none`, promote I22 without selecting it, and squash-merge PR #45.

I22 Network Environment Operations remains downstream and must not be pulled into I21.