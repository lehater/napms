# Backend operability design

Status: ACCEPTED candidate after Coding-Agent Challenge 01

## Responsibility

Own runtime evidence, configuration semantics, health/readiness, dependency-failure visibility, cancellation and shutdown behavior. Product/domain/security/interface truth remains owned upstream.

## Diagnostic contract

Every external request has the accepted correlationId from the HTTP contract. Logs/metrics include correlationId plus safe operation/outcome fields.

Required structured event classes:

- `request.completed`: correlationId, operation, HTTP status class, application outcome code when present, duration;
- `authn.failed`: correlationId, reason category `MISSING|MALFORMED|INVALID_SIGNATURE|EXPIRED|ISSUER|AUDIENCE`; never token contents;
- `authz.denied`: correlationId, operation, required permission, principal subject;
- `command.committed`: correlationId, owner module, command kind, safe aggregate ref, resulting version where applicable;
- `command.conflict`: correlationId, owner module, command kind, `STALE_VERSION|IDEMPOTENCY_CONFLICT|DECISION_ALREADY_FINAL`;
- `permission.recorded`: correlationId, requestRef, ALLOWED|DENIED, deciding principal subject, optional safe decisionRef;
- `policy.materialization.completed`: correlationId, COMPLETE|UNRESOLVED, evaluationAt, ruleCount, rowCount, unresolvedCount, duration;
- `dependency.failure`: correlationId when request-bound, dependency `DATABASE|OIDC`, `TIMEOUT|UNAVAILABLE|INVALID_RESPONSE`;
- `unexpected.failure`: correlationId, stable internal error class; stack trace only in protected server logs;
- `runtime.startup.failed`: configuration/dependency category without secret values;
- `runtime.shutdown`: start/completed/forced-cancellation and in-flight count.

Logs are diagnostic evidence, never authoritative domain/audit history.

## Metrics

Instrumentation must expose at minimum:

- request count and duration by operation/outcome class;
- authentication failure count by safe reason category;
- authorization denial count by operation/permission;
- stale-version, idempotency-conflict and final-decision-conflict counts;
- policy materialization duration, input-rule count, output-row count and unresolved count;
- database operation failure/timeout count;
- OIDC metadata/JWKS refresh success/failure count;
- readiness state and process-start count.

No alert threshold, latency SLO or availability target is invented. Metric names/export protocol are implementation freedoms if these dimensions remain available to the operational consumer.

## Startup configuration contract

Configuration has one precedence rule: **process environment at startup is the only application configuration source** for this MVP.

A platform secret manager may inject environment values, but there is:
- no application config file;
- no command-line override layer;
- no runtime reload;
- no dynamic feature flag;
- no mutable configuration endpoint.

Changing configuration requires process restart.

Required environment keys:

| Key | Meaning / validation | Secret |
| --- | --- | --- |
| `NAPMS_LISTEN_ADDR` | non-empty HTTP listen address | no |
| `NAPMS_DATABASE_DSN` | PostgreSQL connection DSN | yes |
| `NAPMS_OIDC_ISSUER` | absolute HTTPS issuer URL except explicitly local test issuer | no |
| `NAPMS_OIDC_AUDIENCE` | non-empty required audience | no |
| `NAPMS_OIDC_PERMISSION_CLAIM` | non-empty claim name containing effective permission strings | no |
| `NAPMS_DB_STATEMENT_TIMEOUT` | duration > 0 | no |
| `NAPMS_HTTP_REQUEST_TIMEOUT` | duration > 0, bounds one external request including materialization | no |
| `NAPMS_OIDC_HTTP_TIMEOUT` | duration > 0 for metadata/JWKS HTTP attempt | no |
| `NAPMS_OIDC_FETCH_MAX_ATTEMPTS` | integer >= 1 | no |
| `NAPMS_OIDC_FETCH_BACKOFF` | duration >= 0 between OIDC fetch attempts | no |
| `NAPMS_JWKS_MAX_STALE` | duration >= 0 during which already-cached signing keys may remain usable if refresh fails | no |
| `NAPMS_SHUTDOWN_GRACE` | duration > 0 for in-flight graceful shutdown | no |

Optional:
- `NAPMS_LOG_LEVEL`: `DEBUG|INFO|WARN|ERROR`, default `INFO`;
- telemetry exporter/sink configuration may be added by the selected observability library, but must not change application semantics or leak secrets.

