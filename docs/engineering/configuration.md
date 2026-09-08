# Configuration model

Status: `accepted pre-infrastructure engineering decision`.

Date: 2026-09-08.

## Purpose

Prevent configuration from becoming implicit global state or being scattered across modules before infrastructure is introduced.

## Decision

The executable application has **one typed application configuration object assembled at the composition root**. Domain code reads no environment variables, files, command-line arguments or framework settings. Application use cases receive only the values/dependencies they actually need; they do not depend on the global configuration object unless configuration itself is their explicit concern.

Configuration sources are outer-runtime concerns. Precedence and concrete file/environment loader belong the runtime adapter, but all sources normalize into the same typed configuration model before dependency construction.

## Configuration categories

The central model will group configuration by concern, for example:
- runtime/environment identity;
- logging/observability settings;
- transport/server settings when HTTP is introduced;
- persistence connection/pool/timeout settings when persistence is introduced;
- Authority/ACC/Connectivity Decision adapter endpoints, credentials references and timeouts when real adapters are introduced;
- feature/transition switches only when an accepted requirement needs them.

A value is configurable only when it can legitimately vary by deployment/environment. Business invariants, domain identity rules and accepted policy semantics are code/model, not configuration switches.

## File and environment model

A repository-visible config file may provide non-secret defaults and document the complete supported configuration surface. Environment-specific overrides may come from environment variables or deployment secret stores. The application must not require secrets committed to the repository.

Secrets are represented as typed secret/config references and supplied from the deployment environment. They are never emitted by config dumps/logging.

## Validation

Configuration is parsed and validated once at startup before adapters/use cases are constructed. Invalid required configuration fails startup explicitly; it does not become a late runtime `None`, implicit default or partial adapter configuration.

Defaults must be explicit and safe. Security-, identity-, authority- or persistence-critical values must not receive permissive fallback defaults merely to make startup succeed.

## Access rule

Prohibited outside the configuration loader/composition boundary:
- direct `os.environ`/`getenv` reads;
- arbitrary config-file reads;
- module-level mutable settings singletons;
- framework-specific settings imported by Domain/Application;
- duplicated string keys for the same setting across adapters.

## Testability

Tests construct typed configuration values directly. Unit/core tests do not depend on developer machine environment variables or config files. Loader tests belong to the runtime/infrastructure boundary when the loader exists.

## I1 implementation consequence

No infrastructure-specific settings are invented before their adapters exist. I1 fixes the ownership and access rules now; concrete DB/HTTP/external-system fields are added only with their implementation increments. This avoids speculative configuration while preserving one central typed configuration surface.
