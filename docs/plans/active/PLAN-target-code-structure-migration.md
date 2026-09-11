# PLAN — Target Code Structure Migration

Status: `active`

## Goal

Finish the accepted structural migration without product/domain semantic change and leave the repository enforcing the actual final taxonomy:

```text
backend/src/napms/
  contexts/
  workflows/
  platform/

web/src/
  app/
  features/
  components/ui/
  lib/
```

## Inputs

- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`
- `docs/decisions/ADR-014-target-code-structure-taxonomy.md`

## Completed milestones

- M1 — backend repository boundary, `f0e281e`.
- M2 — bounded contexts, PR #74, `91eb009c2338697458ba3874836c93cc044f753a`.
- M3 — workflows and composition drain, PR #75, `18787e3f790368dec8d57078b47c7b6454e85b5d`.
- M4 — platform consolidation, PR #76, `a2caf39587c111fe97341686ff92fbeb9d30599d`; CI path correction PR #77, `10182694590b6b851d35b9594ecc03823cee811f`.
- M5 — justified ACC capability split, PR #78, `3bd5525061a382b77d6298ea5d607bd7f2f63179`.
- M6 — final Web locality, PR #79, `b33849978df76e1737ceb192ae68b840070e476e`.

## M7 — Compatibility purge and final enforcement

M7 removes only structural-migration compatibility debt and strengthens executable structure rules. Product/domain compatibility that is part of accepted I27/I31 behavior is out of scope.

Accepted purge scope:

1. Remove `contexts/application_catalogue/application/curation/structure.py`, which is a pre-M5 re-export facade. Consumers must import:
   - `CatalogueMutationOutcome` from context-wide `application.ports`;
   - Application mutation types/use cases from `curation.application_structure`;
   - Component mutation types/use cases from `curation.component_structure`.
2. Remove the transitional `find_active_references` dependency-port compatibility path:
   - target curation uses `summarize_active_references` directly;
   - target lifecycle uses `list_active_references(... offset=0, limit=1)` for the transactional recheck;
   - production adapters and test fakes implement only the final summary/page contract.
   The second transactional dependency check remains; only the obsolete interface compatibility is removed.
3. Replace stale/vacuous structure tests with final generic enforcement:
   - backend top-level taxonomy remains exactly `contexts / workflows / platform` plus package metadata;
   - bounded-context roots contain only applicable Clean Architecture layers;
   - workflow roots contain only applicable `application / infrastructure / presentation` layers;
   - no `adapters/` or `composition/` directory may reappear anywhere under production `napms`;
   - existing dependency-direction, cross-context and persistence-bypass guards remain effective.
4. Make canonical structure documentation describe the actual repository, not an in-progress migration. Mark the older I32 structure roadmap explicitly historical/superseded rather than current architectural guidance.

Do not remove accepted ACC compatibility projection/domain behavior, legacy-coexistence facts, historical ADRs/baselines, or transactional safety checks merely because their vocabulary contains `legacy` or `compatibility`.

## Exit criteria

M7 closes when:
- structural compatibility facades/fallback interfaces are removed;
- final topology/dependency guards are non-vacuous and protect the accepted taxonomy;
- canonical architecture docs describe actual code;
- full backend, Web, Harness, Knowledge, PostgreSQL and browser/runtime checks pass as applicable;
- the active migration plan is retired before the final hosted PR gate;
- one final milestone PR passes all required hosted gates and is squash-merged.

## Blockers

None.

## Next

Implement the M7 purge/enforcement package on `refactor/m7-final-enforcement`, run the complete local gate, then stop for architectural review. Do not create the final PR or retire the active plan before that review.
