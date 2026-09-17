# Web UI component inventory

## P0 — shell and connectivity foundation

### AppShell / Sidebar / NavItem / Topbar / PageHeader

Own shared shell and navigation presentation.

Pages/actions are driven by admitted backend capabilities, not client-side role assumptions.

### ScopeSwitcher

Displays the current responsibility scope and allows switching among backend-provided selectable scopes.

Scope is product context, not a trusted client-side authority claim.

### ConnectivityTreeGrid

Primary operational inventory.

Responsibilities:

- Resource -> Component -> Connectivity hierarchy;
- full-width dense presentation;
- expansion/collapse;
- loading/empty/filter/error states;
- keyboard navigation;
- stable row/group identity for presentation;
- server-backed paging/search/filter as required.

Do not build a generic graph/grid framework before this use case proves reusable abstractions.

### ResourceGroupRow

Shows Resource label/reference and endpoint/address summary.

Must render even when no Component or connectivity exists.

### ComponentGroupRow

Shows Component Deployment display label and contextual actions.

Must render even when there are zero connectivity relationships.

### ConnectivityRow

Shows one projected exact directed interaction with:

- local-relative direction;
- access summary;
- remote Component;
- remote Resource(s);
- independent Need / Decision / Policy cells;
- later Realization.

It does not own business state.

### DirectionIndicator

Accessible text/icon presentation for incoming/outgoing relative to local side.

Do not rely on arrow shape/color alone.

### AccessSummary

Primary DCS/service label plus optional technical protocol/port summary.

### IndependentStatusCells

Separate presentation components/mappings for:

- Need;
- Decision;
- Policy;
- Realization later.

Do not introduce a single generic connectivity StatusBadge.

### AddConnectivityAction / AddConnectivityDrawer

Contextual action from Resource/Component/relationship.

Known scope/local Resource/local Component context is prefilled.

Remote side and DCS are backend-constrained trusted choices.

### ColumnChooser

Allows optional technical columns such as protocol, ports, stable IDs and endpoint details without forcing them into the default application-owner view.

### TechnicalIdentityDisclosure

Progressive display of stable IDs, canonical source/destination and DCS revision.

## P0 — common controls

### Button

Variants: primary, secondary, ghost, destructive. States: default, hover, focus, disabled, loading.

### Input / SearchInput / Textarea / Select

Support disabled/invalid/focus states and keyboard operation.

### StatusBadge

Central semantic mapping for domain-specific scalar states such as:

- Allowed;
- NotAllowed;
- Active;
- Inactive;
- Covered;
- Uncovered;
- NotCurrent;
- Unknown.

The component renders one semantic dimension at a time. It must not collapse independent Need/Decision/Policy meanings.

Do not add Pending/Approved/Rejected to Connectivity Decision.

### Dialog / Drawer / Toast

Dialog: confirmation/compact action.
Drawer: contextual detail or Add Connectivity.
Toast: transient operation feedback only, never the sole carrier of durable business outcome.

### EmptyState / Skeleton / ErrorState

Distinguish genuine empty, filter-empty, authorization-limited and retryable technical failure.

## P1 — connectivity details

### ConnectivityDetailDrawer

Progressively displays Need, Decision, Policy, Local side, Remote side, Technical details and later Realization.

Protected sections respect their own backend read contract.

### ResourceEndpointSummary

Readable Resource identity with current/effective endpoints as secondary technical data.

### RemoteSideSummary

Remote Component plus zero/one/many Resource realizations.

Explicitly supports unresolved realization without treating it as absent connectivity.

### StatusExplanation

Explains business meaning and source dimension without exposing protected reason/provenance unless admitted.

### FilterBar

Maps explicit filter schema to URL/query state.

### DefinitionList / PropertyGrid

For identifiers, governance scope, DCS references, validity and provenance.

### Timeline / ActivityList

For durable Requirement/Decision/Rule history only when returned by authorized backend use cases.

### DateTime / EffectiveWindow controls

Use explicit offset-aware values and preserve half-open [start,end) semantics.

## P2 — later presentation

### Connectivity service view

Alternative service-centric projection over the same read model.

### Connectivity graph

Topology visualization over the same accepted composition.

### MetricCard / charts

Only after concrete aggregate use cases and real metrics exist.
