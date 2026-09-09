# Web UI implementation plan

Historical UI stages remain implementation evidence. New work follows the current active plan and post-Wave-1 roadmap.

## UI-0 — foundation

Implemented:
- React/TypeScript bootstrap;
- Tailwind + shadcn/ui foundation;
- design tokens;
- AppShell/Sidebar/Topbar/PageHeader;
- form/control/status/table/overlay/feedback primitives;
- route skeleton;
- loading/empty/error patterns.

## UI-1 — first proposal vertical slice

Implemented:

    Login
      -> Compose Connectivity
      -> Submit Access Rule Proposal
      -> ConnectivityDecision result
      -> Allowed: Access Rule summary/details

This was the first browser -> HTTP -> Application -> PostgreSQL proof. It is no longer the target primary information architecture.

## UI-2 — Access Rule workspace

Implemented through I9/I10:
- authorized Rule list/details;
- Active/Inactive mutation;
- EffectiveWindow mutation/history;
- independent read vs mutation authority.

## UI-3 — policy views

Implemented in I10:
- Effective Desired Policy;
- Normalized Policy;
- explicit asOf and scope semantics.

## UI-4 — dashboard/secondary navigation

Still deferred.

Do not manufacture aggregate metrics or fake dashboard cards. The new Connectivity workspace is an operational inventory, not this deferred aggregate dashboard.

## UI-5 — Human-readable Catalogue UX

Implemented in I12:
- ACC display labels;
- stable UUID secondary/fallback identity;
- bounded interaction search;
- DCS traffic summary;
- label-first Rule/Effective/Normalized presentation.

## UI-6 — Connectivity Requirements

Implemented in I13:
- My Connectivity Needs list/details/declaration;
- applicability/justification/retirement;
- no approval lifecycle.

## UI-7 — Requirement-to-Policy Alignment

Implemented in I14:
- Covered / Uncovered / NotCurrent / Unknown;
- explicit asOf;
- no Denied;
- no Rule-detail leakage;
- no configured/observed claim.

## UI-8 — Connectivity Workspace / IA v2

Status: next UI product slice after I16A domain/read-model prerequisites.

Goal:
make the resource-centric Connectivity workspace the primary post-login surface.

Prerequisites:
- accepted selected responsibility scope -> local Resource semantics;
- Scoped Connectivity Inventory application/read contract;
- HTTP contract for the composition.

Deliverables:
- new sidebar IA;
- ScopeSwitcher;
- Connectivity as default post-login route;
- resource-centric ConnectivityTreeGrid;
- Resource -> Component -> Connectivity hierarchy;
- local-relative direction;
- readable DCS/access summary;
- remote Component/Resource;
- independent Need / Decision / Policy cells;
- Resources/Components with zero connectivity;
- relationship detail drawer/route;
- optional technical columns for protocol/ports/IDs.

Exit:
an authenticated actor can select a responsibility scope and understand the current connectivity landscape without navigating through bounded-context-specific pages.

## UI-9 — Contextual Add Connectivity

Status: after UI-8 read-only workspace is proven.

Goal:
start new connectivity work from the Resource/Component context.

Deliverables:
- Add Connectivity action on eligible local Component rows;
- local scope/Resource/Component prefilled;
- trusted remote-side discovery;
- structurally valid DCS/access selection;
- applicability/justification inputs as required;
- user-facing Request access / Add connectivity action;
- integration with accepted Requirement/proposal/Decision/Rule application flow.

Guardrail:
do not add a durable Waiting/Under review state until I16B workflow semantics are accepted.

Exit:
a user can create/request a new exact connectivity relationship from the overview without re-entering known local context or visiting Compose Connectivity as a standalone route.

## UI-10 — Decision participant workflow

Status: gated by I16B.

Goal:
surface real Decision-domain runtime/workflow after semantic closure.

Possible deliverables only if accepted:
- Decisions workspace;
- decision participant queue/worklist;
- waiting/process presentation;
- final Allowed/NotAllowed reason/provenance;
- decision history/supersession.

No UI lifecycle may be invented to satisfy this stage.

## UI-11 — Realization overlays

Status: later I17-I20.

Goal:
add Evidence / Realization / Enforcement dimensions to the same Connectivity workspace.

Do not create a second disconnected operational UI if the existing Scoped Connectivity Inventory can be safely extended.

## Engineering constraints

- route/page orchestration is separate from reusable presentation primitives;
- feature code groups by product/use-case area;
- transport DTO mapping stays at the frontend API boundary;
- abstractions are extracted after demonstrated reuse;
- backend Authority Management remains authoritative;
- no cross-context business truth is duplicated in the frontend;
- no approval/workflow semantics are introduced by UI convenience;
- operational tree-grid uses available viewport width.
