# PLAN-008 — I8 first consumer/runtime boundary

Status: `active`

## Goal

Select and implement the first concrete outer runtime boundary for the already-proven greenfield Wave-1 application, driven by an actual consumer rather than by a conventional technology choice.

I8 must not redefine Access Policy, Authority, ACC, RC, Export Snapshot or normalized-row semantics.

## Current stage

Runtime direction is accepted; detailed Web UI refinement is the current owner/product gate before Web UI implementation and before freezing concrete HTTP route shapes.

Accepted:
- first human-facing consumer: Web UI;
- backend invocation boundary: HTTP JSON API;
- current local/test authentication: login + password through a replaceable authentication boundary;
- normalized-policy machine handoff: JSON through the API;
- operability: structured JSON logging, correlation/request ID and health/readiness behavior.

The UI itself must be refined separately under `docs/requirements/web-ui-requirements.md`: user journeys, screen inventory, information architecture and template/design-system choice are intentionally not yet frozen.

## Inputs

- `docs/engineering/current-state.md`;
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
- vendor rendering/device execution remains out of scope.

## Decision gates

### D1 — First actual consumer — accepted

The first human-facing consumer is the NAPMS **Web UI**.

The Web UI design is a separate product/UX refinement step. The choice of dashboard/template/design system is not an infrastructure default and must be accepted before UI implementation.

Canonical UI requirements: `docs/requirements/web-ui-requirements.md`.

### D2 — Invocation surface — accepted

Use an **HTTP JSON API** as the Web UI backend boundary.

Rules:
- routes expose application use cases, not database CRUD;
- transport status/error syntax does not redefine semantic outcomes;
- Domain/Application remain framework-independent;
- concrete route shapes should follow accepted Web UI journeys/use cases.

### D3 — Actor identity/authentication handoff — accepted for local/test stage

Use local **login + password** authentication for the current controlled/test runtime.

Rules:
- no external OIDC/OAuth2/corporate IdP is required in I8;
- successful authentication establishes the backend actor identity used for Authority checks;
- `actor_id` supplied in an ordinary request body/query parameter is never trusted as authentication;
- password material is never stored/logged in plaintext;
- authentication is an outer replaceable boundary so a future enterprise IdP does not change Domain/Application or Authority semantics.

Exact session/cookie/token mechanics remain an implementation choice to resolve with the Web UI/runtime contract.

External IdP integration is deferred.

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

1. Refine the first Web UI increment under `docs/requirements/web-ui-requirements.md`:
   - personas/roles;
   - top user journeys;
   - screen inventory;
   - navigation/information architecture;
   - dashboard/template/design-system choice;
   - implementation-oriented visual/specification handoff.
2. Derive the minimum HTTP use-case contract from the accepted UI journeys and existing application use cases.
3. Implement the replaceable local login/password authentication boundary and prove request-payload actor spoofing cannot establish identity.
4. Implement the HTTP JSON runtime adapter and wire it through the existing typed configuration/composition root.
5. Implement JSON representation for normalized policy where required by the accepted first UI/API journeys.
6. Implement structured JSON logging, correlation/request ID, health/readiness and startup/configuration failure behavior.
7. Prove positive plus denied/unknown/not-found/stale/correlation failure mappings without leaking domain/infrastructure internals.
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

High-level runtime decisions D1-D5 are accepted.

Before Web UI implementation and before freezing concrete HTTP route shapes, resolve the open UI refinement items in `docs/requirements/web-ui-requirements.md`.

Local authentication/session mechanics may be designed as part of that bounded runtime/UI refinement, but external IdP integration must not be introduced.

## Next

After I8, choose the next wave/increment from accepted product priorities and the Wave-1 deferral register. Do not preselect rendering/device execution without a corresponding product decision.
