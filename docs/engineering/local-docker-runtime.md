# Local Docker runtime

Status: `accepted through I12 local-demo presentation refinement`.

Date: 2026-09-09.

## Purpose

Provide one reproducible local/developer startup path for the already-accepted NAPMS Web/HTTP/PostgreSQL runtime.

This is not a production deployment architecture.

## Topology

```text
Browser
  |
  | http://127.0.0.1:8080
  v
Web / nginx
  |-- static React SPA
  |-- /api/* ----+
  |-- /health/*  |
                  v
              FastAPI
                  |
                  v
              PostgreSQL

PostgreSQL healthy
  -> migrate (one-shot)
  -> local demo seed (one-shot)
  -> API
  -> Web
```

Only Web/nginx is published to the host by default. PostgreSQL and FastAPI remain on the Compose network.

## Services

### postgres

- PostgreSQL 16 Alpine;
- named volume `napms-postgres`;
- no host database port;
- local Compose network uses PostgreSQL trust authentication because the DB is not host-published and I11 is explicitly local-dev only;
- healthcheck: `pg_isready`.

This trust setting must not be promoted to a production deployment.

### migrate

Uses the backend image and runs `napms-migrate`.

The migration runner:
- owns one global ordered registry over module-owned migration files;
- records `migration_id + SHA-256 checksum + applied_at` in `napms_runtime.schema_migrations`;
- uses a PostgreSQL advisory lock so only one runner applies the registry at a time;
- applies each migration transactionally before journaling it;
- skips already-applied matching migrations;
- fails if an applied migration file checksum changes.

Existing module schema ownership is unchanged.

### seed

Uses the backend image and runs `napms-seed-local`.

It inserts deterministic local-demo catalogue/resource facts plus Authority assignments for the configured local actor. I12 gives the demo Source, Destination and DCS human-readable display labels so a fresh stack is usable without interpreting UUIDs.

Current Authority assignments:
- `ProposeConnectivity`;
- `ReadAccessRule`;
- `SetRuleOperationalState`;
- `SetRuleEffectiveWindow`;
- `ReadEffectiveDesiredPolicy`.

It is idempotent bootstrap/demo data, not domain truth and not production seed policy.

### api

Uses the existing `napms-http` executable:
- binds `0.0.0.0:8000` inside the Compose network;
- starts only after migration and seed one-shots succeed;
- readiness is checked through `/health/ready`.

### web

Multi-stage image:
1. Node 22 builds React/Vite;
2. nginx serves static assets on port 8080;
3. same-origin `/api/` and `/health/` are proxied to the API service;
4. SPA fallback serves `index.html`.

Default host endpoint: `http://127.0.0.1:8080`.

## Startup

Recommended:

```bash
make dev-up
```

The helper:
1. generates a random local UI password in process memory;
2. derives the supported scrypt hash;
3. passes only the hash to Compose;
4. builds/starts the stack;
5. checks public readiness through nginx;
6. performs login/session/demo-scope smoke checks;
7. prints the generated login/password once for the developer.

The plaintext password is not written to repository files or Compose configuration.

## Operations

```bash
make dev-logs
make dev-down
make dev-reset
```

- `dev-down`: stop containers, preserve PostgreSQL volume;
- `dev-reset`: stop containers and delete the local PostgreSQL volume;
- `dev-logs`: follow service logs.

Changing deterministic demo seed contents may require `dev-reset` because seed insertion is intentionally idempotent rather than mutating existing demo identities.

## Raw Compose

`compose.yaml` can be used directly, but the caller must supply a valid `NAPMS_LOCAL_AUTH_PASSWORD_HASH`. `.env.example` documents the supported override names.

The supported ergonomic path is `make dev-up`.

## Security boundary

I11 does not claim:
- TLS;
- hardened PostgreSQL authentication;
- production secrets;
- durable/distributed Web sessions;
- multiple API replicas;
- production reverse-proxy topology;
- external IdP integration.

Those require a separate production deployment decision.
