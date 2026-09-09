# Web UI requirements — accepted I8 refinement

Status: `accepted through I16 desktop-first operational UI and planned-capability preview refinement`.

Date: 2026-09-09.

## Purpose

Define the accepted first NAPMS Web UI increment and the product/UX constraints from which the HTTP runtime contract is derived.

This document owns Web UI product/UX requirements. `docs/ui/` owns the implementation-oriented visual handoff. Runtime/API mechanics remain engineering concerns.

## Product boundary

The Web UI is the first human-facing consumer of the NAPMS HTTP JSON API.

The UI is an outer adapter, not a second source of business truth. Access Policy, Authority Management, Application Communication Catalogue, Resource Catalogue and normalized export semantics remain owned by backend Domain/Application modules.

Backend routes and DTOs must follow accepted application use cases and UI journeys rather than generic database CRUD.

## First persona and authority model

The Web UI serves authenticated actors through effective Authority Management permissions for each requested action. Proposal composition uses `ProposeConnectivity`; Access Rule workspace reads use `ReadAccessRule`; state mutation uses `SetRuleOperationalState`.

The UI persona is defined by effective domain authority, not by a hard-coded UI role name. One authenticated actor may have different allowed actions across scopes and times.

I13 adds Connectivity Requirements actions independently from Access Policy actions: declaration/read/applicability/justification/retirement permissions are checked separately by the backend.

The backend remains authoritative for both visibility and action admission. Client-side hiding/disabling is UX only.

## First end-to-end journey

The first useful UI journey is:

```text
Login
    -> Compose Connectivity
    -> select Source Component Deployment
    -> select Destination Component Deployment
    -> select one compatible immutable DCS contract/revision
    -> Submit Access Rule Proposal
    -> consume ConnectivityDecision(Allowed | NotAllowed)
    -> Allowed: show created/resolved authoritative Access Rule
    -> NotAllowed: show the business result; no Access Rule exists
```

Rules:
- the user chooses trusted catalogue/domain references rather than entering firewall addresses, protocol/ports or vendor syntax;
- composition must expose only references/interactions admitted by backend use cases for the authenticated actor/scope;
- the UI never supplies a trusted `actor_id`; authenticated backend identity feeds Authority Management;
- repeated Allowed materialization may resolve the existing Rule and must be presented as the same authoritative outcome, not a duplicate request;
- `NotAllowed` is a valid business outcome, distinct from transport/security failure.

## Connectivity Decision UI boundary

I15 promoted Connectivity Decision to a first-class Bounded Context. I16 may expose direct authorized final-decision operations over that accepted model.

The stable semantic chain is:

```text
Access Rule Proposal
    -> effective ConnectivityDecision(Allowed | NotAllowed)
    -> Access Policy
```

Accepted UI consequences:
- a Connectivity Decision workspace may list/read final Decisions admitted through `ReadConnectivityDecision`;
- an actor admitted through `DecideConnectivity` may record a direct final `Allowed | NotAllowed` Decision with required reason/validity/evidence inputs accepted by backend use cases;
- Decision identity, subject, governance scope, outcome, validity, reason and provenance are inspectable without exposing persistence mechanics;
- proposal authority does not imply decision authority;
- absence/expiry/ambiguity of a Decision is not displayed as a third business outcome;
- a later superseding Decision is a new immutable Decision and historical records remain inspectable.

Do not introduce persistent generic `Access Request`, `Pending`, `Approved`, `Rejected`, approval queue, quorum/SoD UI or automatic Rule-revocation controls unless later canonical Decision requirements explicitly add those semantics.

## Initial screen set

### 1. Login

Purpose: authenticate into the controlled/test environment.

Inputs: login, password.

Output: authenticated application session or explicit authentication failure.

### 2. Compose Connectivity

Purpose: create one structurally valid Access Rule Proposal from trusted application-catalogue references.

Inputs:
- current authorized scope/context;
- Source Component Deployment;
- Destination Component Deployment;
- compatible immutable DCS contract/revision.

Output: proposal submission result.

The composition UX should constrain later choices using backend-provided valid options rather than let the user assemble arbitrary identifier combinations.

I12 presentation rules:
- Component Deployment and DCS display names are shown as primary text when available;
- the stable UUID remains visible as secondary technical identity;
- missing display metadata falls back to the stable ID without changing semantics;
- DCS traffic summary is decoded from the existing immutable projection payload;
- interaction search is server-side and bounded, searching admitted catalogue labels and stable IDs only after the proposal-authority gate.

### 3. Proposal Result

Purpose: present the semantic result of proposal submission.