Unknown `NAPMS_*` keys are startup errors rather than silently ignored typos.

Invalid/missing required configuration:
1. emits `runtime.startup.failed` with safe key/category only;
2. exits non-zero;
3. never starts the HTTP listener.

The application never logs the value of a key classified secret.

## OIDC key/cache/dependency semantics

- issuer/audience/permission-claim configuration is fixed for the process lifetime;
- token signature/issuer/audience/time checks always fail closed;
- metadata/JWKS retrieval uses at most `NAPMS_OIDC_FETCH_MAX_ATTEMPTS`, each bounded by `NAPMS_OIDC_HTTP_TIMEOUT`, with the configured backoff;
- cached signing keys may be used after refresh failure only while their cache age is <= `NAPMS_JWKS_MAX_STALE`;
- a token that is cryptographically invalid against available valid keys -> `401 AUTHENTICATION_REQUIRED`;
- when token validity cannot be established because required key material is unavailable/staler than permitted -> `503 DEPENDENCY_UNAVAILABLE`, not a false 401;
- an unknown token key id may trigger one bounded refresh sequence; if key material still cannot be obtained, use the dependency-failure rule above;
- readiness is false whenever the process lacks key material sufficient to validate protected traffic under these rules.

## Database failure semantics

- every database statement/transaction is bounded by the configured statement timeout and request context;
- application commands do not retry database mutations automatically;
- unknown commit outcome is surfaced as dependency/internal failure, never confirmed success;
- the client may retry only through accepted Idempotency-Key semantics;
- read-only query retry is not required in the application; callers can retry a failed request.

## Request timeout and cancellation

- one external request is bounded by `NAPMS_HTTP_REQUEST_TIMEOUT`;
- client cancellation and request timeout propagate to database/read materialization work;
- cancellation before commit prevents success;
- cancellation observed after a mutation committed does not rewrite the committed domain result; idempotent replay can recover the committed result;
- materialization preflight completes before HTTP 200 response commitment; preflight dependency failure maps to 503/500 normally;
- a cancelled/timeout materialization before response commitment emits no COMPLETE/UNRESOLVED body;
- cancellation/transport failure after streaming response commitment leaves an incomplete response and must not emit a successful COMPLETE materialization event;
- `policy.materialization.completed` is emitted only after a syntactically complete response result has been produced by the application path; aborted/truncated streams emit dependency/unexpected/cancellation evidence instead.

## Health

- `GET /health/live`: process/runtime loop is alive; no database/OIDC network call;
- `GET /health/ready`: true only when required configuration is valid, database read/connectivity check succeeds, and OIDC validation key material is usable under max-stale policy;
- health responses expose only `{"status":"UP"|"DOWN"}` and HTTP 200 for UP / 503 for DOWN;
- readiness DOWN removes the instance from traffic but does not itself terminate the process.

## Shutdown

On SIGTERM/SIGINT:
1. readiness becomes DOWN;
2. stop accepting new application requests;
3. allow in-flight work up to `NAPMS_SHUTDOWN_GRACE`;
4. then cancel remaining request contexts and close database/telemetry resources;
5. never claim rollback of a transaction already committed.

No background jobs are part of this MVP, so there is no independent worker-drain contract.

## Sensitive evidence rules

Never log or emit:
- bearer tokens;
- database DSN/password;
- OIDC client/private secret material if later introduced;
- full request bodies by default.

Principal subject, opaque aggregate IDs and external decision reference may be logged only in the specifically allowed event fields above.

## Implementation freedoms

Logging/metrics/tracing libraries, metric names, exporter protocol, formatter syntax and private exception/error types are free choices. They must preserve the event/metric dimensions, safe-data policy, configuration semantics, health meanings and cancellation/failure distinctions above.

## Verification obligations

Verification/Test Design must prove:
- startup rejects invalid/missing/unknown configuration;
- no runtime reload/override changes accepted configuration;
- OIDC cache/fetch failure distinguishes 401 invalid-token from 503 unverifiable-token;
- no automatic mutation retry occurs;
- request cancellation reaches database/materialization work;
- readiness/liveness semantics and graceful shutdown behavior;
- required diagnostic events are emitted without secret values.
