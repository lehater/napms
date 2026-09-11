# I32 Code Structure Refactoring

Status: `active`

Date: 2026-09-11.

## Goal

Align physical code ownership with the accepted context-first Clean/Hexagonal architecture so humans and agents can locate changes from their semantic owner, without changing product/domain semantics.

Execution roadmap: `docs/engineering/code-structure-refactoring-roadmap.md`.
Architecture contract: `docs/architecture/code-structure.md`.

## Current work package — M0 structure contract

Responsibility: establish the canonical structural target and bounded migration sequence before production-code moves.

Working set:
- `docs/architecture/code-structure.md`;
- `docs/engineering/code-structure-refactoring-roadmap.md`;
- `docs/plans/README.md`;
- `docs/plans/active/README.md`;
- `docs/architecture/README.md`;
- Harness/process rules only if a concrete inconsistency requires correction.

Outputs:
- context-first / layers-second target made explicit;
- feature HTTP ownership rule made explicit;
- process/bootstrap responsibility separated from feature adapters;
- cross-context composition ownership protected from cosmetic relocation;
- no-big-bang migration rule;
- ordered M1-M6 roadmap with M1 as a reversible Application Catalogue HTTP pilot;
- durable Harness recovery state points to I32 M0.

Non-goals:
- no production-code relocation in M0;
- no API, domain, persistence or Web behavior change;
- no new bounded context/service/database;
- no `src/napms/modules/` nesting;
- no arbitrary large-file splitting.

## Gate / local exit

M0 exits when:
- architecture, roadmap and active execution artifacts agree;
- architecture/plans navigation points to the new artifacts;
- `make harness-check` and `make knowledge-check` are green, or equivalent hosted evidence is inspected if local execution is unavailable;
- final diff contains documentation/Harness-state changes only.

## Next stage after M0 integration

M1 is the Application Catalogue HTTP pilot:

```text
runtime/catalogue_target_http.py
runtime/catalogue_target_retirement_http.py
  -> application_catalogue/adapters/http/
```

M1 must preserve HTTP/API semantics and add executable architecture protection for the migrated boundary. M2 is not started until M1 demonstrates improved ownership locality without compensating indirection.

## Blockers

None known.

## Next

Complete M0 documentation/navigation, run the applicable Harness/knowledge checks, self-review the branch diff, then open/finish the M0 PR. After squash integration, recover from `main` and select M1 as the current work package.