Outcomes:
- `Allowed` -> created/resolved Access Rule summary and navigation to Rule Details;
- `NotAllowed` -> explicit business outcome with no Rule;
- denied/unknown authority, invalid interaction, not-found, stale/conflict or dependency failure -> distinct recoverable/error presentation where applicable.

This may be a result state of Compose Connectivity rather than a dedicated route.

### 4. Access Rules

Purpose: inspect authoritative Access Rules visible through explicit `ReadAccessRule` authority. List results contain only Rules from unambiguously permitted governance scopes; read authority does not imply mutation authority.

Initial useful data includes Rule ID, source deployment, destination deployment, DCS revision/reference, governance scope, operational state and effective-window summary where available. Source/destination/DCS display names are primary presentation when available; stable IDs remain visible and authoritative.

### 5. Access Rule Details

Purpose: inspect one authoritative Rule and supported management/provenance information.

Before returning data, backend evaluates `ReadAccessRule` against the Rule's stored governance scope. State-change controls are shown only after a separate `SetRuleOperationalState` admission check.

State and EffectiveWindow mutation controls are admitted independently. `SetRuleOperationalState` permission does not imply `SetRuleEffectiveWindow` permission.

Show progressively:
- Rule ID and immutable semantic identity;
- Rule Governance Scope;
- `Active | Inactive` state;
- optional EffectiveWindow;
- Connectivity Decision correlation/reference where available;
- business audit/provenance;
- admitted state/property actions only when backend use cases allow them.

### 6. Effective Desired Policy

Purpose: select and inspect the authorized effective desired-policy subset for one Rule Governance Scope and explicit `asOf`. Scope choices come from unambiguous effective `ReadEffectiveDesiredPolicy` authority.

### 7. Normalized Policy

Purpose: present the vendor-neutral normalized policy JSON/view for the same explicit authorized scope/asOf context while preserving required row semantics and provenance.

The UI presentation must not redefine or omit normalized export meaning. I12 may add catalogue display labels beside normalized rows, but the normalized technical addresses, traffic semantics and provenance remain authoritative.

### 8. My Connectivity Needs

Purpose: declare and manage authoritative Connectivity Requirements visible through explicit Connectivity Requirements authority.

List:
- readable Source/Destination/DCS labels first, stable IDs second;
- Dependent Component Deployment;
- Governance Scope;
- Applicability;
- lifecycle `Active | Retired`;
- justification summary.

Declaration:
- select one admitted Requirement Governance Scope;
- search/select one exact ACC-backed directed interaction;
- select Dependent from the Source/Destination participants only;
- choose `Ongoing` or absolute `[start,end)` applicability;
- enter mandatory business justification;
- submit only stable semantic IDs; actor/time/provenance are server-owned.

Details:
- immutable Dependent and Required Semantic Interaction;
- stored Requirement Governance Scope;
- current applicability and justification;
- declaration provenance;
- applicability/justification/lifecycle histories;
- independent backend-admitted actions for Set Applicability, Set Justification and Retire.

I14 alignment:
- the list shows derived `Covered | Uncovered | NotCurrent | Unknown` for an explicit `asOf`;
- details expose the same alignment query and explanation time;
- `Uncovered` is never labelled `Denied`;
- status visibility follows Requirement read authority;
- Rule-level evidence remains hidden in the first I14 slice;
- no configured/observed state is implied.

Important:
- Requirement lifecycle shows only `Active | Retired`;
- do not display `Pending/Approved/Rejected`;
- alignment status is a recomputed composition result, not Requirement lifecycle.

### 9. Connectivity Decisions — planned for I16 after the Web UI Quality Gate

Purpose: inspect and record durable final Connectivity Decisions through the accepted I15 domain boundary.

List/read:
- admitted Decision Governance Scope;
- exact Source/Destination/DCS subject;
- `Allowed | NotAllowed`;
- validity;
- reason summary;
- deciding principal/time and Decision ID.

Record:
- select one admitted Decision Governance Scope;
- select an exact admitted subject;
- choose final `Allowed | NotAllowed`;
- provide required reason and validity inputs;
- optionally preserve accepted evidence references;
- submit through backend-owned actor/time/authority provenance.

Details:
- immutable Decision identity and exact subject;
- Governance Scope;
- final outcome;
- validity;
- reason/evidence references;
- deciding provenance;
- supersession relationship/history where present.

The screen must not display a fabricated pending case lifecycle. It is rendered in navigation only when the backend route/use cases exist.

### Deferred screens

- Dashboard: add after source screens expose real data/metrics.
- Global audit log: add when a concrete cross-entity audit query/use case is required; Rule business history is sufficient for the first increment.
- Resource/application portfolio administration: only when a concrete owner workflow requires it.
- Approval/review queue: deferred unless later canonical Connectivity Decision requirements introduce an explicit case/workflow lifecycle.

