# Backend operability design

Status: ACCEPTED after Coding-Agent Challenge 07 repair

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
- `runtime.startup.failed`: serve configuration/schema/dependency category without secret values;
- `runtime.migration.failed`: migration id/category (`LOCK|CHECKSUM|ORDER|DDL|DATABASE`) without secret values;
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

The binary process mode is selected by one positional action: `migrate` or `serve`. It is not a configuration override.

Serve-mode required environment keys:

| Key | Meaning / validation | Secret |
| --- | --- | --- |
| `NAPMS_LISTEN_ADDR` | non-empty HTTP listen address | no |
| `NAPMS_DATABASE_DSN` | PostgreSQL connection DSN | yes |
| `NAPMS_OIDC_ISSUER` | absolute HTTPS issuer URL except explicitly local test issuer | no |
| `NAPMS_OIDC_AUDIENCE` | non-empty required audience | no |
| `NAPMS_OIDC_PERMISSION_CLAIM` | non-empty top-level claim name containing effective permission strings | no |
| `NAPMS_OIDC_ALLOWED_ALGS` | non-empty unique comma-separated subset of RS256,RS384,RS512,PS256,PS384,PS512,ES256,ES384,ES512,EdDSA; HS*/none/unknown forbidden | no |
| `NAPMS_OIDC_CLOCK_SKEW` | duration >= 0 applied to exp/nbf validation only | no |
| `NAPMS_DB_STATEMENT_TIMEOUT` | duration > 0 | no |
| `NAPMS_HTTP_REQUEST_TIMEOUT` | duration > 0, bounds one external request including materialization | no |
| `NAPMS_HTTP_MAX_REQUEST_BODY_BYTES` | integer > 0; hard transport-safety limit for JSON request bodies; no hidden default | no |
| `NAPMS_OIDC_HTTP_TIMEOUT` | duration > 0 for metadata/JWKS HTTP attempt | no |
| `NAPMS_OIDC_FETCH_MAX_ATTEMPTS` | integer >= 1 | no |
| `NAPMS_OIDC_FETCH_BACKOFF` | duration >= 0 between OIDC fetch attempts | no |
| `NAPMS_JWKS_MAX_STALE` | duration >= 0 during which already-cached signing keys may remain usable if refresh fails | no |
| `NAPMS_SHUTDOWN_GRACE` | duration > 0 for in-flight graceful shutdown | no |

Optional:
- `NAPMS_LOG_LEVEL`: `DEBUG|INFO|WARN|ERROR`, default `INFO`;
- telemetry exporter/sink configuration may be added by the selected observability library, but must not change application semantics or leak secrets.

In `migrate` mode, only `NAPMS_DATABASE_DSN` and `NAPMS_DB_STATEMENT_TIMEOUT` are required. Other known NAPMS_* keys may be present and, if present, are validated but not used by migration logic. Unknown NAPMS_* keys are errors in both modes.

In `serve` mode all serve-required keys above are required.

No mode interprets command-line arguments as configuration values.

Invalid/missing required configuration for the selected mode:
1. emits the appropriate safe startup/migration failure event;
2. exits non-zero;
3. serve never starts the HTTP listener; migrate never starts a listener at all.

Serve startup sequence is normative:
1. validate serve configuration;
2. connect PostgreSQL and verify applied migration ids/checksums exactly match the binary;
3. initialize OIDC validation material;
4. only then create/open the HTTP listener.

Migrate sequence is normative:
1. validate migrate-profile configuration;
2. connect PostgreSQL;
3. acquire the exclusive NAPMS migration advisory lock;
4. validate checksums/order and apply pending migrations transactionally;
5. exit; no application listener/services are constructed.

The application never logs the value of a key classified secret.

## OIDC key/cache/dependency semantics

Configuration (issuer/audience/permission-claim/allowed-algs/clock-skew) is immutable for process lifetime.

### Initial acquisition

After serve-mode configuration + exact database schema verification and before opening the HTTP listener:
1. fetch/validate OIDC metadata and JWKS using the bounded retry contract;
2. require at least one usable public verification key compatible with configured allowed algorithms;
3. if initial usable validation material cannot be established, emit safe `runtime.startup.failed` dependency evidence and exit non-zero;
4. only after successful initial acquisition may the listener start/readiness become UP.

### Runtime refresh/cache

- every metadata/JWKS HTTP attempt is bounded by `NAPMS_OIDC_HTTP_TIMEOUT`;
- one refresh sequence uses at most `NAPMS_OIDC_FETCH_MAX_ATTEMPTS` with configured backoff;
- concurrent refresh triggers share one in-flight single-flight refresh; they do not fan out independent fetch storms;
- bearer JWT requires non-empty string `kid`; missing/wrong-type kid -> 401 with no refresh;
- unknown kid may trigger one bounded refresh sequence;
- if refresh succeeds and kid is still absent from usable JWKS -> 401;
- if refresh cannot complete and token validity therefore cannot be established -> 503;
- readiness, when no currently usable key material exists, may trigger one bounded single-flight refresh and reports UP only if usable material is established;
- protected token validation may also trigger that refresh path when required;
- cached signing keys remain usable after refresh failure only while cache age <= `NAPMS_JWKS_MAX_STALE`;
- refresh failure does not force readiness DOWN while still-usable cached keys exist;
- once no usable/non-stale validation material exists, readiness is DOWN;
- cryptographically invalid token against established valid key material -> 401;
- inability to establish token validity because required key material is unavailable/staler than allowed -> 503, not false 401/fail-open.

No product/domain background worker is required; refresh is triggered by initialization, readiness and protected validation paths.

## Database failure semantics

- every database statement/transaction and row-lock/idempotency-key wait is bounded by the configured statement timeout and request context;
- current-Need validation lock waits and competing idempotency-key waits that cannot resolve before deadline map to DEPENDENCY_UNAVAILABLE rather than fabricated conflict/success;
- application commands do not retry database mutations automatically;
- unknown commit outcome is surfaced as dependency/internal failure, never confirmed success;
- the client may retry only through accepted Idempotency-Key semantics;
- read-only query retry is not required in the application; callers can retry a failed request.

## Request timeout and cancellation

- one external request is bounded by `NAPMS_HTTP_REQUEST_TIMEOUT`;
- request JSON decoding is bounded by `NAPMS_HTTP_MAX_REQUEST_BODY_BYTES`; oversized body returns 413 PAYLOAD_TOO_LARGE before semantic command execution;
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

No product/domain background jobs are part of this MVP, so there is no independent worker-drain contract. OIDC refresh is request/readiness-triggered, not a product worker.

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
