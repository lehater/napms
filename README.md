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

The command generates ephemeral local PostgreSQL and UI credentials in memory, builds and starts PostgreSQL, tracked migrations, local demo seed, FastAPI and Web/nginx, runs an authenticated product smoke check, verifies that PostgreSQL requires the configured password, then prints the local URL and generated UI login credentials.

Open the printed URL (default `http://127.0.0.1:8080`).

Useful commands:

```bash
make dev-logs
make dev-down
make dev-reset
```

`dev-down` preserves the database volume. `dev-reset` deletes local database state.

A PostgreSQL volume created by the older pre-I24 `trust` configuration may fail the new authentication verification even though the application can connect. Do not destroy needed data to fix that condition; first follow the local backup/restore procedure once available in I24 WP2, then recreate or explicitly migrate the volume.

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
