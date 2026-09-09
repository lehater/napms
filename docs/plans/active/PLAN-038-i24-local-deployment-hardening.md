# PLAN-038 — I24 Local Deployment and Operational Hardening

Status: `active — WP2 backup and recovery`

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
- `tools/local_start.py`;
- `docs/engineering/local-docker-runtime.md`.

Observed starting baseline:
- local Docker Compose is the supported deployment shape;
- local username/password authentication is primary;
- one nginx endpoint is published on loopback by default;
- pre-I24 Compose used PostgreSQL network trust authentication and a passwordless application DSN;
- migrations and local seed run as one-shot Compose services;
- readiness and an authenticated fresh end-to-end Docker journey already exist.

## WP1 — Local runtime security baseline

Status: `done`.

Implemented and verified:
- PostgreSQL network `trust` removed from the supported Compose path;
- fresh volumes initialize host authentication as SCRAM-SHA-256;
- application/migration/seed DSNs require `NAPMS_POSTGRES_PASSWORD`;
- `make dev-up` generates an ephemeral DB credential and rotates the persistent `napms` role before dependent services start;
- correct-password acceptance and wrong-password rejection are executable gates;
- legacy pre-I24 host-trust volumes fail closed as not hardened;
- supported `make dev-up` uses non-mutating readiness/login/session/read probes and is repeatable on preserved state;
- the stateful `dev_compose.py` journey remains a separate fresh-volume CI proof;
- Docker gate proved the fresh mutation journey followed by a restart on the same preserved volume with a distinct rotated DB credential;
- local UI login/session behavior and loopback-only public ingress remain unchanged.

Findings closed:
- P0: per-run DB credentials initially broke the preserved-volume model until role rotation was introduced;
- P1: the old stateful Docker journey was unsuitable as a normal restart probe because it creates durable Rules/Requirements. Supported startup is now non-mutating.

## WP2 — Backup, restore and recovery contract

Status: `active`.

Scope:
- define supported logical PostgreSQL backup/restore commands for the local Compose deployment;
- add deterministic operator tooling around PostgreSQL custom-format `pg_dump`/`pg_restore`;
- require an explicit destructive confirmation before replacing a local database volume;
- validate a backup before destructive restore begins;
- prove restore into a clean local database preserves durable PostgreSQL state and remains startable through the normal restart-safe helper;
- document recovery boundaries and state not captured by the database backup.

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

Status: `blocked on WP2-WP5`.

Run repository gates and local runtime recovery/hardening proofs, absorb durable outcomes into canonical engineering/architecture truth, remove this active plan and promote I25.

## Exit criteria

I24 exits when:
- supported local Compose no longer relies on PostgreSQL network trust authentication;
- secret/configuration handling has a documented local contract with no committed plaintext credentials;
- local PostgreSQL backup/restore and recovery procedure is executable and verified;
- migration/upgrade procedure is documented and proven for the supported local path;
- useful local operational diagnostics are documented/proven;
- low-risk container/dependency hardening is applied where justified;
- a measured local workload envelope exists or an explicit documented reason explains why further performance claims remain deferred;
- core, PostgreSQL persistence, harness, knowledge and Docker local-runtime gates pass on the final merge candidate.

## Blockers

No external infrastructure is required. Real TLS certificates, enterprise secret stores, HA, corporate identity and multi-node topology remain out of scope unless a concrete accepted local target requirement later selects them.

## Next

Implement WP2 logical PostgreSQL backup and explicit clean-volume restore tooling, then add a Docker round-trip proof that durable state survives backup -> volume replacement -> restore -> restart-safe startup.