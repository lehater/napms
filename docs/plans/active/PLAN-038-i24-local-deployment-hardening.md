# PLAN-038 — I24 Local Deployment and Operational Hardening

Status: `active — WP3 upgrade and migration`

Date: 2026-09-10.

## Goal

Make the supported local NAPMS deployment safer to run, easier to recover and easier to operate without assuming enterprise HA, corporate identity, external secret stores or multi-node production infrastructure.

## Inputs

Canonical inputs:
- `docs/engineering/post-wave1-product-completion-roadmap.md`;
- `docs/engineering/current-state.md`;
- `docs/architecture/current-architecture.md`;
- `compose.yaml`;
- `tools/local_start.py`;
- `tools/local_postgres_backup.py`;
- `docs/engineering/local-docker-runtime.md`.

## WP1 — Local runtime security baseline

Status: `done`.

Verified outcomes:
- PostgreSQL network `trust` removed from the supported Compose path;
- fresh volumes use SCRAM host authentication;
- all application database DSNs require an explicit password;
- supported startup rotates an ephemeral database credential even on a preserved volume;
- correct-password acceptance and wrong-password rejection are executable gates;
- supported startup is non-mutating and repeatable on preserved state;
- loopback-only public ingress and local UI login/session behavior remain unchanged.

Closed findings:
- P0: per-run DB credentials initially conflicted with persistent volume reuse; role rotation fixed it;
- P1: the old stateful Docker journey could not serve as a restart probe; a separate read-only startup helper fixed it.

## WP2 — Backup, restore and recovery contract

Status: `done`.

Implemented and verified:
- PostgreSQL custom-format logical backup through `pg_dump`;
- temporary-file write plus `pg_restore --list` validation before publishing a backup artifact;
- ignored local backup artifacts under `backups/` / `*.napms.dump`;
- destructive restore requires explicit `restore-clean` semantics and `CONFIRM_RESET=yes` in the Make target;
- archive validation occurs before the existing volume is deleted;
- clean-volume restore runs through normal password preparation and restart-safe startup;
- recovery boundary explicitly excludes in-memory sessions, in-memory NEO operation records, external device/provider state, logs outside PostgreSQL and plaintext local secrets;
- Docker round-trip proved durable Access Rule count survives backup -> volume replacement -> restore -> authenticated restart, with password-authentication still enforced.

## WP3 — Upgrade and migration procedure

Status: `active`.

Scope:
- document safe pre-upgrade backup and startup/migration ordering;
- make failure/recovery behavior explicit;
- prove replay of the migration runner against a current database is a no-op and preserves the migration journal;
- treat checksum mismatch as a hard failure;
- avoid claiming arbitrary database/application downgrade support.

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

Status: `blocked on WP3-WP5`.

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

Document the supported local upgrade sequence and add a Docker proof that repeated `napms-migrate` execution preserves the existing migration-journal count and current restored state.