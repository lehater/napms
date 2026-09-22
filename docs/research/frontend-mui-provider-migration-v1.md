# Research — NAPMS frontend provider architecture and MUI migration v1

Status: research branch candidate with RESOURCE-CATALOGUE pilot.

## Decision

NAPMS should use MUI Material v9 as the primary presentation provider while keeping product/screen semantics provider-neutral.

The target dependency chain is:

```text
Backend domain/application
  ↓
OpenAPI / HTTP contracts
  ↓
Frontend API boundary
  ↓
Feature-local query/command orchestration
  ↓
Screen Model + request lifecycle
  ↓
Canonical Screen/View semantics
  ↓
Canonical Presentation System pattern ids
  ↓
Component Design: provider realization mapping
  ↓
Provider-neutral presentation facade
  ↓
MUI provider adapters + ThemeProvider + selected template composition
  ↓
Rendered UI
```

Not every item is a separate runtime layer. Canonical Screen/View and Presentation System contracts are design-time authority. Runtime code needs only the API boundary, feature-local screen application code, a small presentation facade and the concrete provider.

## Responsibility classification

### Product semantics

Owned upstream by Product/Domain/Application/HTTP contracts.

Examples: Resource identity, create Resource use case, current site/endpoints/responsibilities, backend authorization, conflict/validation outcomes.

### Frontend application semantics

Owned by screen application code plus canonical Screen/View Design.

Examples: query/command bindings, Screen Model shape, request lifecycle, navigation intent, mapping backend outcomes to visible screen states, ephemeral form/disclosure state.

### Presentation semantics

Owned by the provider-neutral Presentation System and Screen/View composition.

Examples: CATALOGUE, DATA-TABLE, TASK-ACTIONS, STATUS; primary identity emphasis; context/actions/collection ordering; required loading/empty/error treatment.

### Provider-specific realization

Owned by Component Design and `web/src/presentation/providers/mui/`.

Examples: MUI Table versus DataGrid, Drawer/List shell, Button variants, ThemeProvider, theme component overrides, responsive `sx`, template source composition.

## Layer decisions

### Backend ↔ frontend boundary

Keep the canonical OpenAPI HTTP interface. Frontend code does not access domain modules or persistence.

The existing `app/api.ts` remains the transport boundary for now. Its long-term cleanup may separate generated DTO/client mechanics from semantic API adapters, but that is independent of the MUI migration.

### Query/command layer

Use feature-local functions shaped to the screen rather than a generic CQRS framework.

For RESOURCE-CATALOGUE:

```text
api.listResources()
  → queryResourceCatalogue()
  → toResourceCatalogueScreenModel()
  → ResourceCatalogueScreenModel
```

Commands remain explicit feature operations. Accepted mutations refresh authoritative server state.

### Screen/View Model

Required when transport projections are not the exact runtime contract the view should consume.

The Screen Model may:
- select/rename fields;
- precompute display summaries;
- represent frontend application state;
- preserve stable identifiers needed for navigation/actions.

It may not invent domain truth or authorization.

### Screen semantics

Remain canonical in `mvp-screen-view-design.yaml`.

For RESOURCE-CATALOGUE the allowed set is inspect/open/create and the excluded set includes search/filter/sort/pagination/bulk/edit/delete. This is the semantic authority regardless of MUI capabilities.

### State/error model

Preserve material distinctions from accepted backend outcomes. Do not reduce authorization rejection, validation rejection, conflict and technical failure to one generic success/failure contract when the screen semantics distinguish them.

Provider adapters render the state they are given; they do not reinterpret HTTP outcomes.

### Permissions/capabilities

Backend admission is authoritative. Frontend capabilities define what the screen may expose for usability and semantic conformance.

Rule: provider/template features are deny-by-default. A disabled MUI control is not authorization proof.

### Navigation

Paths and workspace destinations are frontend application/interface semantics. Drawer/List/Button realization belongs to the provider.

The pilot moves navigation items out of the MUI shell so another provider can render the same workspace navigation model.

### Presentation patterns and slots

Keep the current small vocabulary (APP-SHELL, CATALOGUE, DATA-TABLE, EDITOR, STATUS, etc.).

Do not create a universal slot/component DSL. Add only pattern inputs that carry stable NAPMS presentation semantics. Do not mirror arbitrary MUI props.

### Provider capabilities

