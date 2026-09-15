# Configuration model

## Purpose

Keep deployment/runtime configuration explicit, typed and outside Domain semantics.

## Configuration boundary

Each executable process assembles one typed configuration object at its composition root. Domain code reads no environment variables, files, command-line arguments or framework settings. Application use cases receive only the values and dependencies they actually need.

Configuration sources are outer-runtime concerns and normalize into typed configuration before dependency construction.

## Local runtime surface

The supported local runtime uses PostgreSQL and local authentication. Its configuration includes the values required to establish:

- environment identity (`local-dev` for the supported Compose runtime);
- PostgreSQL DSN/credentials;
- local authentication login, actor identity and supported password hash;
- HTTP bind host/port;
- Web/nginx host port.

PostgreSQL configuration is password-authenticated. Required credentials are generated/supplied by the local runtime tooling and are not committed as plaintext repository configuration.

The authenticated actor identity remains separate from Authority Management admission. Authentication configuration never embeds business authority.

## Secrets

Connection strings, passwords, tokens and credential material are secret-bearing configuration.

- secret values are not emitted by configuration object representations or normal logs;
- plaintext generated local credentials are not written to repository files;
- deployment secret stores/environment injection remain outer-runtime mechanisms;
- non-secret defaults may be repository-visible when they are part of the supported runtime contract.

## Validation

Configuration is parsed and validated once at startup before adapters or use cases are constructed.

Missing or invalid required values fail startup explicitly. Security-, identity-, authority- and persistence-critical values do not receive permissive fallback defaults merely to make startup succeed.

A value is configurable only when it can legitimately vary by deployment/environment. Business invariants, semantic identity rules and accepted policy meaning are model/code, not configuration switches.

## Access rule

Outside the configuration loader/composition boundary, prohibit:

- direct `os.environ` / `getenv` reads;
- arbitrary configuration-file reads;
- module-level mutable settings singletons;
- framework-specific settings imported by Domain/Application;
- duplicated string keys representing the same setting across modules.

Adapters receive typed configuration values or focused configuration objects from composition.

## Testability

Tests construct configuration explicitly. Configuration tests cover parsing, validation, secret redaction and startup failure for missing/invalid required values. Domain/Application tests do not depend on process environment state.
