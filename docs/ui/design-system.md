# NAPMS UI design system

Status: Resource Catalogue reference behavior implemented through PR #89.

The accepted Resource Catalogue concept board under `docs/ui/references/resource-catalogue/` is the visual baseline for NAPMS. Product/domain semantics remain owned by canonical requirements/domain/architecture artifacts; this document owns reusable visual/layout rules derived from that baseline.

## Layering

```text
semantic tokens
  -> primitives/components
    -> layout
      -> product patterns
        -> feature pages
```

Features supply domain data and actions. They must not recreate shared geometry or control styling.

## Global invariants

- Desktop workspace uses the full width available after the sidebar.
- Page-root arbitrary `max-width` is not used for operational/data/detail workspaces.
- Width constraints are allowed only for semantic cases such as dialogs, forms or readable prose.
- Features do not introduce raw hex colors when a semantic token exists.
- Shared controls, status visuals, tags, page states and table structure come from the design system.
- React reuse is by composition, not page inheritance or a monolithic prop-driven universal page.
- A feature may map domain meaning to a visual tone, but generic design-system components must not encode Resource/Application/etc. semantics.
- The signed-in account remains visible in the lower-left desktop sidebar; display only actor data actually supplied by authentication.

## Reference catalogue anatomy

The canonical catalogue slice is composed as:

```text
AppShell
  Sidebar
    Brand
    grouped Navigation
    User/Logout
  PageWorkspace
    PageHeader
      title
      description
      primary action
    CatalogueSurface
      CatalogueToolbar
        SearchInput
        CatalogueFilterBar
          CatalogueFilterField*
          actions
      CatalogueViewBar
        counted FilterChip presets
        optional view actions
      DataTable
        selection column
        sortable header cells
        rows
          Checkbox
          primary link/cell
          reference text
          technical values
          TagList
          StatusIndicator
          IssueIndicator
      CataloguePaginationControls
        result summary
        numbered pager
        rows-per-page selector
```

The Resource Catalogue is the executable reference implementation.

## Visual calibration from the accepted board

The reference crop is treated as an implementation reference rather than an abstract mood board. Its executable targets include:

- desktop sidebar: `232px`;
- workspace padding: `24px`;
- page title: about `20px` with compact line-height;
- primary/search/filter controls: about `38px` high;
- quick filters: about `28px` high;
- table header: about `40px` high;
- table rows: about `40px` high;
- selection column: about `48px`;
- table cells: compact horizontal padding (`12px`);
- table itself owns its border/radius; toolbar, quick filters and pagination are not wrapped in a large card;
- lifecycle inside catalogue rows is dot + text, not a filled badge;
- scope tags are compact and visually lighter than quick-filter chips;
- default Resource ordering is Name ascending, shown by the upward sort arrow;
- pagination is summary on the left, numbered pages in the center and Rows per page on the right;
- the first page of a long result set renders `1 2 3 4 5 … last` between previous/next arrows.

These values are encoded in reusable design-system components/tokens so later catalogue pages inherit the same density.

## Reference audit checklist

The reference slice is reviewed from top-left to bottom-right. Each item must be represented by a shared component/token/pattern or explicitly marked not applicable because product behavior is not accepted.

