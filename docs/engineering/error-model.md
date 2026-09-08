# Error and message model

Status: `accepted pre-infrastructure engineering decision`.

Date: 2026-09-08.

## Purpose

Define failure semantics for the executable core before transport, persistence, logging and external adapters are introduced.

## Decision

The application distinguishes **expected business/application outcomes** from **exceptional defects or failed technical execution**.

Expected outcomes are explicit typed results, not exceptions:
- materialized;
- existing Rule resolved idempotently;
- connectivity NotAllowed;
- authority denied;
- required authority unknown/unavailable;
- interaction invalid;
- required interaction knowledge unknown/unavailable;
- decision unknown/unavailable;
- decision-subject mismatch / rejected inconsistent dependency answer.

Domain exceptions are reserved for attempts to construct or mutate an impossible domain state. They are not transport messages and are not used for normal business branching.

Unexpected programming defects are not converted into a business outcome. They propagate to the application boundary, where infrastructure will later log/correlate them and map them to a generic failure response.

Technical adapter failures must eventually be translated at the adapter/application boundary into the relevant port-level `Unknown/Unavailable` result when the application can safely continue with an explicit degraded outcome. An adapter must not leak vendor/driver exceptions into Domain.

Persistence failure is special: no materialization success may be reported unless the authoritative result is established. Detailed transaction/concurrency exception mapping belongs I2, but it must preserve this rule.

## Stable error identity

Application outcomes are the stable machine-readable error/non-success identity for I1. Human-readable messages are presentation concerns and must not be parsed to recover semantics.

Transport adapters may later map an application outcome to HTTP/status/message, but they must not redefine the outcome. Public error codes, if introduced, are stable symbolic codes derived from application semantics rather than Python exception class names.

## Messages

Core code does not own localized/user-facing prose. Core results carry semantic facts and safe references only. Presentation adapters own user-facing wording.

Messages must never expose:
- internal exception text or stack traces;
- secrets/configuration values;
- unrelated authority/catalogue/decision data;
- database/driver/vendor details.

Diagnostic detail may be attached to internal observability context later, subject to the logging policy.

## Invariants

- `NotAllowed` is a valid business result, never an infrastructure error.
- `Unknown/Unavailable` is distinct from denied/not-allowed and always fails closed where permission/validity is required.
- dependency subject mismatch is never silently repaired or substituted.
- rejected/unknown outcomes leave authoritative Rule state unchanged.
- Domain/Application do not depend on HTTP status codes, FastAPI exceptions, database exceptions or external SDK exception classes.

## I1 implementation consequence

The current `MaterializationOutcome` result model is retained as the application branching mechanism. Domain invariant failures use a domain-specific exception rather than generic `ValueError`. Transport/persistence-specific exception taxonomy is intentionally deferred until the corresponding adapter exists.
