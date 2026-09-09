# Local upgrade and migration procedure

Status: `accepted I24 local upgrade contract`.

Date: 2026-09-10.

## Purpose

Define the supported forward-upgrade procedure for the local Docker Compose deployment and the recovery path when an upgrade cannot complete.

This procedure does not claim arbitrary application/database downgrade compatibility.

## Preconditions

Before changing application/container versions:
1. confirm the current stack is healthy;
2. create and retain a validated logical PostgreSQL backup with `make dev-backup BACKUP=...`;
3. retain the application/source revision that produced the backup so rollback can restore both database and matching application code if required.

Do not treat a container image rebuild as a database backup.

## Forward upgrade

Supported order:
1. stop or replace application containers through the normal Compose reconciliation path;
2. prepare/rotate the local PostgreSQL credential;
3. run the ordered `napms-migrate` registry;
4. run the idempotent local seed;
5. start API;
6. wait for API readiness;
7. start Web/nginx;
8. run the restart-safe authenticated startup probe.

`make dev-up` preserves this ordering through the existing Compose dependencies.

## Migration invariants

The migration runner:
- acquires a PostgreSQL advisory lock;
- applies the repository's single ordered migration registry;
- applies each pending migration transactionally;
- records `migration_id`, SHA-256 checksum and `applied_at` in `napms_runtime.schema_migrations`;
- skips an already-applied migration only when the stored checksum matches the current migration file;
- fails closed if an applied migration file's checksum changes.

Running `napms-migrate` repeatedly against an already-current database is therefore expected to be a no-op.

## Failure handling

If migration or startup fails:
- do not manually edit `schema_migrations` to force progress;
- do not continue with a partially incompatible application build;
- inspect migration/application logs and preserve the failing database until diagnosis is complete;
- when recovery requires rollback, restore the validated pre-upgrade backup into a clean PostgreSQL volume and run the matching pre-upgrade application revision.

A backup restored under a newer application revision may legitimately receive forward migrations during startup. For a true rollback, use the application revision that matches the pre-upgrade database state.

## Downgrade boundary

NAPMS does not currently provide reverse/down migrations or guarantee that an older application can run against a database already migrated by a newer version.

The supported rollback mechanism is backup restoration, not schema reversal.

## Verification evidence

The Docker local-runtime gate proves the current first-slice upgrade invariant after backup/restore:
1. record migration-journal row count;
2. run `napms-migrate` against the current restored database;
3. run it again;
4. confirm the journal row count is unchanged;
5. confirm durable Access Rule state remains unchanged;
6. confirm the normal runtime remains healthy.

This proves current migration replay/idempotency, not compatibility with unknown future migration shapes.
