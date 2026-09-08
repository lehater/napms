# PLAN-011 — I11 Dockerized Local Runtime

Status: `active`

## Goal

Make the complete local-dev NAPMS runtime start from one repository command with Docker Compose:

```text
Browser -> Web/nginx -> FastAPI -> PostgreSQL
                         ^
                         |
                    migrations
```

This is local/developer packaging, not production deployment architecture.

## Current stage

**WP1 — executable migration/runtime packaging.**

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

1. **ACTIVE — Migration runner.** Add packaged migration registry/journal, checksum validation and `napms-migrate` entrypoint with tests.
2. **Backend image.** Add minimal Python runtime Dockerfile and container health behavior.
3. **Web image.** Add multi-stage React build + nginx SPA/proxy configuration.
4. **Compose topology.** Add PostgreSQL, migrate, api and web services with health/dependency ordering and named volume.
5. **Local startup UX.** Add `.env.example`, one-command Make targets and secret-safe local credential bootstrap.
6. **Smoke proof.** Add container smoke flow: readiness -> login -> authenticated session/API call.
7. **CI Docker gate.** Build images and run Compose smoke test in GitHub Actions.
8. **Docs/current-state.** Document local run/reset/log workflows and explicit non-production boundary.
9. **Final review/gates.** Run core, PostgreSQL, Web, Docker, harness and knowledge gates; close P0/P1.

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

Implement migration runner and tests first, then build Docker images around the existing runtime.