A provider realization contract under Component Design records:
- provider/version;
- deny-by-default feature policy;
- selected migration screen scope;
- required pattern mappings;
- adapter owner;
- provider primitives.

This contract is mechanically checked by Harness.

### Theme

MUI ThemeProvider is provider-specific realization. It is the correct owner for MUI palette, typography, shape and component defaults.

Canonical visual invariants such as shell width and dense table geometry remain upstream Presentation System knowledge. The MUI theme/adapter realizes them.

The legacy generated CSS token pipeline should not remain merely to duplicate values already realized through MUI unless a token continues to serve an independent cross-provider or verification contract.

### Official CRUD dashboard template

Use the official template as a pinned composition reference, not as a runtime API and not as product authority.

Adopt selectively:
- responsive dashboard shell;
- navigation composition;
- spacing/density ideas;
- ThemeProvider composition.

Do not import template-specific routes, CRUD controls, fields or behaviors into Screen semantics.

Template internals are source examples and may change. Stable provider APIs are the published MUI components/theme APIs.

### Tables and MUI X DataGrid

MUI X is useful when the accepted screen semantics genuinely require advanced tabular capabilities, virtualization, server-side data source behavior or other DataGrid features.

RESOURCE-CATALOGUE should use plain MUI Table now because:
- sorting is explicitly excluded;
- filtering is explicitly excluded;
- pagination is explicitly excluded;
- Community DataGrid enables pagination and exposes other optional grid capabilities.

Adding DataGrid here would require suppressing provider defaults to emulate a simpler table, increasing coupling without product value.

Reevaluate DataGrid per screen after its semantics authorize corresponding capabilities. Community `@mui/x-data-grid` is MIT; Pro/Premium introduce commercial licensing and should be adopted only for a demonstrated requirement.

### Forms/dialogs

Use MUI form/dialog primitives inside provider adapters or provider-specific presentation components when they realize accepted EDITOR/confirmation semantics.

Do not create wrappers for every TextField/Button/Dialog solely to hide MUI. Create an abstraction only when it is a stable NAPMS pattern seam.

### Data fetching/cache

Server state remains API-owned. The pilot uses local request lifecycle because no shared caching/invalidation problem is demonstrated.

Introduce TanStack Query or another server-state cache only when repeated screens need deduplication, background refresh, invalidation, retries or shared server state. Do not add global client state by default.

### Client state

Keep local form drafts, disclosure/open state and other ephemeral state feature-local. Avoid a global mutable application store until a cross-screen ownership requirement exists.

### Validation

Backend remains authoritative. Frontend may provide immediate field validation only when it implements accepted constraints and does not contradict backend validation.

Map backend 422/403/409/technical outcomes to distinct accepted states.

### Routing

Keep the current small router during the MUI migration. Replacing routing infrastructure is independent of presentation-provider replacement.

If routing complexity later justifies React Router, change it as a frontend application concern, not as part of the MUI adapter.

## BFF decision

BFF state: NOT APPLICABLE for the current First MVP.

Current HTTP projections already supply the facts needed by the browser and frontend mapping is deterministic.

Introduce a server-side BFF only when at least one architecture-significant need appears:
- material aggregation across independently deployed services;
- excessive browser chattiness/latency requiring server composition;
- trusted credential or authorization mediation;
- server/edge caching/projection shaping;
- a stable frontend-facing API insulating the browser from independently evolving downstream APIs.

Do not call a Screen Model or frontend Presenter a BFF. A BFF is a server/network boundary; a Screen Model is frontend application semantics.

## Current WebUI audit

### Preserve

- `app/api.ts`: HTTP transport/error boundary, then incrementally split DTO/client mechanics if useful;
- `app/http-semantics.ts`: transport outcome semantics;
- `app/router.ts`: current route/navigation mechanism;
- feature-specific product/application behavior;
- backend operation mappings;
- accepted screen state/capability semantics;
- existing E2E/visual references as evidence where still valid.

### Rewrite/move

- screen components that currently mix fetch/orchestration, Screen Model construction and JSX;
- top-level AppShell into provider adapter;
- catalogue/detail/editor/list/status rendering into MUI pattern adapters;
- old feature-local presentation markup as each vertical slice migrates;
- UI boundary checker so feature code depends on the provider-neutral presentation facade.

### Delete after final screen migration

