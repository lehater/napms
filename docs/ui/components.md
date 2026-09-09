# Web UI component inventory

Canonical product/viewport contract: `docs/requirements/web-ui-requirements.md`.

## P0 — foundation

### AppShell / Sidebar / NavItem / Topbar / PageHeader

Own shared shell and navigation presentation. Actions shown by pages are driven by admitted backend capabilities, not client-side role assumptions.

Desktop keeps persistent navigation. Narrow screens use the same IA through off-canvas/collapsed navigation.

### Button

Variants: primary, secondary, ghost, destructive.

States:
- default;
- hover;
- focus-visible;
- active;
- disabled;
- loading.

All visible/intermediate states must preserve required contrast. Avoid broad color interpolation transitions when intermediate colors can violate WCAG contrast.

### Input / SearchInput / Textarea / Select

Support disabled/invalid/focus states and keyboard operation.

Controls require semantic accessible names. Test-only selectors must not substitute for missing labels.

### StatusBadge

One central mapping owns semantic label/color/icon. Domain statuses must always include text and never rely on color alone.

Current/near-term examples:
- `Allowed`;
- `NotAllowed`;
- `Active`;
- `Inactive`;
- Requirement alignment statuses.

Do not introduce `Pending/Approved/Rejected` unless canonical Decision semantics later add those states.

### DataTable

Primary representation for comparable operational collections.

Baseline capabilities as required by each use case:
- server-side pagination;
- sorting/filtering/search;
- dominant row/details navigation;
- secondary row actions;
- stable readable + technical identity presentation;
- loading/empty/filter-empty/authority-limited/error states;
- bounded horizontal overflow.

Avoid:
- card-per-object responsive transformations as the default;
- a generic mega-table abstraction before multiple screens prove a stable shared API;
- client-side sorting/filtering over only one server page while implying a complete result set.

Per-user column visibility/order preferences are a later capability requiring a concrete operator need; they are not baseline scope merely because comparable tools support them.

### Dialog / Drawer / Toast

Dialog: confirmation/compact action.

Drawer: contextual detail/light edit.

Toast: transient operation feedback, never the sole carrier of a durable business result.

### EmptyState / Skeleton / ErrorState

Shared states must distinguish genuine empty, filter-empty, authorization-limited and retryable failure conditions.

## P1 — workflow/details

### FilterBar

Maps explicit filter schema to URL/query view state. Desktop layout should keep high-frequency filters visible without forcing a modal workflow.

### DefinitionList / PropertyGrid

For Rule/Requirement/Decision identity, governance scope, DCS references, validity and provenance.

### Timeline / ActivityList

For durable business history/provenance where returned by backend use cases.

### DateTime / EffectiveWindow controls

Use explicit offset-aware values and preserve `[start, end)` semantics. UI controls must not invent recurring schedule behavior.

## P2 — dashboard

MetricCard/chart/status-summary components only after concrete aggregate product use cases exist.
