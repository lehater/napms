# PLAN — Web UI convergence

Status: `active`

## Goal

Remove the parallel/legacy Web UI composition paths left after the component-composition migration so routed screens consistently use the shared design system for page geometry, catalogue/list composition, tables, controls, pagination, and detail structure while feature semantics remain feature-owned.

## Inputs

- Issue #93: Web UI convergence audit and implementation.
- `web/AGENTS.md` and `docs/ui/component-composition.md` define the ownership model.
- Current routed Web UI on `main`, including the target-catalogue family and remaining feature pages.
- Existing design-system primitives/components/patterns and `web/scripts/check-ui-boundaries.mjs`.

## Exit criteria

- Routed list/catalogue screens use common page/workspace/header/list composition instead of page-local width and shell rules.
- Target catalogue screens use design-system controls/tables/pagination and no longer depend on compatibility `components/ui`.
- Remaining feature imports from `@/components/ui/*` are removed where a durable design-system owner exists.
- Dead duplicate catalogue screens and superseded pager/composition helpers are removed when no longer referenced.
- Semantic visual tokens replace feature-level raw color literals in the migrated scope.
- Structural checks prevent reintroducing compatibility imports and parallel catalogue/list layout implementations.
- Applicable Web, Harness, Docker runtime, and browser journey gates are green on the same final PR head.

## Blockers

None. The active-plan index inherited from #91 is stale and is corrected as part of this increment.

## Next

Complete the repository-wide Web UI audit, classify remaining parallel composition paths, migrate them in coherent groups, remove dead compatibility paths, strengthen UI-boundary checks, then run the full final hosted gate before one squash merge.
