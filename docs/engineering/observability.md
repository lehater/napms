# Logging and observability policy

Status: `accepted and exercised through I8 HTTP runtime`.

Date: 2026-09-09.

## Purpose

Define what the application must make observable without coupling Domain/Application to a logging framework or transport.

## Decision

Logging is a **central application/runtime concern**, configured and emitted at boundaries/composition rather than scattered through domain entities. Domain objects do not call a logger.

The I8 runtime uses structured JSON logging. A single application logging configuration controls handlers, format, level policy and redaction. Modules use named loggers or an injected observability abstraction only where a business-significant application event cannot be reconstructed safely at the boundary; no module configures its own handlers.

## Mandatory events for the I1 use case

At the application/runtime boundary record one completion event per command with:
- operation/use-case name;
- correlation/request ID;
- semantic outcome code;
- duration;
- actor identifier or safe correlation form;
- proposal reference when safe;
- RuleId when materialized/resolved;
- Rule semantic identity references when policy permits;
- decision/authority references when present and safe;
- dependency name for degraded/unknown dependency outcomes.

Unexpected exceptions record:
- same correlation/operation context;
- exception class and stack trace internally;
- no raw secrets or unreviewed dependency payloads.

Do not require log statements for every method call, branch or domain value construction.

## Levels

- `DEBUG`: developer diagnostic detail; disabled by default in production.
- `INFO`: successful materialized/resolved operations and normal business non-materialization such as NotAllowed when operationally useful.
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

Business audit/provenance is not replaced by application logs. Authoritative Rule provenance/audit belongs to business state/contracts. Logs are operational diagnostics and may be rotated/lost without changing domain truth.

## Failure ownership

An exception is logged once at the boundary that has enough context and owns recovery/response. Lower layers do not repeatedly log-and-rethrow the same failure. Adapters may add dependency-specific structured context but the application boundary owns the final operation outcome event.

## I8 implementation evidence

The FastAPI runtime boundary emits one JSON completion event per request with operation, correlation ID, semantic outcome, HTTP status and duration. When safe/applicable it includes authenticated actor, Rule, authority, decision and degraded dependency references.

Unexpected exceptions are returned publicly as generic failures. Internal structured events record exception class and stack-frame locations without serializing the exception message, raw payloads, credentials or connection strings.

`/health/live` proves process liveness without dependency traversal. `/health/ready` checks the admitted PostgreSQL runtime dependency and returns only safe readiness state.

Domain/Application remain free of logging-framework dependencies.
