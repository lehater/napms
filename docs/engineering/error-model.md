# Error and message model

## Purpose

Define failure semantics without coupling Domain/Application to HTTP, database-driver or provider exception types.

## Outcome rule

Expected business/application outcomes are explicit typed results rather than exceptions. Examples include accepted/completed, denied/not-authorized, invalid input or semantic conflict, unresolved/unknown dependency truth, and precondition failure.

The exact outcome vocabulary belongs to the owning use case/domain contract. Generic infrastructure must not invent or reinterpret domain meaning.

Domain exceptions are reserved for attempts to construct or mutate impossible domain state. They are not transport messages and are not normal business branching.

Unexpected programming defects propagate to the application/runtime boundary, where they are correlated/logged and mapped to a generic external failure response.

Technical adapter failures are translated at the adapter/application boundary into infrastructure-neutral port semantics. Vendor, framework and driver exception classes do not enter Domain/Application contracts.

## Fail-closed semantics

`Unknown` / `Unavailable` is distinct from a negative business answer. Where authoritative permission, completeness, identity or consistency is required, unresolved technical truth fails closed rather than being converted to denial, absence, an empty set or success.

Subject/correlation mismatch is an explicit conflict and is never silently repaired by substituting another object.

## Persistence uncertainty

No application success is reported unless authoritative persistence outcome is established.

Adapters distinguish semantic uniqueness/idempotency conflicts from general persistence failure and from unknown commit outcome. Only an explicitly named semantic uniqueness condition may be treated as an idempotency race. Primary-key collisions or unrelated database failures are not reclassified as successful duplicate resolution.

When commit acknowledgement is uncertain, callers must not infer success or blindly repeat a non-idempotent mutation. Recovery/reconciliation uses the owning operation's explicit identity and current authoritative state.

## Stable error identity

Application outcomes are stable machine-readable semantic identities. Infrastructure failures use stable port-level execution identities. Public transport codes, when present, are symbolic application/transport contracts rather than Python/vendor exception class names.

Transport adapters may map outcomes to HTTP/status/message forms but do not redefine their meaning.

## Messages

Core code does not own localized or user-facing prose. Core results carry semantic facts and safe references. Presentation adapters own wording.

User-facing messages never expose internal exception text/stack traces, credentials or connection strings, raw dependency payloads, database/driver/vendor details, or unrelated protected domain facts.

Diagnostic detail belongs to internal observability subject to redaction policy.

## Invariants

- expected semantic outcomes are explicit values;
- unresolved authoritative truth is distinct from a negative result and fails closed when required;
- dependency subject/correlation mismatch is never silently repaired;
- failed or unknown mutation/persistence outcomes do not become success;
- Domain/Application do not depend on HTTP status codes, FastAPI exceptions, database exceptions or external SDK exception classes;
- infrastructure translation occurs at adapter/application boundaries;
- presentation wording does not become domain error identity.
