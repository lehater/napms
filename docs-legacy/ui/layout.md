# Web UI layout

## App shell

    +-------------------------------------------------------------------+
    | Sidebar | Topbar: Scope switcher / user menu                      |
    |         +---------------------------------------------------------+
    |         | Breadcrumb / PageHeader                                 |
    |         | Filters / Actions                                       |
    |         | Main workspace                                          |
    +---------+---------------------------------------------------------+

## Sidebar

Responsibility: primary product navigation using short user-oriented labels.

Expanded desktop width: 224-240px. Collapsed width: 64-72px.

Current navigation:

    OVERVIEW
      Connectivity
      Checker

    CATALOGUES
      Applications
      Resources

    POLICY
      Needs
      Decisions
      Rules
      Effective
      Export

    OPERATIONS
      Realization

Compose Connectivity is not a primary navigation destination. It is an action flow launched from Connectivity or relevant details.

### Future navigation

Future areas may be visible only when backed by accepted scope, explicitly marked Planned and visually disabled/distinct. They do not navigate to fabricated working screens or fake data.

## Topbar / scope context

The selected responsibility scope is a primary workspace context.

Use a compact ScopeSwitcher in the topbar or page-context area so that:

- the current scope is always discoverable;
- changing scope is deliberate;
- shareable routes may carry selected scope where appropriate;
- the UI does not imply scope is merely a table filter.

Exact selectable-scope semantics come from the accepted I16A responsibility model.

The topbar also contains the current user menu and logout.

## Connectivity page structure

    PageHeader
      Connectivity
      selected scope context
      admitted primary actions

    FilterBar
      search
      status filters
      direction
      column chooser

    Full-width ConnectivityTreeGrid

The tree-grid uses available viewport width. Do not wrap it in a narrow marketing-style max-width container.

## Tree-grid hierarchy

    Resource group row
      Component Deployment group row
        Connectivity relationship row

A Resource/Component with zero connectivity remains visible.

Group rows should minimize repeated data while keeping scanning and keyboard navigation clear.

## Focused forms/details

Use:

- Drawer for Add Connectivity and contextual relationship detail when the content is compact enough;
- dedicated route for deep/bookmarkable details;
- Dialog for confirmation/compact actions.

Focused forms may use a bounded width around 720-900px. Deep detail pages may use a readable wider bound. Operational inventories use full workspace width.

## Responsive behavior

- >= 1280px: expanded desktop shell and full tree-grid;
- 768..1279px: collapsed sidebar by default; tree-grid may scroll horizontally;
- < 768px: sidebar overlay; forms/details remain functional; dense inventory may use progressive column reduction/scrolling.

Mobile remains functional but is not the primary optimization target.
