# Configuration model

Status: `accepted and exercised through I7 local-dev PostgreSQL composition`.

Date: 2026-09-08.

## Purpose

Prevent configuration from becoming implicit global state or being scattered across modules.

## Decision

The executable application has **one typed application configuration object assembled at the composition root**. Domain code reads no environment variables, files, command-line arguments or framework settings. Application use cases receive only the values/dependencies they actually need.

Configuration sources are outer-runtime concerns. All sources normalize into the same typed configuration model before dependency construction.

## Current I7 configuration surface

The admitted local-dev greenfield composition uses:

- `NAPMS_ENVIRONMENT=local-dev`;
- `NAPMS_DATABASE_DSN=<postgres/postgresql DSN>`.

Rules:
- PostgreSQL is the only admitted relational engine;
- DSN must contain a PostgreSQL scheme, host and database name;
- missing/invalid required values fail startup;
- the DSN is treated as secret-bearing configuration and is excluded from normal object representation;
- no Legacy/MSSQL configuration exists;
- no HTTP/server, public serializer or external-service credential fields are invented before their adapters are selected.

The I7 composition is deliberately limited to `local-dev`; using the same configuration object with an unaccepted environment identity fails validation rather than silently implying production readiness.

## Future configuration categories

Add only when the corresponding runtime adapter is admitted:
- logging/observability settings;
- transport/server settings;
- persistence pool/timeout settings if the runtime needs them;
- external-provider endpoint/credential references;
- feature switches only when an accepted requirement needs them.

A value is configurable only when it can legitimately vary by deployment/environment. Business invariants, identity rules and accepted policy semantics are code/model, not configuration switches.

## File and environment model

A repository-visible config file may provide non-secret defaults and document the supported surface. Environment-specific overrides may come from environment variables or deployment secret stores.

Secrets are supplied by the deployment environment and are never emitted by config dumps/logging.

## Validation

Configuration is parsed and validated once at startup before adapters/use cases are constructed. Invalid required configuration fails startup explicitly; it does not become a late runtime `None`, implicit default or partial adapter configuration.

Security-, identity-, authority- or persistence-critical values must not receive permissive fallback defaults merely to make startup succeed.

## Access rule

Prohibited outside the configuration loader/composition boundary:
- direct `os.environ`/`getenv` reads;
- arbitrary config-file reads;
- module-level mutable settings singletons;
- framework-specific settings imported by Domain/Application;
- duplicated string keys for the same setting across adapters.

## Testability

Tests construct typed configuration values directly. Core tests do not depend on developer-machine environment variables or config files. Loader/composition tests verify required-value failure and secret-safe representation.
