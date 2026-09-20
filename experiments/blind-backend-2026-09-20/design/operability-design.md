# Backend operability design

Status: ACCEPTED candidate

## Diagnostic contract

Every external request has a `correlationId` generated or accepted only from a validated format. Logs/metrics include correlationId plus safe operation/outcome fields.

Structured event classes:
- `request.completed`: route/operation, status class, duration;
- `authn.failed`, `authz.denied`: reason category, never token;
- `command.committed` / `command.conflict`: owner module, command kind, aggregate ref when safe, version;
- `permission.recorded`: requestRef, result, principal subject, decisionRef when non-sensitive;
- `policy.materialization.completed`: status COMPLETE/UNRESOLVED, evaluationAt, ruleCount, rowCount, unresolvedCount, duration;
- `dependency.failure`: dependency class, timeout/unavailable/error category;
- `unexpected.failure`: stable error class + correlationId, stack trace only in protected server logs.

Logs are diagnostic evidence, never authoritative domain history.

## Metrics

At minimum:
- request count/duration/error by operation;
- authentication failure and authorization denial count;
- stale-version/idempotency-conflict count;
- policy materialization duration, input-rule count, output-row count, unresolved count;
- database connection/query failure count;
- process start/readiness state.

No alert/SLO threshold is invented without accepted operational targets.

## Health

- `GET /health/live`: process event loop/runtime is alive; no external dependency call.
- `GET /health/ready`: required configuration loaded, database connectivity/read check succeeds, OIDC validation metadata/key set is available or valid cached material exists according to library contract.
- readiness failure prevents new traffic but does not terminate process solely to force restart.

## Configuration

Typed startup configuration:
- bind/listen settings;
- database connection;
- OIDC issuer/audience/permission-claim name/JWKS cache settings;
- timeout limits;
- log level/telemetry endpoint if used.

Invalid/missing required configuration fails startup explicitly. Secrets are read from environment/secret-file/runtime secret provider abstraction and redacted.

## Timeout/retry/cancellation

- database statement/transaction timeouts are bounded;
- OIDC metadata/JWKS refresh uses bounded timeout and library-safe retry/backoff; token validation never fails open;
- request cancellation propagates to read/materialization queries;
- application does not automatically retry committed/unknown mutations; client idempotency supports safe retry.

## Failure semantics

Operational dependency failure maps to `DEPENDENCY_UNAVAILABLE` only when the requested behavior cannot be completed. Domain rejection/authorization denial/UNRESOLVED policy are not logged as infrastructure failures.

## Observability implementation freedom

Logging/metrics/tracing libraries and backend are implementation choices. OpenTelemetry-compatible correlation is preferred but not required by product semantics; the observable contract above is required.
