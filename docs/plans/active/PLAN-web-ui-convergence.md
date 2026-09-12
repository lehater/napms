# PLAN — Web UI convergence

Status: `active`

## Goal

Remove the parallel/legacy Web UI composition paths left after the component-composition migration so routed screens consistently use the shared design system for page geometry, catalogue/list composition, tables, controls, pagination, detail structure, and global visual styling while feature semantics remain feature-owned.

## Inputs

- Issue #93: Web UI convergence audit and implementation.
- `web/AGENTS.md` and `docs/ui/component-composition.md` define the ownership model.
- Current routed Web UI on `main`, including the target-catalogue family and remaining feature pages.
- Existing design-system primitives/components/patterns, `web/src/design-system/tokens.css`, and `web/scripts/check-ui-boundaries.mjs`.

## Exit criteria

- Routed list/catalogue screens use common page/workspace/header/list composition instead of page-local width and shell rules.
- Target catalogue screens use design-system controls/tables/pagination and no longer depend on compatibility `components/ui`.
- Remaining feature imports from `@/components/ui/*` are removed where a durable design-system owner exists.
- Dead duplicate catalogue screens and superseded pager/composition helpers are removed when no longer referenced.
- Reusable visual constants are owned by `tokens.css`/design-system: feature code contains no raw palette values, local fixed page-width constants, repeated arbitrary typography/radius/shadow constants, or numeric table-width contracts.
- Page width uses semantic `PageWorkspace` presets; table geometry uses semantic `DataTable` width presets whose concrete dimensions are token-owned.
- Feature tables compose the shared `DataTable` pattern rather than rendering manual HTML tables.
- Structural checks reject legacy UI ownership, raw feature-level design constants, local page widths, numeric table widths, and manual feature tables.
- Applicable Web, Harness, Docker runtime, and browser journey gates are green on the same final PR head.

## Blockers

None.

## Next

Run the strict Web ownership/build gate, resolve any remaining convergence findings, update the durable guidance, then run the complete Web + Harness + Docker + browser journey gate on one final head before the active-plan cleanup and one squash merge.
