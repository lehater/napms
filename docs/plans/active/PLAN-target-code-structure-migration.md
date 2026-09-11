# PLAN — Target Code Structure Migration

Status: `active`

## Goal

Move NAPMS to the accepted final physical taxonomy without product/domain semantic change:

```text
backend/src/napms/
  contexts/
  workflows/
  platform/
```

## Inputs

- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`
- `docs/decisions/ADR-014-target-code-structure-taxonomy.md`

## Execution order

```text
M1 backend repository boundary
-> M2 bounded contexts + final Clean layers
-> M3 workflows + remove generic composition
-> M4 platform consolidation
-> M5 capability-oriented internals where justified
-> M6 Web final locality
-> M7 compatibility purge + final enforcement
```

## Completed milestones

- M1 — complete in `f0e281e`.
- M2 — complete in PR #74, squash merge `91eb009c2338697458ba3874836c93cc044f753a`.
- M3 — complete in PR #75, squash merge `18787e3f790368dec8d57078b47c7b6454e85b5d`.
- M4 — complete in PR #76, squash merge `a2caf39587c111fe97341686ff92fbeb9d30599d`; post-merge CI path-filter correction complete in PR #77, squash merge `10182694590b6b851d35b9594ecc03823cee811f`.

## M5 — Capability-oriented internals

Status: `implementation and architectural review complete; final PostgreSQL evidence and hosted PR gates pending` on branch `refactor/m5-capability-internals`.

M5 refines only application layers where actual change locality shows independent responsibilities. File size alone is not a reason to split. M5 is one milestone PR and hosted gates run once at the end.

### Accepted split — Application Catalogue

Application Catalogue has sufficient evidence for capability decomposition: its application layer contains separate curation, discovery/read, and accepted I31 Application Catalogue Target responsibilities. The split is intentionally coarse; there is no one-folder-per-use-case convention.

Final application shape:

```text
contexts/application_catalogue/application/
  __init__.py
  ports.py
  curation/
  discovery/
  target/
```

`curation/` owns retained general catalogue mutation use cases and shared catalogue truth.

`discovery/` owns catalogue/detail/participant/interaction discovery and resolve-oriented reads.

`target/` owns the accepted I31 Application Catalogue Target contract and use cases. `target` is accepted requirement terminology, not a temporary generic bucket.

Architecture review confirms:
- application root contains only `__init__.py`, `ports.py`, and the three capability packages;
- mapped legacy flat modules are absent and consumers use final imports;
- `target` does not import `curation` or `discovery`;
- `curation` and `discovery` do not import `target`;
- common `CatalogueMutationOutcome` was moved to the context-wide application contract surface because it is consumed across capability boundaries;
- target compatibility-binding calls use consumer-side structural contracts rather than importing curation implementation types;
- product/domain behavior is preserved.

Validation:
- targeted Application Catalogue: 151 passed;
- architecture: 67 passed;
- `make test`: 810 passed, 141 deselected;
- `make harness-check`: passed;
- `make knowledge-check`: passed.

### Resource Catalogue review

Resource Catalogue was evaluated as the only secondary M5 candidate and is intentionally **not** decomposed further in this milestone.

Reason: current read/workspace behavior spans Resource core state plus effective realization, scope affiliation and responsibility; temporal mutation use cases share one repository/temporal contract. Additional packages would introduce artificial cross-capability coupling rather than improve demonstrated change locality. Large files alone are not sufficient evidence.

Access Policy and the remaining contexts/workflows likewise do not justify additional M5 package depth.

## Exit criteria

M5 closes when the accepted ACC capability split remains behavior-preserving, architecture/locality guards pass, a real PostgreSQL integration run passes without skips, and one final M5 PR passes all required hosted gates.

## Blockers

None.

## Next

Run final PostgreSQL integration evidence for M5. If green, open one M5 milestone PR, run required hosted gates, and squash-merge. Do not start M6 before M5 is merged.
