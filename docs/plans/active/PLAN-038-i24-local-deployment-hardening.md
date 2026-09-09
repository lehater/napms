# PLAN-038 — I24 Local Deployment and Operational Hardening

Status: `active — WP1 local runtime security baseline`

Date: 2026-09-10.

## Goal

Make the supported local NAPMS deployment safer to run, easier to recover and easier to operate without assuming enterprise HA, corporate identity, external secret stores or multi-node production infrastructure.

## Inputs

Canonical inputs:
- `docs/engineering/post-wave1-product-completion-roadmap.md`;
- `docs/engineering/current-state.md`;
- `docs/architecture/current-architecture.md`;
- `compose.yaml`;
- `.env.example`;
- `tools/dev_compose.py`;
- `README.md`.

Observed baseline:
- local Docker Compose is the supported deployment shape;
- local username/password authentication is primary;
- one nginx endpoint is published on loopback by default;
- PostgreSQL currently uses `POSTGRES_HOST_AUTH_METHOD=trust` inside the Compose network;
- application database DSN currently has no password;
- migrations and local seed run as one-shot Compose services;
- readiness and authenticated end-to-end Docker smoke already exist.

## WP1 — Local runtime security baseline

Status: `active`.

Close avoidable local-runtime trust shortcuts without introducing an enterprise secret platform.

Scope:
- remove PostgreSQL `trust` authentication from the supported Compose path;
- use an explicit local database password injected through the Compose environment;
- keep generated credentials ephemeral for `make dev-up`;
- document raw `docker compose` overrides without committing plaintext secrets;
- preserve the existing local login/session flow and loopback-only public ingress.

## WP2 — Backup, restore and recovery contract

Status: `queued`.

Scope:
- define supported logical PostgreSQL backup/restore commands for the local Compose deployment;
- add deterministic operator tooling around `pg_dump`/`pg_restore` or equivalent PostgreSQL-native logical backup;
- prove restore into a clean local database preserves authoritative state;
- document recovery boundaries and what is not captured by the backup.

## WP3 — Upgrade and migration procedure

Status: `queued`.

Scope:
- document safe startup/migration ordering;
- define pre-upgrade backup and failure recovery procedure;
- prove migrations are idempotently applied by the existing migration runner;
- avoid claiming arbitrary downgrade support unless executable evidence exists.

## WP4 — Local observability and runtime diagnostics

Status: `queued`.

Scope:
- retain structured application logging/correlation;
- expose/document the smallest useful local health/readiness diagnostics;
- make Compose service state and failure diagnosis straightforward;
- add metrics only if a concrete local operator use-case justifies them.

## WP5 — Container/dependency hardening and workload envelope

Status: `queued`.

Scope:
- review container privileges, image/runtime defaults and dependency hygiene;
- harden reversible low-risk defaults where evidence supports it;
- define a modest accepted local workload envelope from executable measurements rather than invented SLA/SLO claims.

## WP6 — Verification and absorption

Status: `blocked on WP1-WP5`.

Run repository gates and local runtime recovery/hardening proofs, absorb durable outcomes into canonical engineering/architecture truth, remove this active plan and promote I25.

## Exit criteria

I24 exits when:
- supported local Compose no longer relies on PostgreSQL trust authentication;
- secret/configuration handling has a documented local contract with no committed plaintext credentials;
- local PostgreSQL backup/restore and recovery procedure is executable and verified;
- migration/upgrade procedure is documented and proven for the supported local path;
- useful local operational diagnostics are documented/proven;
- low-risk container/dependency hardening is applied where justified;
- a measured local workload envelope exists or an explicit documented reason explains why further performance claims remain deferred;
- core, harness, knowledge and Docker local-runtime gates pass on the final merge candidate.

## Blockers

No external infrastructure is required. Real TLS certificates, enterprise secret stores, HA, corporate identity and multi-node topology remain out of scope unless a concrete accepted local target requirement later selects them.

## Next

Complete WP1 by replacing Compose PostgreSQL trust authentication with explicit generated/override credentials while preserving `make dev-up`, raw Compose configurability and the existing Docker smoke.