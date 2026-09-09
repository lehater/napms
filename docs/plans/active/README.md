# Active execution

Current: `PLAN-017-i17-technical-access-evidence-core.md`

Goal: close I17 Technical Access Evidence Core with complete executable evidence and canonical truth absorption.

Current task: WP4 — end-to-end proof and closure.

Working mode: architecture-review + execute-work-package.

## Working set

Read first:
- `docs/plans/active/PLAN-017-i17-technical-access-evidence-core.md`
- `docs/requirements/technical-access-evidence-acceptance-examples.md`

Expand only if needed into:
- `docs/domain/technical-access-evidence/tactical-model.md`;
- TAE Domain/Application/adapters;
- dedicated TAE/PostgreSQL integration tests;
- current-state/roadmap canonical truth;
- final architecture and workflow gates.

## Recovery facts

- WP0 Tactical DDD, WP1 core, WP2 PostgreSQL persistence and WP3 local/import durable proof are complete.
- WP3 hosted gates on `4da9e651`: core #98 (454 passed), postgres #83 (105 passed), docker #59, harness #103, knowledge #67 — all success.
- `Configured | TrafficDerived | Imported` remain evidence kinds, never authorization.
- Imported local source path is strict/all-or-nothing and has no Access Policy side effect.
- No current/fresh selection, coverage/confidence conclusion, domain resolution, placement or reconciliation exists in I17.
- No public TAE HTTP/Web or human authority workflow exists.

## Blockers

None identified before WP4 review.

## Gate

WP4 must:
- map accepted examples/exit criteria to executable evidence;
- run P0-P3 architecture review and close all P0/P1 findings;
- confirm no I18/I19/I20 leakage;
- absorb stable I17 outcomes into canonical domain/requirements/architecture/engineering truth;
- run final core/postgres/docker/harness/knowledge gates on the closure head;
- remove this active PLAN only after the final gates are green;
- promote I18 in roadmap/current-state, but do not start I18 implementation.

## Next

Execute I17 final closure. Stop after I17 is absorbed and I18 is only the next roadmap increment.
