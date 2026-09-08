# Web UI requirements — accepted I8 refinement

Status: `accepted through I10 Policy Operations Workspace`.

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

## Connectivity Decision deferral

I8 does not implement or expose an approval workflow.

The current stable seam remains:

```text
Access Rule Proposal
    -> ConnectivityDecision(Allowed | NotAllowed)
    -> Access Policy
```

Do not introduce UI/domain concepts such as persistent `Access Request`, `Pending`, `Approved`, `Rejected`, approval queue, approver, human approval lifecycle or self-approval.

If a future product increment must manage the Connectivity Decision process, first reopen the deferred Connectivity Decision Domain and define its semantics before adding workflow UI.

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

### 3. Proposal Result

Purpose: present the semantic result of proposal submission.

Outcomes:
- `Allowed` -> created/resolved Access Rule summary and navigation to Rule Details;
- `NotAllowed` -> explicit business outcome with no Rule;
- denied/unknown authority, invalid interaction, not-found, stale/conflict or dependency failure -> distinct recoverable/error presentation where applicable.

This may be a result state of Compose Connectivity rather than a dedicated route.

### 4. Access Rules

Purpose: inspect authoritative Access Rules visible through explicit `ReadAccessRule` authority. List results contain only Rules from unambiguously permitted governance scopes; read authority does not imply mutation authority.

Initial useful data includes Rule ID, source deployment, destination deployment, DCS revision/reference, governance scope, operational state and effective-window summary where available.

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

The UI presentation must not redefine or omit normalized export meaning.

### Deferred screens

- Dashboard: add after source screens expose real data/metrics.
- Global audit log: add when a concrete cross-entity audit query/use case is required; Rule business history is sufficient for the first increment.
- Resource/application portfolio administration: only when a concrete owner workflow requires it.
- Approval/review queue: deferred with the Connectivity Decision Domain.

## Information architecture

Use a desktop-first enterprise application shell:

```text
ACCESS POLICY
  Compose Connectivity
  Access Rules

POLICY VIEWS
  Effective Policy
  Normalized Policy
```

Dashboard may be added above these groups only after real aggregate use cases exist.

Do not add inactive navigation controls as decoration.

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

- `>= 1280px`: full desktop shell;
- `768..1279px`: collapsed sidebar by default; dense tables may scroll horizontally;
- `< 768px`: functional overlay navigation and usable forms/details, without making mobile the primary optimization target.

## Accessibility target

Applicable Web UI behavior targets WCAG 2.2 AA.

Minimum implementation obligations:
- keyboard operation;
- visible focus states;
- semantic labels;
- accessible dialogs/drawers;
- sufficient contrast;
- statuses not encoded by color alone.

## Non-goals for I8 UI

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
