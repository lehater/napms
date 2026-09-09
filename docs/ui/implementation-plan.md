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

## UI-5 — Human-readable Catalogue UX — implemented in I12

- optional Component Deployment and DCS display labels;
- stable UUID shown as secondary/fallback identity;
- server-side authorized interaction search in Compose Connectivity;
- DCS traffic summary decoded from immutable projection semantics;
- Access Rules, Rule Details, Effective Policy and Normalized Policy render catalogue labels without changing business meaning;
- no generic catalogue CRUD/browse surface is introduced.

## UI-6 — My Connectivity Needs — implemented in I13

- Connectivity Requirements navigation/workspace;
- authorized paged list and details;
- declaration using I12 label-first ACC search;
- Dependent constrained to one interaction participant;
- Ongoing / absolute-window applicability;
- mandatory business justification;
- backend-admitted applicability/justification/retirement actions;
- provenance/history presentation;
- no approval/decision/policy-alignment status in I13.

## UI-7 — Requirement-to-Policy Alignment — implemented in I14

- explicit-asOf policy coverage on My Connectivity Needs list;
- Requirement Details coverage panel;
- statuses: Covered / Uncovered / NotCurrent / Unknown;
- exact semantic interaction matching;
- no Denied status;
- no Rule detail leakage from derived coverage;
- no configured/observed-access implication.

## UI-8 — Desktop-first operational quality baseline — active in I16

Goal: harden the existing UI before adding Connectivity Decision screens.

Accepted baseline:
- NetBox-class professional desktop operational UX as a comparative reference, not a clone;
- primary visual/test viewport at 1440 x 900/1000 class;
- complete normal operation at 1280 x 800;
- same IA with off-canvas/collapsed navigation at tablet/mobile widths;
- no mobile-only top navigation taxonomy;
- operational collections remain table-first;
- document-level horizontal overflow is prohibited;
- Playwright real-browser scenarios use roles/labels;
- WCAG 2.2 AA automated checks for critical routes/states;
- functional mutation + reload persistence scenarios;
- visual regression for stable desktop states and selected mobile compatibility states;
- P0/P1 UI defects close before new I16 Decision UI.

Exit: browser/visual quality gate is green and becomes a required regression gate for later UI increments.

## UI-9 — Connectivity Decisions — planned in I16 after UI-8

- authorized Decision list/details;
- direct final `Allowed | NotAllowed` recording;
- exact subject/scope/validity/reason/provenance presentation;
- immutable supersession history;
- no Pending/Approved/Rejected or approval queue.

## Engineering constraints

- route/page orchestration is separate from reusable presentational primitives;
- feature code groups by use case/domain area rather than one global component bucket;
- transport DTO mapping stays at the frontend API boundary;
- abstractions are extracted after demonstrated reuse;
- no client-side role assumption substitutes for backend Authority Management;
- no approval workflow is introduced by UI convenience;
- desktop-first does not permit broken narrow-screen behavior;
- responsive adaptation must not change domain meaning or admitted capability.
