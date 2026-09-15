# Logging and observability policy

## Purpose

Define what the application makes observable without coupling Domain/Application to a logging framework or transport.

## Logging boundary

Logging is a central runtime concern configured and emitted at application/transport/composition boundaries. Domain objects do not call a logger.

The runtime uses structured JSON logging. One application logging configuration owns handlers, formatting, level policy and redaction. Modules do not configure their own handlers.

An application module may use an injected observability abstraction only when a business-significant application event cannot be reconstructed safely at an owning boundary.

## Operation context

At the application/runtime boundary record one completion event per command/request with, when applicable:

- operation/use-case name;
- correlation/request ID;
- semantic outcome code;
- duration;
- authenticated actor identifier or safe correlation form;
- relevant safe business/provenance references;
- dependency identity for degraded/unknown dependency outcomes.

Unexpected exceptions include the same operation/correlation context plus internal exception class/stack location. Raw secrets and unreviewed dependency payloads are not logged.

Do not require logging for every method call, branch or domain value construction.

## Levels

- `DEBUG`: developer diagnostic detail.
- `INFO`: successful operations and normal outcomes when operationally useful.
- `WARNING`: fail-closed denied/invalid/unknown/dependency-unavailable outcomes requiring operational visibility but not representing application defects.
- `ERROR`: unexpected application/adapter failure or inability to establish authoritative execution/persistence outcome.
- `CRITICAL`: process/system integrity failure, not ordinary business rejection.

Level policy may be tuned for volume without changing semantic outcome identity.

## Correlation

A correlation ID is created or accepted by the outer runtime boundary and propagated through application execution and outbound adapters. Correlation identity is diagnostic only and never replaces domain identity.

## Sensitive data

Never log secrets, tokens, credentials, connection strings, raw external payloads by default, stack traces in user-facing responses, unrelated protected domain facts or secret-bearing configuration dumps.

Identifiers are logged only when needed for traceability. Redaction occurs before serialization/output.

## Audit versus operational log

Business provenance/audit is domain/application state owned by the relevant semantic contract. Operational logs are diagnostic and may be rotated or lost without changing project truth.

An exception is logged once at the boundary that owns recovery/response and has enough context. Lower layers do not repeatedly log and rethrow the same failure.

## HTTP/runtime evidence

The HTTP boundary emits one structured completion event per request including operation, correlation ID, semantic outcome, HTTP status and duration. Safe actor/domain/dependency references may be included when relevant.

Unexpected exceptions are returned externally as generic failures while internal structured events retain diagnostic class/location without serializing secret-bearing exception text or raw payloads.

```text
/health/live  -> process liveness without dependency traversal
/health/ready -> readiness of required runtime dependencies
```

Domain/Application remain logging-framework independent.

## Local operator diagnostics

```bash
make dev-status
make dev-logs
```

`dev-status` verifies Compose service state, public liveness/readiness and a real PostgreSQL query through the local operator boundary. It exits non-zero when a required probe fails.

`dev-logs` follows service logs including structured API completion events.

Recommended diagnosis order:

1. `make dev-status` to establish runtime health;
2. `make dev-logs` for failing status or request diagnosis;
3. correlate a request through its correlation ID;
4. use supported backup/recovery tooling rather than editing durable database state to repair operational failures.

The current local runtime does not require a metrics backend. Health/readiness, Compose state and structured logs are the supported operator observability surface.
