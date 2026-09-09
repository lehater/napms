# Local Docker runtime

Status: `accepted local runtime through I24 PostgreSQL authentication hardening`.

Date: 2026-09-10.

## Purpose

Provide one reproducible supported local startup path for the NAPMS Web/HTTP/PostgreSQL runtime.

This is a local deployment contract. It does not claim enterprise HA/SLA topology.

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
                  | password-authenticated PostgreSQL connection
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
- explicit `NAPMS_POSTGRES_PASSWORD` required by Compose;
- new database volumes initialize host authentication as `scram-sha-256`;
- application/migration/seed services use the same password through `NAPMS_DATABASE_DSN`;
- healthcheck: `pg_isready`.

`POSTGRES_HOST_AUTH_METHOD=trust` is not part of the supported I24 local runtime.

`make dev-up` intentionally generates a fresh database password for each startup. Before migration/API services start, `tools/prepare_local_postgres.py` starts only PostgreSQL, waits for readiness and rotates the `napms` role password through the container-local database socket. This keeps the generated database password ephemeral while allowing the named PostgreSQL volume to survive `dev-down` and subsequent startups.

Important upgrade boundary: PostgreSQL host-authentication rules are stored in the database volume. A volume created by a pre-I24 runtime may still contain legacy `trust` host rules even after the Compose file changes. The supported startup path verifies both that the configured password succeeds and that a deliberately wrong password fails. If the wrong password succeeds, startup verification fails and the volume must be backed up and recreated or explicitly migrated before it can be considered hardened.

Do not delete a legacy volume containing needed data merely to satisfy this check; WP2 defines the supported backup/restore recovery path.

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

It inserts deterministic local-demo catalogue/resource facts plus Authority assignments for the configured local actor. Demo presentation metadata makes a fresh stack usable without interpreting technical identifiers.

The seed is idempotent bootstrap/demo data, not domain truth and not production seed policy.

### api

Uses the existing `napms-http` executable:
- binds `0.0.0.0:8000` inside the Compose network;
- starts only after migration and seed one-shots succeed;
- readiness is checked through `/health/ready`.

### web

Multi-stage image:
1. Node builds React/Vite;
2. nginx serves static assets on port 8080;
3. same-origin `/api/` and `/health/` are proxied to the API service;
4. SPA fallback serves `index.html`.

Default host endpoint: `http://127.0.0.1:8080`.

## Startup

Recommended:

```bash
make dev-up
```

The helper path:
1. generates a random local PostgreSQL password in process memory;
2. starts PostgreSQL only and initializes a fresh volume when needed;
3. rotates the `napms` role to the generated password through the container-local socket, including on a preserved hardened volume;
4. generates a random local UI password in process memory and derives the supported scrypt hash;
5. starts/reconciles the full stack with the generated database password;
6. checks public readiness through nginx;
7. performs authenticated product smoke checks;
8. verifies PostgreSQL accepts the configured password;
9. verifies PostgreSQL rejects a deliberately incorrect password;
10. prints the generated UI login/password once for the developer.

Neither generated plaintext credential is written to repository files by the helper.

## Operations

```bash
make dev-logs
make dev-down
make dev-reset
```

- `dev-down`: stop containers, preserve PostgreSQL volume;
- `dev-reset`: stop containers and delete the local PostgreSQL volume;
- `dev-logs`: follow service logs.

The Make targets provide non-secret placeholder interpolation for commands that only inspect or stop existing containers; these placeholders are not used to authenticate to PostgreSQL.

Changing deterministic demo seed contents may require `dev-reset` because seed insertion is intentionally idempotent rather than mutating existing demo identities.

## Raw Compose

`compose.yaml` can be used directly, but startup requires both:
- `NAPMS_POSTGRES_PASSWORD` with a non-empty local database password matching the current `napms` role password for an existing volume;
- `NAPMS_LOCAL_AUTH_PASSWORD_HASH` with a supported scrypt-v1 UI password hash.

`.env.example` documents the override names but intentionally contains no usable plaintext credentials. Keep local secret values outside version control.

The supported ergonomic path is `make dev-up`, because it safely prepares/rotates the persistent local database credential before bringing up dependent services.

## Security boundary

The current local runtime now provides password-authenticated PostgreSQL on the private Compose network and loopback-only public Web ingress by default.

I24 does not by itself claim:
- public-network TLS/certificate management;
- enterprise secret storage;
- durable/distributed Web sessions;
- multiple API replicas or HA PostgreSQL;
- enterprise reverse-proxy topology;
- external IdP integration.

Those require a concrete target-environment requirement before being introduced.
