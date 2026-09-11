# I32 Code Structure Refactoring

Status: `active`

Date: 2026-09-11.

## Goal

Align physical code ownership with the accepted context-first Clean/Hexagonal architecture so humans and agents can locate changes from their semantic owner, without changing product/domain semantics.

## Inputs

Canonical architecture and execution inputs:
- `docs/architecture/current-architecture.md`;
- `docs/architecture/code-structure.md`;
- `docs/engineering/current-state.md`;
- `docs/engineering/code-structure-refactoring-roadmap.md`;
- `AGENTS.md`, `src/AGENTS.md`, `web/AGENTS.md`;
- `docs/process/working-loop.md`.

Current structural evidence:
- `src/napms/runtime/`;
- `src/napms/composition/`;
- `src/napms/application_catalogue/`;
- `tests/architecture/test_dependency_rules.py`;
- `web/src/`.

## WP-0 — structure contract

Responsibility: establish the canonical structural target and bounded migration sequence before production-code moves.

Outputs:
- context-first / layers-second target made explicit;
- feature HTTP ownership rule made explicit;
- process/bootstrap responsibility separated from feature adapters;
- cross-context composition ownership protected from cosmetic relocation;
- no-big-bang migration rule;
- ordered M1-M6 roadmap with M1 as a reversible Application Catalogue HTTP pilot;
- durable Harness recovery state points to I32 WP-0.

Non-goals:
- no production-code relocation in WP-0;
- no API, domain, persistence or Web behavior change;
- no new bounded context/service/database;
- no `src/napms/modules/` nesting;
- no arbitrary large-file splitting.

Local exit: architecture, roadmap, navigation and active resume state agree; applicable Harness/knowledge gates are green; branch diff is documentation/Harness-state only.

## Later work packages

The ordered M1-M6 sequence and their gates are owned by `docs/engineering/code-structure-refactoring-roadmap.md`. Only the currently selected work package is expanded here when coordination detail is required.

The next candidate after WP-0 is M1, the Application Catalogue HTTP pilot:

```text
runtime/catalogue_target_http.py
runtime/catalogue_target_retirement_http.py
  -> application_catalogue/adapters/http/
```

M1 must preserve HTTP/API semantics and add executable architecture protection for the migrated boundary. M2 is not started until M1 demonstrates improved ownership locality without compensating indirection.

## Exit criteria

I32 exits only when the roadmap completion criterion is satisfied: feature code is reliably discoverable from its semantic owner, runtime/bootstrap is assembly-oriented, architecture tests protect migrated boundaries and current product journeys remain behaviorally unchanged.

For the current WP-0, exit is limited to the documentation/Harness contract described above; completing WP-0 does not imply I32 completion.

## Blockers

None known.

## Next

Complete WP-0 documentation/navigation, run the applicable Harness/knowledge checks, self-review the branch diff, then integrate WP-0 through one squash PR. After integration, recover from `main` and select M1 as the current work package.
