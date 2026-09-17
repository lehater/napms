# Logging and observability policy

Status: `accepted and exercised through I24 local operational diagnostics`.

Date: 2026-09-10.

## Purpose

Define what the application must make observable without coupling Domain/Application to a logging framework or transport.

## Decision

Logging is a **central application/runtime concern**, configured and emitted at boundaries/composition rather than scattered through domain entities. Domain objects do not call a logger.

The runtime uses structured JSON logging. A single application logging configuration controls handlers, format, level policy and redaction. Modules use named loggers or an injected observability abstraction only where a business-significant application event cannot be reconstructed safely at the boundary; no module configures its own handlers.

## Mandatory operation context

At the application/runtime boundary record one completion event per command/request with:
- operation/use-case name;
- correlation/request ID;
- semantic outcome code;
- duration;
- actor identifier or safe correlation form when applicable;
- relevant business/provenance references when safe;
- dependency name for degraded/unknown dependency outcomes.

Unexpected exceptions record:
- same correlation/operation context;
- exception class and stack trace internally;
- no raw secrets or unreviewed dependency payloads.

Do not require log statements for every method call, branch or domain value construction.

## Levels

- `DEBUG`: developer diagnostic detail; disabled by default in production-like operation.
- `INFO`: successful operations and normal business outcomes when operationally useful.
- `WARNING`: fail-closed denied/invalid/unknown/dependency-unavailable outcomes that require operational visibility but are not application defects.
- `ERROR`: unexpected application/adapter failure or inability to establish authoritative persistence outcome.
- `CRITICAL`: reserved for process/system integrity failure; not normal business rejection.

Exact level may be refined for high-volume outcomes after telemetry exists, without changing semantic outcome identity.

## Correlation

A correlation ID is created or accepted by the outer runtime boundary and propagated through application execution and outbound adapters. Domain identity must never be replaced by correlation identity. Correlation is diagnostic only.

## Sensitive data

Never log:
- secrets, tokens, credentials or connection strings;
- full external payloads by default;
- stack traces to user-facing responses;
- unrelated catalogue/authority/decision facts;
- configuration dumps containing secrets.

Identifiers are logged only when needed for traceability and according to deployment privacy policy. Redaction occurs centrally before serialization/output.

## Audit vs operational log

Business audit/provenance is not replaced by application logs. Authoritative domain provenance belongs to business state/contracts. Logs are operational diagnostics and may be rotated/lost without changing domain truth.

## Failure ownership

An exception is logged once at the boundary that has enough context and owns recovery/response. Lower layers do not repeatedly log-and-rethrow the same failure. Adapters may add dependency-specific structured context but the application boundary owns the final operation outcome event.

## Runtime evidence

The FastAPI runtime boundary emits one JSON completion event per request with operation, correlation ID, semantic outcome, HTTP status and duration. When safe/applicable it includes authenticated actor and relevant domain/dependency references.

Unexpected exceptions are returned publicly as generic failures. Internal structured events record exception class and stack-frame locations without serializing the exception message, raw payloads, credentials or connection strings.

`/health/live` proves process liveness without dependency traversal. `/health/ready` checks the admitted PostgreSQL runtime dependency and returns only safe readiness state.

Domain/Application remain free of logging-framework dependencies.

## I24 local operator diagnostics

For the supported local Docker deployment:

```bash
make dev-status
make dev-logs
```

`dev-status`:
- prints current Compose service state;
- requires the public nginx `/health/live` endpoint to return `alive`;
- requires the public nginx `/health/ready` endpoint to return `ready`;
- requires a real `SELECT 1` against the local PostgreSQL database through the container-local operator boundary;
- exits non-zero if any required probe fails.

`dev-logs` follows the Compose service logs, including structured API completion events.

Recommended diagnosis order:
1. run `make dev-status` to distinguish healthy vs unavailable runtime;
2. run `make dev-logs` when status fails or an application request needs correlation-level diagnosis;
3. use the correlation ID from a failing HTTP response/log completion event to inspect the relevant structured runtime event;
4. use backup/recovery tooling rather than editing durable database state to repair operational failures.

No metrics backend is added in I24 because the current local operator use cases are satisfied by health/readiness, Compose state and structured logs. Adding a metrics stack remains evidence-driven rather than a product-completion prerequisite.