## Product class and primary operating environment

NAPMS Web UI is a professional network/infrastructure operations application in the same broad interaction class as tools such as NetBox: technically skilled authenticated users work with structured objects, policy state, provenance and repeated operational workflows over sustained desktop sessions.

This comparison is a **product-class reference**, not a visual/theme or information-architecture dependency. NAPMS keeps its own domain/workflow structure:

```text
Requirement -> Decision -> Access Rule -> Effective Policy -> realization/evidence
```

Accepted consequences:
- primary optimization target is a desktop/laptop workstation, not a phone-sized application;
- information density and direct comparability take priority over decorative whitespace/cards;
- entity collections with multiple comparable attributes are table-first;
- deep objects/workflows use bookmarkable detail pages rather than mobile-style stacked navigation;
- filters, search, sorting, pagination and current view state should remain visible and URL-shareable where practical;
- stable technical identity/provenance stay available without displacing readable labels;
- keyboard use and repeated operator actions are first-class desktop concerns;
- mobile compatibility must prevent broken/inaccessible UI, but mobile does not redefine the desktop information architecture.

The UI must not be redesigned into a card-per-object/mobile-dashboard model merely to avoid horizontal density.

## Desktop-first viewport contract

Quality targets are ordered:

1. **Primary desktop baseline — 1440 x 900/1000-class viewport**
   - full navigation shell;
   - full operational table/detail density;
   - primary visual-regression baseline.
2. **Minimum supported desktop workspace — 1280 x 800**
   - all normal single-object workflows are fully usable;
   - no critical action requires horizontal page scrolling outside an explicitly scrollable dense table/technical region.
3. **Tablet compatibility — around 768px**
   - same information architecture;
   - navigation may collapse/off-canvas;
   - dense tables may use explicit horizontal scrolling or selectively hide non-critical presentation-only columns.
4. **Mobile compatibility — around 390px**
   - authentication, navigation, reading details and safe single-object actions remain reachable;
   - no clipped controls, inaccessible actions or document-level horizontal overflow;
   - complex dense analysis/bulk workflows may remain desktop-optimized and are not required to become card-first/mobile-native experiences.

Responsive changes must preserve domain meaning and action availability. Presentation may change; semantic status, identity and admitted capabilities may not.

## Planned-capability preview policy

NAPMS may expose accepted **future user-facing roadmap capabilities** in the Web UI before their backend/runtime implementation exists so the product shell, navigation, information architecture and screen composition can be reviewed early.

This is allowed only as an explicit preview contract.

Rules:
- every preview surface must map to an accepted roadmap increment or canonical requirement; do not invent speculative product capabilities;
- navigation to a preview surface is functional: selecting it opens a real preview route/page rather than a dead navigation control;
- every preview page and preview-only action is visibly labelled `Preview` / `Planned Ixx` and must not be visually indistinguishable from executable product behavior;
- preview screens may show layout, section headings, known fields/columns, filters and action placement only where those concepts are already accepted;
- unknown domain semantics remain visibly unspecified; do not invent statuses, workflow states, mutation semantics, metrics or authoritative data merely to make the mock look complete;
- existing demo/read-only illustrative values may be used only when clearly marked non-authoritative and when they do not create new domain meaning;
- a future mutation control must not appear enabled unless it actually invokes an implemented backend capability; use disabled controls with adjacent explanation, or a non-interactive action preview;
- disabled state alone is insufficient communication: the screen must state why the capability is unavailable and identify the planned increment;
- preview surfaces are excluded from authority claims: their visibility does not imply the authenticated actor is or will be authorized for the future capability;
- when a real feature ships, its preview marker is removed only after browser tests prove the executable route and relevant actions;
- preview pages participate in desktop visual-regression testing because one purpose is to validate the future product shell before implementation;
- infrastructure-only roadmap work is not forced into product navigation. Production hardening, deployment, backup/restore, observability plumbing and similar non-user-facing work remain outside the UI unless a concrete operator use case later requires a surface.

This preview policy supersedes the earlier blanket prohibition on inactive navigation decoration. Dead controls remain prohibited; **explicit functional preview routes are allowed**.

### Current accepted preview candidates

Based on the accepted I16-I25 roadmap, the current user-facing preview set may include:

