# Local Docker runtime

## Purpose

Provide one reproducible supported local startup path for the NAPMS Web/HTTP/PostgreSQL runtime. This is a local deployment contract and does not claim HA/SLA production topology.

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

## PostgreSQL

The local database uses PostgreSQL 16 Alpine with named volume `napms-postgres`, no host database port and password-authenticated host connections.

The supported startup path requires the configured password to succeed and a deliberately incorrect password to fail. If that verification fails, the runtime is not considered healthy; preserve needed data through the supported backup procedure before recreating or repairing the volume.

## Migration

The `migrate` service runs `napms-migrate` before the API starts.

The migration runner:

- owns one globally ordered registry over module-owned migration files;
- records `migration_id + SHA-256 checksum + applied_at` in `napms_runtime.schema_migrations`;
- uses a PostgreSQL advisory lock;
- applies each pending migration transactionally before journaling it;
- skips an already-applied migration only when the checksum matches;
- fails if an applied migration file's checksum changes.

Schema ownership remains with the owning modules/contexts.

## Local seed

The `seed` service runs `napms-seed-local` after migration. It creates deterministic local-demo data and Authority assignments for the configured local actor.

Seed data is idempotent local bootstrap/demo state, not production policy or external authoritative truth.

## API and Web

The API runs `napms-http`, binds inside the Compose network and exposes liveness/readiness through nginx.

The Web image builds the React/Vite application and serves it through nginx. Same-origin `/api/` and `/health/` traffic is proxied to the API; SPA fallback serves `index.html`.

Default host endpoint:

```text
http://127.0.0.1:8080
```

## Supported startup

```bash
make dev-up
```

The startup helper:

1. generates local PostgreSQL and UI credentials in process memory;
2. starts/prepares PostgreSQL;
3. applies migrations;
4. applies idempotent local seed data;
5. starts API and Web;
6. waits for public readiness;
7. performs non-mutating authenticated startup probes;
8. verifies correct PostgreSQL credentials succeed and incorrect credentials fail;
9. prints the generated local UI credential once for the developer.

Generated plaintext credentials are not written to repository files.

The normal startup path is restart-safe against a preserved local database and does not depend on recreating product mutations to prove health.

## Docker gate journey

The Docker gate may run a separate fresh-state end-to-end journey to prove product behavior against a clean volume. That mutation journey is test evidence; normal `make dev-up` remains the supported restart-safe operational path.

## Operations

```bash
make dev-status
make dev-logs
make dev-down
make dev-reset
```

- `dev-status` verifies service/readiness/database health;
- `dev-logs` follows service logs;
- `dev-down` stops containers while preserving PostgreSQL volume;
- `dev-reset` stops containers and removes the local PostgreSQL volume.

Use `docs/engineering/local-backup-recovery.md` before destructive volume replacement when local durable data must be preserved.