- `web/src/design-system/base.css`;
- `web/src/design-system/tokens.css`;
- `web/src/design-system/components.tsx`;
- old `web/src/components/AppShell.tsx`;
- `web/scripts/generate-design-tokens.mjs`;
- obsolete portions of `web/scripts/check-ui-boundaries.mjs`;
- `web/components.json` and shadcn/Tailwind-specific setup when no longer referenced;
- Tailwind/shadcn/lucide dependencies that become unused.

The clearly identified legacy presentation/tooling files are about 27 KB before counting presentation JSX embedded in feature screens. Therefore the final reduction should exceed that amount once screen-local legacy markup is also removed. This is an order-of-magnitude migration estimate, not a completion metric.

## Target code structure

```text
web/src/
  app/
    api.ts
    http-semantics.ts
    router.ts
    navigation.ts
  features/
    resources/
      resourceCatalogueApplication.ts
      resourceCatalogueModel.ts
      ResourceCatalogueScreen.tsx
      ...
  presentation/
    contracts.ts
    index.ts
    providers/
      mui/
        theme.ts
        MuiPresentationRoot.tsx
        MuiAppShell.tsx
        MuiCataloguePattern.tsx
        MuiEditorPattern.tsx
```

Do not create `screen-models/`, `queries/`, `commands/` and other global directories merely to match conceptual layers. Keep feature-local code together until reuse is demonstrated.

## Resource Catalogue end-to-end pilot

```text
OpenAPI operationId: listResources
  ↓
app/api.ts: api.listResources()
  ↓
resourceCatalogueApplication.ts: queryResourceCatalogue()
  ↓
resourceCatalogueModel.ts: ResourceCatalogueScreenModel
  ↓
canonical RESOURCE-CATALOGUE semantic_contract
  allowed: inspect/open/create
  excluded: search/filter/sort/pagination/bulk/edit/delete
  ↓
list mode patterns: CATALOGUE + DATA-TABLE + TASK-ACTIONS + STATUS
create mode pattern: EDITOR + STATUS
  ↓
presentation facade
  ↓
MuiCataloguePattern / MuiEditorPattern
  ↓
MUI Stack/Button/Table/TextField/Alert/CircularProgress
  ↓
rendered catalogue and create route
```

The pilot covers both accepted RESOURCE-CATALOGUE modes: `/resources` and `/resources/new`. Creation remains the canonical `createResource` command and navigates to RESOURCE-DETAIL only after backend acceptance.

## Verification model

1. Contract: OpenAPI operation ids and response outcomes.
2. Screen semantic: Screen Model sources, states, allowed/excluded capabilities, pattern feature bindings.
3. Provider mapping: every pattern required by the migrated scope maps to an adapter and concrete provider primitives; default policy is deny.
4. Structural: feature code cannot import MUI directly.
5. Unit: pure Screen Model mapping is deterministic.
6. Rendered: hierarchy, dense table geometry, responsive navigation, loading/empty/error states and accepted reference conformance.
7. Journey/E2E: navigation/API behaviors remain intact.

Visual baselines prove accepted presentation invariants only; they do not authorize template features.

## Migration plan

1. Pilot RESOURCE-CATALOGUE with MUI shell + Catalogue/Table/Editor/Status adapters, including list and create modes.
2. Verify build, semantic/provider checks, unit/E2E/rendered evidence.
3. Migrate RESOURCE-DETAIL next; this exercises DETAIL + EDITOR + DISCLOSURE and mutation/error states.
4. Migrate remaining catalogue/detail/editor workspaces by vertical slice, adding an adapter only when a new accepted pattern is first needed.
5. Introduce MUI X DataGrid only on a screen whose accepted semantics require its capabilities.
6. After every screen is off the legacy design-system, remove legacy CSS/components/token generator/Tailwind-shadcn setup and tighten the boundary checker.
7. Refresh rendered baselines only through explicit reference-conformance review.

## Priority findings

- P0: provider/template capabilities must remain deny-by-default; otherwise MUI silently changes product semantics.
- P0: MUI imports must stay behind the presentation provider boundary; otherwise provider replacement touches feature/application code.
- P1: keep Screen Model/query-command orchestration feature-local and provider-neutral.
- P1: remove the legacy presentation stack after the final vertical slice rather than maintain two permanent systems.
- P1: do not use Community DataGrid for RESOURCE-CATALOGUE while pagination is explicitly excluded.
- P2: split `app/api.ts` further only when generated client/DTO complexity creates a real maintenance problem.
- P2: adopt a server-state cache only after repeated invalidation/deduplication needs appear.
