# PLAN-008 — I8 first consumer/runtime boundary

Status: `active`

## Goal

Select and implement the first concrete outer runtime boundary for the already-proven greenfield Wave-1 application, driven by an actual consumer rather than by a conventional technology choice.

I8 must not redefine Access Policy, Authority, ACC, RC, Export Snapshot or normalized-row semantics.

## Current stage

Web UI refinement, HTTP runtime, first Web UI slice and normalized-policy JSON handoff are implemented and green. The current stage is **WP6–WP7 — complete observability and runtime failure-mapping proof**.

Accepted:
- first human-facing consumer: Web UI;
- backend invocation boundary: HTTP JSON API;
- current local/test authentication: login + password through a replaceable authentication boundary;
- normalized-policy machine handoff: JSON through the API;
- operability: structured JSON logging, correlation/request ID and health/readiness behavior;
- first UI journey: Login -> Compose Connectivity -> Access Rule Proposal -> ConnectivityDecision result -> Allowed Rule summary/details;
- UI stack/direction: React + TypeScript + Tailwind + shadcn/ui, dark navy collapsible shell and dense enterprise workspace;
- approval/review workflow and persistent generic Access Request lifecycle are deferred with the Connectivity Decision Domain.

Canonical UI requirements: `docs/requirements/web-ui-requirements.md`.
Implementation-oriented visual handoff: `docs/ui/`.

## Inputs

- `docs/engineering/current-state.md`;
- `docs/requirements/web-ui-requirements.md`;
- `docs/ui/`;
- `docs/requirements/wave1-product-requirements.md`;
- `docs/requirements/wave1-semantic-contracts.md`;
- `docs/requirements/wave1-deferrals.md`;
- `docs/engineering/error-model.md`;
- `docs/engineering/configuration.md`;
- `docs/engineering/dependency-injection.md`;
- `docs/engineering/observability.md`;
- current greenfield PostgreSQL composition and end-to-end integration proof.

## Accepted constraints

- NAPMS remains greenfield; Legacy/MSSQL are not implementation dependencies;
- PostgreSQL remains the admitted relational engine;
- Domain/Application stay framework-independent;
- actor identity supplied by an outer runtime must be explicit and trustworthy enough for Authority checks; it cannot be invented from untrusted request data;
- semantic outcomes remain distinct from transport status/error syntax;
- normalized export meaning is unchanged by serialization;
- structured logging/correlation is mandatory at the first runtime boundary;
- secrets/DSNs/raw dependency payloads are never logged;
- vendor rendering/device execution remains out of scope;
- UI convenience must not invent Connectivity Decision workflow/domain semantics.

## Decision gates

### D1 — First actual consumer — accepted

The first human-facing consumer is the NAPMS **Web UI**.

The accepted first increment and visual/interaction baseline are defined by `docs/requirements/web-ui-requirements.md` and `docs/ui/`.

### D2 — Invocation surface — accepted

Use an **HTTP JSON API** as the Web UI backend boundary.

Rules:
- routes expose application use cases, not database CRUD;
- transport status/error syntax does not redefine semantic outcomes;
- Domain/Application remain framework-independent;
- concrete route shapes follow the accepted Web UI journey/use cases.

### D3 — Actor identity/authentication handoff — accepted for local/test stage

Use local **login + password** authentication for the current controlled/test runtime.

Rules:
- no external OIDC/OAuth2/corporate IdP is required in I8;
- successful authentication establishes the backend actor identity used for Authority checks;
- `actor_id` supplied in an ordinary request body/query parameter is never trusted as authentication;
- password material is never stored/logged in plaintext;
- authentication is an outer replaceable boundary so a future enterprise IdP does not change Domain/Application or Authority semantics.

Exact session/cookie/token mechanics remain an implementation choice for WP3.

### D4 — Normalized export handoff — accepted

Primary machine handoff: **JSON through the HTTP API**.

CSV/XLSX/downloadable artifacts are deferred until a concrete consumer requires them.

The JSON representation must preserve all normalized semantics/provenance required by the accepted export contract.

### D5 — Operability boundary — accepted

The first runtime boundary implements:
- structured JSON logs;
- correlation/request ID;
- one structured completion event per operation;
- semantic outcome code;
- duration;
- safe Rule/decision/authority/dependency references when applicable;
- unexpected exception context without secret/raw-payload leakage;
- explicit startup/configuration failure;
- health/readiness endpoints appropriate to the selected HTTP runtime.

## Work packages

1. **DONE — Web UI refinement.** Accepted personas/authority model, first journey, initial screen inventory, navigation, design system, interaction states, accessibility baseline and implementation-oriented handoff under `docs/ui/`.
2. **DONE — Minimum HTTP use-case contract.** Accepted in `docs/engineering/http-api-contract.md`, including trusted actor/time boundary, proposal composition support, semantic outcome mapping and health/correlation conventions.
3. **DONE — Local authentication boundary.** Hashed local credentials, opaque server-side sessions and explicit logout are implemented; proposal payload uses `extra=forbid` and executable tests prove request-supplied `actorId` cannot establish identity.
4. **DONE — HTTP JSON runtime adapter/composition + first Web UI slice.** FastAPI runtime, local-dev Decision adapter, React Login -> Compose Connectivity -> Rule-result slice and runtime/web gates are green.
5. **DONE — Normalized-policy JSON handoff.** Authorized effective-policy selection -> coherent snapshot -> normalized rows is exposed through semantics-preserving JSON; incomplete snapshots return no partial rows.
6. **ACTIVE — Observability/operability proof.** Structured completion events, correlation, health/readiness and startup/configuration failure behavior are being verified.
7. **ACTIVE — Runtime failure mappings.** Denied/unknown/not-found/stale/correlation/persistence paths are being verified with safe public errors.
8. Run core, PostgreSQL and runtime-specific gates; close all P0/P1 findings.

## Exit criteria

- first consumer and invocation surface are explicit;
- actor identity handoff is explicit and fail closed;
- public handoff format, if any, is explicit and semantics-preserving;
- runtime uses existing application ports/use cases rather than duplicating domain logic;
- structured observability/correlation obligations are executable;
- startup/config failures are explicit;
- no framework dependency leaks into Domain/Application;
- existing greenfield PostgreSQL end-to-end proof remains green;
- no open P0/P1 security, semantic, provenance, operability or architecture issue.

## Blockers

No current owner/product blocker for WP6–WP7.

Approval/review workflow is explicitly deferred. Reopen the Connectivity Decision Domain before introducing approval actors, lifecycle/statuses or queue semantics.

External IdP integration remains deferred.

## Next

Complete observability/error-mapping proof, then run final architecture/security review and all gates.
