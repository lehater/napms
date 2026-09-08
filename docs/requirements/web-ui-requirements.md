# Web UI requirements — initial baseline

Status: `accepted partial baseline — detailed UI refinement required before implementation`.

Date: 2026-09-08.

## Purpose

Define the currently accepted human-facing UI direction without prematurely fixing a template, information architecture or component library.

This document is the canonical owner for Web UI product/UX requirements. Runtime/API engineering decisions remain in the active execution plan and engineering artifacts.

## Accepted product direction

### First human-facing consumer

The first intended human-facing consumer is a **Web UI** backed by the NAPMS HTTP JSON API.

The UI is not a second source of business truth. Access Policy, Authority Management, Application Communication Catalogue and Resource Catalogue semantics remain in the backend application/domain modules.

### UI design is a separate refinement step

The Web UI must be designed/refined separately before screen implementation.

The refinement must cover:
- user roles and concrete user journeys;
- screen inventory;
- information architecture and navigation;
- selected dashboard/template/design-system approach;
- state/error/empty/loading behavior;
- component/layout rules;
- development handoff artifacts such as screen mockups/images and an implementation-oriented UI specification.

Backend API routes should be derived from accepted application use cases and UI journeys rather than from generic CRUD over database tables.

### Visual direction

Accepted visual direction:
- blue / dark-blue / navy primary palette;
- restrained enterprise/administrative appearance;
- dashboard/workspace-oriented product rather than a document-only or form-only interface;
- clear visual hierarchy suitable for dense operational data.

The exact template, component library, navigation layout, typography, spacing system and light/dark treatment remain open until UI refinement.

### Personal workspaces and authority separation

Resource/system owners need a personal workspace where they can:
- see the resources/systems within their authorized scope;
- inspect relevant connectivity/access state;
- declare/request a connectivity need for their scope;
- see the state/result of that request.

Declaring a need does **not** grant access. Approval/authorization must be performed by another actor with the required authority.

The UI must not allow a resource/system owner to bypass Authority Management or self-approve merely because the resource is visible in their workspace.

### Authorization-aware presentation

The UI may present only actions/data returned or admitted by backend use cases for the authenticated actor/scope.

Client-side hiding/disabling is UX only and never the security boundary. Backend Authority checks remain authoritative.

## Authentication baseline for the current test/local stage

For the current controlled/test stage:
- local `login + password` authentication is sufficient;
- no external OIDC/OAuth2/enterprise IdP integration is required yet;
- authentication must establish a trusted backend actor identity; ordinary request payload fields must not be able to spoof `actor_id`;
- password material must never be stored or logged in plaintext;
- the authentication boundary must be replaceable later without changing Domain/Application semantics or Authority Management.

Exact session/token mechanics are an I8 runtime decision/implementation detail.

External corporate identity integration is explicitly deferred.

## Normalized policy/export UI boundary

The primary machine-facing normalized export handoff is JSON through the HTTP API.

CSV/XLSX and other downloadable representations are deferred until a concrete consumer/use case requires them.

The Web UI may display normalized-policy data, but serialization/presentation must not redefine normalized policy semantics or drop required provenance.

## Candidate screen inventory for refinement

The following are **candidate screens**, not yet accepted implementation scope:

1. Login.
2. Role/scope-aware dashboard.
3. My resources / systems.
4. Connectivity need/request composition.
5. Request/rule status and details.
6. Approval/review queue for authorized reviewers.
7. Access Rule details, state, EffectiveWindow and business history.
8. Effective desired policy view.
9. Normalized policy/export view.
10. Administration/reference-data surfaces only where concrete owner workflows require them.

The UI refinement step may merge, split or remove these screens.

## Open UI decisions

Must be resolved before Web UI implementation:

- exact role/persona set represented in the first UI increment;
- first end-to-end user journeys and acceptance examples;
- initial screen set;
- sidebar vs top navigation vs hybrid information architecture;
- exact dashboard/template/design system/component library;
- table density, filtering/search, detail-panel patterns;
- responsive/mobile requirements;
- light/dark theme requirements;
- accessibility target;
- login/session UX and timeout/logout behavior;
- error/denied/unknown/stale-data presentation;
- how provenance/audit detail is progressively disclosed without overwhelming normal workflows.

## Non-goals for the current UI baseline

Not yet implied:
- mobile/native applications;
- public/anonymous access;
- external enterprise SSO;
- device/firewall execution UI;
- configured-state reconciliation UI;
- generic IAM administration;
- generic CMDB/application-portfolio UI;
- vendor-specific policy rendering.
