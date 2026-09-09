# Active execution

Current: `PLAN-033-i19-network-enforcement-placement.md`
Goal: Complete I19 Network Enforcement Placement without pulling I20 reconciliation or vendor/device mechanics forward.
Current task: WP-2 — add durable NEP-owned PostgreSQL knowledge and one strict local import adapter.

Working mode: implementation slice; primary Skill `implement-slice`.

## Working set

Read first:
- `docs/plans/active/PLAN-033-i19-network-enforcement-placement.md`
- `docs/architecture/network-enforcement-placement-boundary.md`
- `src/napms/network_enforcement_placement/domain/model.py`

Expand only if needed:
- `src/napms/technical_access_evidence/adapters/postgres/`
- `src/napms/technical_access_evidence/adapters/local_import.py`
- `src/napms/runtime/migrations.py`
- `tests/integration/`
- `pyproject.toml`

Recovery facts:
- WP-0 accepted the first-slice semantics.
- WP-1 core is implemented; isolated NEP tests pass 11/11 in the available execution environment.
- full repository-local `make test` remains unavailable because the tool environment cannot clone GitHub; final repository validation will use the PR hosted gate.
- PostgreSQL/schema/import code must preserve NEP ownership and fail closed; no peer SQL.

## Blockers

None for WP-2.

## Gate

WP-2 passes when strict source input persists/reloads NEP facts through a module-owned PostgreSQL schema and produces the same time-qualified selection semantics without cross-context persistence access.

## Next

Implement migration, repository/read adapter, strict local JSON import and PostgreSQL integration proof; then advance to WP-3 composition only after the durable path is coherent.
