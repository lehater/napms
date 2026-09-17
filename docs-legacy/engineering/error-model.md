# Error and message model

Status: `accepted engineering decision`.

Date: 2026-09-08.

## Purpose

Define failure semantics for the executable core and infrastructure boundaries without coupling Domain/Application to transport, database or vendor exception types.

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

Unexpected programming defects are not converted into a business outcome. They propagate to the application boundary, where infrastructure later logs/correlates them and maps them to a generic failure response.

Technical adapter failures are translated at the adapter/application boundary into port-level semantics. Vendor/driver exception classes do not enter Domain/Application contracts.

Persistence failure is special: no materialization success may be reported unless the authoritative result is established.

## I2 persistence exception contract

The Access Policy repository port exposes infrastructure-neutral persistence failures:

- `RuleSemanticIdentityConflict` — the authoritative semantic-identity unique constraint selected another Rule; application may resolve that winner by exact identity;
- `AccessRulePersistenceError` — persistence execution failed and no application success is established;
- `AccessRuleCommitOutcomeUnknown` — commit acknowledgement failed and the server-side outcome may be uncertain.

The PostgreSQL adapter translates only the named semantic-identity unique constraint to `RuleSemanticIdentityConflict`. A primary-key collision or other database failure is not misclassified as an idempotency race.

On `AccessRulePersistenceError` or `AccessRuleCommitOutcomeUnknown`, the current materialization use case returns no success; the exception propagates to the application boundary. An outer operation/composition layer may later perform authoritative recovery/reconciliation, but it must not infer success from the failed acknowledgement.

## Stable error identity

Application outcomes are the stable machine-readable business/non-success identity. Infrastructure failure classes are stable port-level execution identities, not user-facing messages.

Transport adapters may later map an application outcome or infrastructure failure to HTTP/status/message, but they must not redefine domain meaning. Public error codes, if introduced, are symbolic codes rather than Python/vendor exception class names.

## Messages

Core code does not own localized/user-facing prose. Core results carry semantic facts and safe references only. Presentation adapters own user-facing wording.

Messages must never expose:
- internal exception text or stack traces;
- secrets/configuration values;
- unrelated authority/catalogue/decision data;
- database/driver/vendor details.

Diagnostic detail may be attached to internal observability context, subject to the logging policy.

## Invariants

- `NotAllowed` is a valid business result, never an infrastructure error.
- `Unknown/Unavailable` is distinct from denied/not-allowed and always fails closed where permission/validity is required.
- dependency subject mismatch is never silently repaired or substituted.
- rejected/unknown outcomes leave authoritative Rule state unchanged.
- Domain/Application do not depend on HTTP status codes, FastAPI exceptions, database exceptions or external SDK exception classes.
- a database uniqueness failure is treated as idempotent Rule resolution only when it is specifically the authoritative `RuleSemanticIdentity` constraint.
