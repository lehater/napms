# PLAN-011 — I11 Dockerized Local Runtime

Status: `active`

## Goal

Make the complete local-dev NAPMS runtime start from one repository command with Docker Compose:

```text
Browser -> Web/nginx -> FastAPI -> PostgreSQL
                         ^
                         |
PostgreSQL -> migrations -> local demo seed
```

This is local/developer packaging, not production deployment architecture.

## Current stage

**WP9 — final architecture/security review and repository gates.**

## Inputs

- `docs/engineering/current-state.md`;
- `docs/engineering/configuration.md`;
- `docs/engineering/dependency-injection.md`;
- existing PostgreSQL module-owned SQL migrations;
- existing `napms-http` runtime entrypoint;
- existing React/Vite Web UI;
- existing health/readiness endpoints and CI gates.

## Accepted constraints

- PostgreSQL remains the only relational engine;
- one public local endpoint: Web/nginx on `localhost:8080`;
- nginx serves built React assets and proxies `/api` + `/health` to FastAPI;
- FastAPI is not directly required to be exposed to the host;
- migrations run before API admission;
- migration application is repeatable and fail-fast on applied-file checksum drift;
- database data lives in a named Docker volume;
- local-dev credentials remain hashed configuration; no plaintext password is committed or logged;
- API waits on migration completion; Web waits on API readiness;
- Compose and image build must not introduce production claims;
- no Kubernetes, Helm, TLS termination, Redis, external IdP or production secret manager in I11.

## Work packages

1. **DONE — Migration runner.** Packaged migration registry/journal, checksum validation, advisory lock and `napms-migrate` are implemented with core/PostgreSQL tests.
2. **DONE — Backend image.** Minimal non-root Python runtime image with readiness healthcheck is implemented.
3. **DONE — Web image.** Multi-stage React build + nginx SPA/same-origin proxy image is implemented.
4. **DONE — Compose topology.** PostgreSQL, migrate, local demo seed, API and Web services use health/completion ordering and a named volume.
5. **DONE — Local startup UX.** `.env.example`, Make targets and in-memory random credential bootstrap are implemented.
6. **DONE — Smoke proof.** Public readiness, login/session and seeded demo-scope checks run through nginx.
7. **DONE — CI Docker gate.** Full Compose startup plus repeated migration/seed proof runs in GitHub Actions.
8. **DONE — Docs.** README and local Docker runtime/configuration/composition contracts document operations and non-production boundaries.
9. **ACTIVE — Final review/gates.** Run core, PostgreSQL, Web, Docker, harness and knowledge gates; close P0/P1.

## Exit criteria

- fresh clone can start the full local runtime through one documented command;
- PostgreSQL becomes healthy before migrations;
- migrations are tracked and checksum-protected;
- API starts only after successful migrations;
- Web serves SPA and same-origin proxies API/health;
- persistent DB volume survives restart and can be explicitly reset;
- login/runtime smoke test passes through the public Web endpoint;
- credentials/DSN plaintext are not emitted in logs;
- existing architecture/domain semantics remain unchanged;
- all repository gates green;
- no open P0/P1 finding.

## Blockers

No current owner/product blocker.

## Next

Run final architecture/security review and all repository gates; close P0/P1 before I11 absorption.
