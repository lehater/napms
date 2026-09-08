# PLAN-008 — I8 first consumer/runtime boundary

Status: `active`

## Goal

Select and implement the first concrete outer runtime boundary for the already-proven greenfield Wave-1 application, driven by an actual consumer rather than by a conventional technology choice.

I8 must not redefine Access Policy, Authority, ACC, RC, Export Snapshot or normalized-row semantics.

## Current stage

Owner decision required before transport/handoff code.

I7 proves direct local-dev application composition against PostgreSQL. The repository deliberately has no accepted first external consumer, HTTP/CLI contract or public normalized-export serialization.

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

### D1 — First actual consumer

Name the first consumer of the runtime boundary.

Examples only:
- a web/UI backend;
- another internal service;
- an operator/administrator using a CLI;
- a scheduled automation/job.

Do not choose a transport until this consumer is explicit.

### D2 — Invocation surface

Choose the minimum surface required by D1:
- HTTP API;
- CLI;
- scheduled/internal application runner;
- another explicit boundary.

### D3 — Actor identity/authentication handoff

Define how the runtime obtains the actor identity used by Authority Management.

The runtime must distinguish authenticated/trusted identity from arbitrary request fields. Full IAM is not implied, but an untrusted caller-supplied actor ID is not sufficient for an admitted non-test runtime.

### D4 — Normalized export handoff

Only if D1 requires external export delivery, select the minimum representation:
- synchronous structured response;
- JSON artifact;
- CSV/XLSX artifact;
- persisted/downloadable artifact;
- another explicit consumer contract.

Serialization is replaceable interface detail and must retain all required provenance/semantics.

### D5 — Operability boundary

Implement the already accepted observability obligations:
- correlation/request ID;
- one structured completion event per operation;
- semantic outcome code;
- duration;
- safe Rule/decision/authority/dependency references when applicable;
- unexpected exception context without secrets/raw payload leakage;
- explicit startup/configuration failure.

Choose a logging sink/format only to the extent needed by the selected runtime.

## Work packages

1. Resolve D1-D4 with the owner; D5 semantics are already accepted.
2. Record the bounded runtime contract before framework/serializer code.
3. Add only the transport/authentication/serialization dependencies admitted by that contract.
4. Wire the runtime through the existing typed configuration and explicit composition root.
5. Prove semantic outcome -> transport/result mapping for positive and fail-closed cases.
6. Prove actor identity cannot be spoofed through ordinary request payload fields.
7. Prove structured correlation/logging and secret redaction.
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

D1-D4 are not yet owner-accepted.

No HTTP/CLI/public serializer/authentication adapter should be implemented before those decisions.

## Next

After I8, choose the next wave/increment from accepted product priorities and the Wave-1 deferral register. Do not preselect rendering/device execution without a corresponding product decision.
