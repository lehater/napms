# NAPMS

**Network Access Policy Management System**

Authoritative greenfield NAPMS product repository.

## Current implementation state

NAPMS is implemented through I12:
- Access Policy, Authority Management, Application Communication Catalogue and Resource Catalogue;
- PostgreSQL persistence;
- Web/HTTP runtime;
- Access Rule operational workspace;
- EffectiveWindow management;
- Effective Desired Policy and normalized policy views;
- human-readable catalogue labels and authorized interaction search across operator workflows.

I11 adds and proves the reproducible local Docker runtime. I12 makes the existing workflows label-first while retaining stable technical IDs.

## Local Docker start

Prerequisites: Docker Engine/Desktop with Docker Compose v2 and Python 3.

```bash
make dev-up
```

The command builds and starts PostgreSQL, tracked migrations, local demo seed, FastAPI and Web/nginx, runs an authenticated smoke check, then prints the local URL and generated login credentials.

Open the printed URL (default `http://127.0.0.1:8080`).

Useful commands:

```bash
make dev-logs
make dev-down
make dev-reset
```

`dev-down` preserves the database volume. `dev-reset` deletes local database state.

See `docs/engineering/local-docker-runtime.md` for the topology and explicit non-production boundary.

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
docs/plans/active/         current execution plan
```

See `AGENTS.md` and `docs/README.md` before changing domain or architecture semantics.