- [x] dark fixed desktop sidebar;
- [x] brand block;
- [x] grouped navigation and active state;
- [x] signed-in account block and logout at sidebar bottom;
- [x] full-width application and Resource detail workspaces;
- [x] page title, description and primary action;
- [x] full-width search with leading icon;
- [x] search applies server-side after a short debounce and still submits immediately on Enter;
- [x] labeled compact filter controls;
- [x] reset action without an extra visible Apply button;
- [x] counted quick-filter presets: All, Active, Retired, No address, No responsibility, No scope;
- [x] counts and exact total are server-backed and computed before pagination;
- [x] dense table with its own border/radius;
- [x] sortable supported columns with ascending/descending indicator;
- [x] sorting is server-backed and applied before pagination;
- [x] select-all checkbox;
- [x] per-row checkbox;
- [x] checked/unchecked/indeterminate selection behavior;
- [x] selected-row visual state;
- [x] primary clickable identity cell;
- [x] monospace secondary reference;
- [x] technical address presentation;
- [x] compact scope tags;
- [x] lifecycle dot indicator;
- [x] diagnostic state indicators;
- [x] distinct loading/error/empty states;
- [x] pagination summary (`Showing x–y of n`);
- [x] centered numbered pager with previous/next arrows;
- [x] server-backed rows-per-page selector;
- [ ] Resource type filter shown in the concept board: intentionally omitted because canonical Resource Catalogue semantics explicitly reject a first-class Resource type attribute/filter;
- [ ] More filters affordance: omitted until there are additional accepted filters to reveal;
- [ ] saved-view behavior: visually present in the concept family but no accepted product semantics yet;
- [ ] bulk mutation toolbar: selection is supported, but no bulk domain actions are accepted yet.

The unchecked items are deliberate semantic gaps, not invitations to fake client-side behavior.

## Table and paging rules

- Catalogue tables are dense and server-backed.
- Header and row heights are tokens.
- Sorting is an allow-listed read-model capability. The backend orders the whole filtered set before offset/limit; never sort only the current client page.
- The active sorted column exposes `aria-sort` and a visible arrow; repeated activation toggles direction.
- Selection uses a first-column checkbox, including select-all and indeterminate state.
- Checkbox interaction never triggers row navigation.
- Primary identity is the strongest clickable cell; technical references are secondary/monospace.
- Empty technical values use a neutral dash unless the domain explicitly defines an error state.
- Tags, lifecycle/status indicators and diagnostic indicators are separate visual concepts.
- Loading, error and empty results are distinct shared page states.
- Exact totals and quick-filter counts come from the read model, never from the current page.
- Page-size changes reset to page 1 and are sent to the backend.

## Detail workspace rules

- Resource Overview, History and Technical details use the full available workspace after the sidebar.
- Detail screens use the same tokens, shared controls, status indicators, page states and surfaces as catalogue lists.
- Temporal facts continue to use add/replace/end semantics; a wider layout must not turn them into scalar CRUD.

## Visual regression guard

The canonical Resource Catalogue layout is protected by `e2e/test_j00_resource_catalogue_visual.py` at a `1440x1000` viewport. The test fingerprints the rendered `main` workspace after creating deterministic Resource rows and compares it with the accepted browser baseline in `e2e/screenshot_regression.py`.

The fingerprint is a regression guard, not the source of design truth. Rebaseline it only after a deliberate comparison with the accepted concept-board reference and the canonical UI/domain contracts. A changed fingerprint caused by an intentional reference/design-system change must be reviewed before its baseline is accepted.

## Tokens

Executable tokens live in `web/src/design-system/tokens.css` and cover:

- application/surface/text/border colors;
- primary and semantic state colors;
- navigation colors;
- control heights/radii;
- tag and checkbox dimensions;
- sidebar width;
- table header/row/cell dimensions;
- standard surface shadow.

Features consume semantic tokens indirectly through design-system components where possible.

## Reference implementation

Current reusable implementation lives under `web/src/design-system/`.

`web/src/features/catalogues/pages/ResourcesPage.tsx` is the reference catalogue feature page. `ResourceDetailsPage.tsx` is the full-width Resource detail reference. New catalogue/detail migrations should first attempt composition from the existing patterns and extend them only when the new requirement is genuinely reusable.

## Deliberate non-goals

The visual baseline may show affordances whose product behavior is not accepted. Do not create placeholder backend/domain behavior merely to fill the picture. Legitimate read-model needs such as total counts, facet counts and ordering belong server-side; domain concepts such as a Resource type do not become valid merely because a concept image contains a control for them.
