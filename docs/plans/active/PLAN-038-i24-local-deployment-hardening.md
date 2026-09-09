# PLAN-038 — I24 Local Deployment and Operational Hardening

Status: `active — final verification`

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

Verified outcomes:
- PostgreSQL custom-format logical backup through `pg_dump`;
- temporary-file write plus `pg_restore --list` validation before publishing a backup artifact;
- ignored local backup artifacts under `backups/` / `*.napms.dump`;
- destructive restore requires explicit `restore-clean` semantics and `CONFIRM_RESET=yes` in the Make target;
- archive validation occurs before the existing volume is deleted;
- clean-volume restore runs through normal password preparation and restart-safe startup;
- recovery boundary excludes in-memory sessions/NEO operation records, external provider state, non-PostgreSQL logs and plaintext local secrets;
- Docker round-trip proved durable Access Rule count survives backup -> volume replacement -> restore -> authenticated restart, with password authentication still enforced.

## WP3 — Upgrade and migration procedure

Status: `done`.

Verified outcomes:
- supported local forward-upgrade order and pre-upgrade backup requirement documented;
- failed upgrade recovery uses a validated pre-upgrade backup and matching application revision rather than arbitrary reverse migrations;
- migration checksum mismatch remains fail-closed;
- Docker gate runs `napms-migrate` twice against current restored state and proves migration-journal count and durable Rule count remain unchanged;
- arbitrary application/database downgrade compatibility is explicitly not claimed.

## WP4 — Local observability and runtime diagnostics

Status: `implemented; final verification pending`.

Implemented:
- existing structured JSON logging/correlation retained as the runtime diagnostic source;
- existing `/health/live` and PostgreSQL-backed `/health/ready` retained;
- `make dev-status` prints Compose state and requires public live/ready plus a real PostgreSQL `SELECT 1`;
- `make dev-logs` remains the follow-up diagnostic path;
- no metrics backend is added because no concrete local operator use-case currently requires one.

## WP5 — Container/dependency hardening and workload boundary

Status: `implemented/reviewed; final verification pending`.

Implemented/reviewed:
- backend runtime remains dedicated non-root uid 10001;
- backend-derived and Web services use `init: true` and `no-new-privileges:true`;
- PostgreSQL privilege/entrypoint model is left on the official image rather than speculatively overridden;
- public ingress remains loopback-only and PostgreSQL/API remain un-published;
- Web dependency lockfile absence is recorded as P2 reproducibility debt rather than hidden or hand-authored;
- no performance/SLA envelope is invented because no accepted workload/user-count/dataset/latency target exists; capacity claims remain explicitly deferred until such a target is accepted.

## WP6 — Verification and absorption

Status: `active`.

Run core, PostgreSQL persistence, harness, knowledge and Docker local-runtime gates on the complete hardening branch. If green, update canonical current-state/roadmap, remove this active plan and promote I25 Product Completion, Operator UX and Acceptance.

## Exit criteria

I24 exits when:
- supported local Compose no longer relies on PostgreSQL network trust authentication;
- secret/configuration handling has a documented local contract with no committed plaintext credentials;
- local PostgreSQL backup/restore and recovery procedure is executable and verified;
- migration/upgrade procedure is documented and proven for the supported local path;
- useful local operational diagnostics are documented/proven;
- low-risk container/dependency hardening is applied where justified;
- performance/capacity claims are either measured against an accepted target or explicitly deferred because no target exists;
- core, PostgreSQL persistence, harness, knowledge and Docker local-runtime gates pass on the final merge candidate.

## Blockers

No product/domain blocker remains. Final closure is blocked only on complete-branch verification and absorption. Enterprise TLS/secret stores/HA/corporate identity/multi-node topology remain out of scope for the selected local target.

## Next

Run final complete-branch gates. If green, absorb I24 into canonical engineering/architecture/roadmap state, remove PLAN-038 from active execution and promote I25.