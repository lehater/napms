# Web UI component inventory

## P0 — foundation

### AppShell / Sidebar / NavItem / Topbar / PageHeader

Own shared shell and navigation presentation. Actions shown by pages are driven by admitted backend capabilities, not client-side role assumptions.

### Button

Variants: primary, secondary, ghost, destructive. States: default, hover, focus, disabled, loading.

### Input / SearchInput / Textarea / Select

Support disabled/invalid/focus states and keyboard operation.

### StatusBadge

One central mapping owns semantic label/color/icon. Initial domain statuses include:
- `Allowed`;
- `NotAllowed`;
- `Active`;
- `Inactive`.

Do not introduce `Pending/Approved/Rejected` while the Connectivity Decision workflow remains deferred.

### DataTable

Add capabilities only when required:
- server-side pagination;
- sorting/filtering;
- row actions;
- loading/empty/error states.

Avoid a generic mega-table before multiple screens prove a stable shared API.

### Dialog / Drawer / Toast

Dialog: confirmation/compact action. Drawer: contextual detail. Toast: transient operation feedback, never the sole carrier of a durable business result.

### EmptyState / Skeleton / ErrorState

Shared states must distinguish genuine empty, filter-empty, authorization-limited and retryable failure conditions.

## P1 — workflow/details

### FilterBar

Maps explicit filter schema to URL/query view state.

### DefinitionList / PropertyGrid

For Rule identity, governance scope, DCS references, validity and provenance.

### Timeline / ActivityList

For durable Access Rule business history/provenance where returned by backend use cases.

### DateTime / EffectiveWindow controls

Use explicit offset-aware values and preserve `[start, end)` semantics. UI controls must not invent recurring schedule behavior.

## P2 — dashboard

MetricCard/chart/status-summary components only after concrete aggregate product use cases exist.
