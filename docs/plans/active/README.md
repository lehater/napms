# Active execution

Current: `harness-change-lifecycle.md` — isolated Harness lifecycle/context-management design on branch `harness/change-lifecycle`.

Goal: validate a coherent stage/gate change lifecycle from problem evidence to implementation readiness together with a paired context lifecycle that loads only the minimum rules/artifacts required for the current task.

Current task: run representative real-change dry runs through S0-S4/G0-G4 and refine only concrete routing, reopen or context-loading defects.

Lifecycle stage: Harness meta-design / real-change validation.

Stage state: `IN_PROGRESS`.

## Working set

Read first:
- `docs/plans/active/harness-change-lifecycle.md`;
- `docs/process/change-lifecycle.md`;
- `.agents/skills/agent-harness-design/SKILL.md`.

Expand only if needed:
- the one stage protocol exercised by the current dry run;
- the smallest real requirement/domain/architecture/code artifact used as test evidence;
- `docs/process/working-loop.md` when testing implementation re-entry/rollover;
- `docs/process/plan-lifecycle.md` when testing persistence/recovery;
- `tools/validate_harness.py` when changing deterministic structural validation.

## Recovery facts

- All current Harness design changes belong only to branch `harness/change-lifecycle`; do not update or merge to `main` unless explicitly requested later.
- The lifecycle has S0 Problem/Evidence -> S1 Requirements -> S2 Domain Design -> S3 Architecture -> S4 Implementation Readiness -> G4 code authorization.
- S2 contains Strategic and Tactical routes; switching between them is an internal S2 reroute, not top-level `REOPEN`.
- A Strategic ownership/boundary/contract change requires revalidation of only dependent Tactical assumptions before G2.
- `REOPEN(stage)` targets one top-level owner stage; dependent downstream acceptances become dirty and must be revalidated.
- If implementation triggers an upstream reopen, stop the affected slice, preserve WIP only as recoverable branch state, and do not resume until G4 is revalidated.
- `execute-work-package` must not route into `implement-slice` before applicable S4/G4 authorization.
- Missing upstream truth becomes an explicit problem/unknown; lower layers must not invent it.
- Repetition without changed evidence/model/problem/decision state is a no-progress blockage.
- Stage protocols are lazy-loaded; the top-level lifecycle is a transition protocol, not permanent working context.
- `tools/validate_harness.py` checks only structural routing/discoverability boundaries, not semantic gate correctness.
- Dry runs found and corrected: ambiguous Strategic/Tactical `REOPEN`, missing Tactical revalidation after Strategic change, missing implementation-WIP suspension on upstream reopen, and an execution-path G4 bypass.
- A real `policy_export` peer-domain import dry run confirmed S3 can distinguish a pure architecture leak from a missing semantic contract that requires `REOPEN(S2)`.

## Blockers

No semantic Harness blocker is known. The deterministic `make harness-check` gate is still pending because:
- `.github/workflows/harness.yml` has no `workflow_dispatch`, so the current GitHub connector cannot start an intermediate run;
- the current shell runtime cannot resolve `github.com`, so a temporary branch checkout for local `make harness-check` failed before repository execution.

Do not claim the deterministic gate passed until an execution surface becomes available.

## Gate

Do not declare the Harness lifecycle stable until representative dry runs cover direct-entry and reopen paths without unresolved P0/P1 routing/context defects and the deterministic Harness validation has actually executed. Do not add new global rules merely for completeness.

## Next

Continue the remaining direct-entry/S0 dry runs, then review the accumulated branch diff for duplication/context cost. Execute `make harness-check` when an execution surface is available; otherwise keep the deterministic gate explicitly pending.