- I16 — Connectivity Decisions;
- I17 — Technical Access Evidence;
- I18 — Technical-to-Domain Access Resolution;
- I19 — Network Enforcement Placement;
- I20 — Desired-vs-Configured Reconciliation / Enforcement Policy;
- I21 — Configuration Rendering;
- I22 — Network Environment Operations;
- I23 — Enterprise Identity / Authoritative Sources only to the extent a concrete human/operator surface is later accepted;
- I25 — global explainability/audit navigation, mature search/filter/bulk surfaces and Dashboard only where accepted read models exist.

I24 Production Deployment and Operational Hardening is not a product-navigation preview target by default.

## Information architecture

Use a desktop-first enterprise application shell:

```text
CONNECTIVITY NEEDS
  My Connectivity Needs

CONNECTIVITY GOVERNANCE
  Connectivity Decisions   # only when the I16 route is executable

ACCESS POLICY
  Compose Connectivity
  Access Rules

POLICY VIEWS
  Effective Policy
  Normalized Policy
```

Dashboard may be added above these groups only after real aggregate use cases exist.

Do not add dead navigation controls as decoration. Executable product routes and explicit planned-capability preview routes are both allowed; preview entries must carry a visible Preview/Planned marker and open a real preview page.

## Operational list/detail conventions

For NetBox-class operational data:
- default list representation is a dense table when users compare multiple objects/attributes;
- row identity/link opens a bookmarkable detail view;
- one dominant row navigation target is preferred; secondary row actions use explicit controls/menus;
- potentially unbounded collections remain server-paginated and server-filtered/sorted where supported;
- empty/filtered-empty/authority-limited/error states remain distinct;
- wide tables are allowed to scroll inside their own content region rather than force the entire application shell wider;
- card grids are reserved for genuinely summary/aggregate content, not as the default responsive replacement for operational tables;
- per-user column/order preferences may be added only after a concrete operator need exists; they are not required merely because the reference class supports them.

## Visual/design-system baseline

Accepted implementation direction:
- React + TypeScript;
- Tailwind CSS;
- shadcn/ui as the component foundation;
- Tabler-like enterprise/control-plane visual language without adopting a heavyweight admin theme;
- dark navy collapsible sidebar;
- light working area;
- blue primary accent;
- information-dense tables/forms;
- borders and restrained elevation rather than decorative cards.

The visual reference under `docs/ui/references/` defines composition/style direction only; its sample IAM/resource/request data is not NAPMS domain truth and is not a pixel-perfect contract.

Detailed tokens/layout/components are owned by `docs/ui/`.

## Interaction and state requirements

- list view state should be URL-shareable where reasonable (`page`, `sort`, `filters`, `search`);
- potentially unbounded lists use server-side pagination/filtering/sorting;
- forms validate obvious constraints client-side while the server remains authoritative;
- duplicate mutation submission is prevented while a request is pending;
- initial loading, background refresh, empty, filtered-empty, unauthorized-empty and retryable error states are distinct;
- semantic statuses use one central UI mapping and never rely on color alone;
- domain/business outcomes remain distinct from transport/authentication failures;
- provenance/audit details use progressive disclosure rather than overwhelming the primary workflow.

## Authentication/session UX

For I8 local/test runtime:
- login + password only;
- no social login, OIDC/OAuth2 or corporate IdP controls;
- explicit logout is available from the user menu;
- an expired/invalid session returns the user to Login and may preserve the intended route for post-login navigation;
- failed login must not reveal whether a login or password component was incorrect;
- exact cookie/token/session-storage mechanics and timeout values remain runtime engineering choices, subject to the security constraints in the active plan.

## Responsive baseline

The detailed viewport contract above is authoritative.

Implementation summary:
- `>= 1280px`: desktop shell and desktop information density;
- `768..1279px`: same IA with collapsible/off-canvas navigation and bounded table overflow;
- `< 768px`: compatibility mode, not a separate mobile product;
- narrow-screen navigation should preserve the desktop IA via an overlay/off-canvas navigation model rather than create a second shortened mobile-only navigation taxonomy.

## Accessibility target

Applicable Web UI behavior targets WCAG 2.2 AA.

Minimum implementation obligations:
- keyboard operation;
- visible focus states;
- semantic labels;
- accessible dialogs/drawers;
- sufficient contrast in default, hover, focus, active, disabled-where-applicable and animated/intermediate visual states;
- statuses not encoded by color alone;
- browser tests should prefer role/label-based interaction so missing accessible names fail quality gates rather than being hidden behind test-only selectors.

## Current Web UI non-goals

- persistent generic Access Request lifecycle;
- approval/review workflow;
- mobile/native applications;
- public/anonymous access;
- external enterprise SSO;
- generic IAM administration;
- generic CMDB/application-portfolio administration;
- device/firewall execution UI;
- configured-state reconciliation UI;
- vendor-specific policy rendering;
- CSV/XLSX export.
