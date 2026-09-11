# NAPMS UI design system

Status: reference slice in PR #85.

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
- Page-root arbitrary `max-width` is not used for operational/data pages.
- Width constraints are allowed only for semantic cases such as dialogs, forms or readable prose.
- Features do not introduce raw hex colors when a semantic token exists.
- Shared controls, status visuals, tags, page states and table structure come from the design system.
- React reuse is by composition, not page inheritance or a monolithic prop-driven universal page.
- A feature may map domain meaning to a visual tone, but generic design-system components must not encode Resource/Application/etc. semantics.

## Reference catalogue anatomy

The canonical catalogue slice is composed as:

```text
CataloguePage
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
      FilterChip*
      optional view actions
    DataTable
      selection column
      header
      rows
        Checkbox
        primary link/cell
        reference text
        technical values
        TagList
        StatusPill
        IssueIndicator
    CataloguePagination
```

The Resource Catalogue is the first executable reference implementation.

## Table rules

- Catalogue tables are dense and server-backed.
- Header and row heights are tokens.
- Selection uses a first-column checkbox, including select-all and indeterminate state.
- Checkbox interaction never triggers row navigation.
- Primary identity is the strongest clickable cell; technical references are secondary/monospace.
- Empty technical values use a neutral dash unless the domain explicitly defines an error state.
- Tags, lifecycle/status pills and diagnostic indicators are separate visual concepts.
- Loading, error and empty results are distinct shared page states.

## Tokens

Executable tokens live in `web/src/design-system/tokens.css` and cover:

- application/surface/text/border colors;
- primary and semantic state colors;
- navigation colors;
- control heights/radii;
- tag and checkbox dimensions;
- sidebar width;
- table header/row/body dimensions;
- standard surface shadow.

Features consume semantic tokens indirectly through design-system components where possible.

## Reference implementation

Current reusable implementation lives under `web/src/design-system/`.

`web/src/features/catalogues/pages/ResourcesPage.tsx` is the reference catalogue feature page. New catalogue migrations should first attempt composition from the existing pattern and extend the pattern only when the new requirement is genuinely reusable.

## Deliberate non-goals of the first slice

The visual baseline may show affordances whose product behavior is not yet accepted (for example saved views or bulk mutations). Do not create placeholder backend/domain behavior merely to fill the picture. Add such affordances only when their semantics are accepted; the visual system should already have a place for them.
