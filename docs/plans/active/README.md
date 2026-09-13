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
- Missing upstream truth becomes an explicit problem/unknown; lower layers must not invent it.
- Repetition without changed evidence/model/problem/decision state is a no-progress blockage.
- Stage protocols are lazy-loaded; the top-level lifecycle is a transition protocol, not permanent working context.
- `tools/validate_harness.py` checks only structural routing/discoverability boundaries, not semantic gate correctness.
- Dry runs so far found and corrected ambiguous internal S2 reopen semantics and implementation-WIP behavior on upstream reopen.

## Blockers

No external blocker. `make harness-check` is not executable through the current GitHub connector because the harness workflow has no `workflow_dispatch`; do not claim the deterministic gate passed without an execution surface.

## Gate

Do not declare the Harness lifecycle stable until representative dry runs cover direct-entry and reopen paths without unresolved P0/P1 routing/context defects. Do not add new global rules merely for completeness.

## Next

Continue dry runs for direct S3, direct S4, S0->S1 and multi-stage reopen cases; capture only demonstrated Harness defects, then review the accumulated branch diff and deterministic validation surface.
