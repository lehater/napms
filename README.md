# NAPMS

**Network Access Policy Management System**

Authoritative greenfield NAPMS product repository.

## Current implementation state

NAPMS includes the current local product chain through Network Environment Operations plus the optional external-integration seam absorbed in I23. Canonical capability status lives in `docs/engineering/current-state.md`; roadmap sequencing lives in `docs/engineering/post-wave1-product-completion-roadmap.md`.

## Local Docker start

Prerequisites: Docker Engine/Desktop with Docker Compose v2 and Python 3.

```bash
make dev-up
```

The command generates ephemeral local PostgreSQL and UI credentials in memory, prepares/rotates the local database role password, builds and starts PostgreSQL, tracked migrations, local demo seed, FastAPI and Web/nginx, runs only restart-safe authenticated readiness/session/read probes, verifies that PostgreSQL rejects an incorrect password, then prints the local URL and generated UI login credentials.

Open the printed URL (default `http://127.0.0.1:8080`).

Useful commands:

```bash
make dev-logs
make dev-down
make dev-reset
```

`dev-down` preserves the database volume. `dev-reset` deletes local database state. Re-running `make dev-up` against preserved state does not create or mutate application domain objects as part of its startup probe.

A PostgreSQL volume created by the older pre-I24 host-`trust` configuration may fail the new authentication verification even though the application can connect. Back up needed data before recreating or explicitly migrating such a volume.

## Local backup and recovery

Create a validated PostgreSQL custom-format logical backup:

```bash
make dev-backup BACKUP=backups/napms.napms.dump
```

Restore into a clean replacement PostgreSQL volume:

```bash
make dev-restore BACKUP=backups/napms.napms.dump CONFIRM_RESET=yes
```

Restore is deliberately destructive and refuses to replace the volume without explicit confirmation. The archive is validated before volume deletion. See `docs/engineering/local-backup-recovery.md` for the exact recovery boundary and exclusions.

For raw `docker compose up`, provide `NAPMS_POSTGRES_PASSWORD` and `NAPMS_LOCAL_AUTH_PASSWORD_HASH` outside version control. `.env.example` lists the supported overrides but intentionally contains no usable credentials.

See `docs/engineering/local-docker-runtime.md` for the topology, credential boundary and explicit non-enterprise scope.

## Native development

```bash
python -m pip install -e ".[dev,postgres,runtime]"
make test
```

PostgreSQL integration tests use `NAPMS_TEST_POSTGRES_DSN` and `make postgres-test`.

Web build:

```bash
cd web
npm install
npm run build
```

## Repository layout

```text
src/napms/                 product code
web/                       React Web UI
tests/                     executable specifications and integration tests
docs/domain/               living DDD model
docs/requirements/         accepted product requirements
docs/architecture/         architecture contracts
docs/engineering/          engineering/runtime policies
docs/plans/active/         current execution resume state / active plan when selected
```

See `AGENTS.md` and `docs/README.md` before changing domain or architecture semantics.
