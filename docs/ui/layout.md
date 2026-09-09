# Web UI layout

Canonical product/viewport contract: `docs/requirements/web-ui-requirements.md`.

## App shell

```text
+-------------------------------------------------------------+
| Sidebar | Topbar                                            |
|         +---------------------------------------------------+
|         | Breadcrumb / PageHeader                           |
|         | Filters / Actions                                 |
|         | Main content                                      |
+---------+---------------------------------------------------+
```

The shell is optimized for sustained desktop operational work, not a mobile-dashboard layout.

## Sidebar

Responsibility: primary application navigation.

Expanded desktop width: 224-240px. Collapsed width: 64-72px. Collapse state may be stored locally because it is presentation preference, not business state.

Current/near-term navigation:

```text
CONNECTIVITY NEEDS
  My Connectivity Needs

CONNECTIVITY GOVERNANCE
  Connectivity Decisions   [Preview until I16 executable]

ACCESS POLICY
  Compose Connectivity
  Access Rules

POLICY VIEWS
  Effective Policy
  Normalized Policy
```

At desktop width the sidebar should remain persistently available unless the user explicitly collapses it.

Future user-facing capabilities may appear in their intended groups as explicit `Preview · Ixx` destinations according to the canonical preview policy. Each item must open a real preview route.

The future full shell may additionally contain:
- TECHNICAL ACCESS — Technical Evidence, Access Resolution;
- ENFORCEMENT — Enforcement Placement, Reconciliation, Configuration Rendering;
- NETWORK OPERATIONS — Network Operations;
- later operator/admin surfaces only after their roadmap semantics are concrete.

Dashboard remains special: show it in preview only after the intended aggregate read models are sufficiently defined to review a meaningful layout. Do not manufacture metrics.

Do not add approval, user/role administration or other non-roadmap placeholder navigation.

## Narrow-screen navigation

Below the desktop shell breakpoint, preserve the same navigation taxonomy.

Preferred implementation:
- menu button;
- overlay/off-canvas sidebar/drawer;
- same groups and labels as desktop;
- clear active destination;
- keyboard/focus containment and Escape-to-close.

Do not replace the application IA with a separate row of shortened mobile-only destination labels.

## Topbar

Responsibility: global UI context/actions.

Initial content:
- current user;
- logout;
- menu trigger when sidebar is off-canvas;
- optional breadcrumb below topbar.

Global search/notifications are added only with real use cases.

## Page structure

```text
PageHeader
  title
  optional description/breadcrumb
  admitted primary/secondary actions

FilterBar / Tabs when required

Content
  Table / Details / Form
```

Operational tables use available viewport width rather than a narrow marketing-style container.

Forms/details may use bounded readable widths when that improves scanning, but data tables, policy projections and technical evidence regions should not be artificially constrained.

## Tables and wide technical regions

- table overflow is contained inside the table/content region;
- document-level horizontal scrolling is a defect;
- essential identity/action columns remain discoverable;
- presentation-only columns may be reduced at intermediate widths;
- mobile compatibility may use explicit horizontal table scrolling rather than converting every row to a card;
- technical JSON/provenance may use dedicated scrollable/preformatted regions.

## Drawer/dialog

Use Drawer for contextual read/light-edit detail that does not justify a separate route. Use a dedicated page for deep, multi-section or bookmarkable content. Use Dialog for confirmations and compact actions.

## Viewport quality matrix

| Viewport | Role | Required behavior |
|---|---|---|
| 1440 x 900/1000 class | primary desktop | full shell, full density, visual baseline |
| 1280 x 800 | minimum desktop | complete normal workflows, no critical clipping |
| ~768px | tablet compatibility | same IA, off-canvas/collapsed nav, bounded table overflow |
| ~390px | mobile compatibility | auth/navigation/read/simple actions reachable; no document overflow |

Desktop is the product optimization target. Narrow widths are compatibility targets, not a separate mobile product.
