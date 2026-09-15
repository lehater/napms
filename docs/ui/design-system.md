# NAPMS UI design system

## Purpose

This document owns reusable visual, layout and interaction rules for the current NAPMS UI. Product and domain semantics remain owned by requirements/domain/architecture artifacts.

## Layering

```text
semantic tokens
  -> primitives/components
    -> layout
      -> product patterns
        -> feature pages
```

Features provide domain data and actions. They compose shared UI building blocks rather than recreating generic geometry, controls or state presentation.

## Global invariants

- Desktop workspaces use the full width available after the sidebar.
- Page-root arbitrary `max-width` is not used for operational, catalogue or detail workspaces.
- Width constraints are reserved for semantic cases such as dialogs, focused forms and readable prose.
- Features do not introduce raw colors when a semantic token exists.
- Shared controls, status visuals, tags, page states and table structure come from the design system.
- React reuse is by composition rather than page inheritance or a monolithic universal component.
- Generic design-system components do not encode Resource, Application or other domain semantics.
- A feature may map domain meaning to a visual tone through an explicit feature-level mapping.
- The authenticated account remains visible in the lower-left desktop sidebar and displays only actor data supplied by authentication.

## Application shell

The standard desktop structure is:

```text
AppShell
  Sidebar
    Brand
    grouped Navigation
    User/Logout
  PageWorkspace
    PageHeader
    feature content
```

Reusable shell geometry is owned by the design system, not duplicated inside features.

## Catalogue pattern

Catalogue pages compose the shared pattern:

```text
PageWorkspace
  PageHeader
    title
    description
    primary action when accepted by product behavior
  CatalogueSurface
    CatalogueToolbar
      SearchInput
      CatalogueFilterBar
    CatalogueViewBar
      counted presets when supported by the read model
      optional view actions
    DataTable
      selection column when selection is supported
      sortable header cells
      rows
    CataloguePaginationControls
```

Catalogue behavior is server-backed where the result depends on the complete result set:

- search/filtering operate on the backend result set;
- supported sorting is allow-listed by the read model and applied before pagination;
- exact total and facet/preset counts are computed before pagination;
- changing page size resets to page 1 and is sent to the backend;
- the UI never derives global counts or ordering from the current page alone.

## Table rules

- Catalogue tables use compact reusable row/header geometry from design-system tokens.
- The table surface owns its border/radius; toolbar, presets and pagination are separate layout regions.
- The active sorted column exposes `aria-sort` and a visible direction indicator.
- Repeated activation toggles direction when the column supports both directions.
- Selection uses a first-column checkbox with checked, unchecked and indeterminate select-all states.
- Checkbox interaction does not trigger row navigation.
- Primary identity is the strongest clickable cell; technical references use secondary/monospace presentation.
- Empty technical values use a neutral dash unless the domain defines a distinct semantic state.
- Tags, lifecycle/status indicators and diagnostic indicators are separate visual concepts.
- Loading, error and empty-result states are distinct shared page states.

## Detail workspaces

Detail screens use the same shell, tokens, controls, status visuals and page states as catalogue screens.

Operational and data-heavy details use the full available workspace. Domain-specific temporal facts retain their domain operations and must not be reduced to scalar CRUD merely because the UI uses a wider layout.

## Reusable source

Executable design-system code lives under:

```text
web/src/design-system/
```

Semantic tokens are defined in `web/src/design-system/tokens.css`. Feature code should consume reusable components and semantic tokens from this layer before introducing feature-local visual infrastructure.

The design system covers application/surface/text/border colors, semantic states, navigation, control geometry, tags, checkboxes, sidebar dimensions, table dimensions and reusable surfaces.

## Semantic boundary

Visual affordances do not create product or domain behavior. A filter, action, status, saved view, bulk operation or domain attribute appears only when its semantics are accepted by the owning requirements/domain contract.

Legitimate read-model needs such as total counts, facet counts and ordering belong server-side when they describe the complete result set. UI convenience must not invent domain concepts or client-only approximations of server-owned truth.
