# Web UI implementation plan

## UI-0 — foundation

Goal: reusable frontend shell without reproducing the whole product.

Deliverables:
- React/TypeScript application bootstrap;
- Tailwind + shadcn/ui foundation;
- design tokens;
- AppShell/Sidebar/Topbar/PageHeader;
- basic form/control/status/table/overlay/feedback primitives;
- route skeleton;
- loading/empty/error patterns.

Exit: one real route renders inside the accepted shell without ad-hoc styling.

## UI-1 — first vertical slice

```text
Login
  -> Compose Connectivity
  -> Submit Access Rule Proposal
  -> ConnectivityDecision result
  -> Allowed: Access Rule summary/details
```

Goal: validate the actual browser -> HTTP -> Application -> PostgreSQL boundary on the smallest useful user outcome.

Required UI states include successful new/existing Rule resolution, `NotAllowed`, authority denial/unknown, invalid interaction/reference and retryable runtime failure.

## UI-2 — Access Rule workspace — implemented in I9

Implemented:
- explicit `ReadAccessRule` authorized list;
- bookmarkable Rule Details;
- proposal provenance and state-history presentation;
- backend-admitted Active/Inactive mutation using `SetRuleOperationalState`;
- independent read vs mutation authority;
- server-side Rule pagination and fail-closed ambiguous-scope indication.

I10 extension:
- independent backend-admitted EffectiveWindow set/change/clear;
- half-open interval guidance and offset-aware datetime controls;
- EffectiveWindow business-history presentation.

## UI-3 — policy views — implemented in I10

Implemented:
- explicit asOf-bound ReadEffectiveDesiredPolicy scope discovery;
- Effective Desired Policy screen with authorized-empty distinction;
- Normalized Policy screen preserving Any / NotApplicable / inclusive ranges;
- Rule/decision/Authority/ACC/RC provenance presentation;
- fail-closed denied/unknown/stale/correlation errors from existing HTTP contracts.

## UI-4 — dashboard/secondary navigation

Add aggregate dashboard and any global audit/search features only after concrete source queries exist. Do not manufacture metrics or placeholder navigation.

## Engineering constraints

- route/page orchestration is separate from reusable presentational primitives;
- feature code groups by use case/domain area rather than one global component bucket;
- transport DTO mapping stays at the frontend API boundary;
- abstractions are extracted after demonstrated reuse;
- no client-side role assumption substitutes for backend Authority Management;
- no approval workflow is introduced by UI convenience.


## UI-5 — Human-readable Catalogue UX — implemented in I12

- optional Component Deployment and DCS display labels;
- stable UUID shown as secondary/fallback identity;
- server-side authorized interaction search in Compose Connectivity;
- DCS traffic summary decoded from immutable projection semantics;
- Access Rules, Rule Details, Effective Policy and Normalized Policy render catalogue labels without changing business meaning;
- no generic catalogue CRUD/browse surface is introduced.
