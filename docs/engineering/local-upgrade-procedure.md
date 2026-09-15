# Local upgrade and migration procedure

## Purpose

Define the supported forward-upgrade procedure for the local Docker Compose deployment and recovery when an upgrade cannot complete.

NAPMS does not claim arbitrary application/database downgrade compatibility.

## Preconditions

Before changing application/container versions:

1. confirm the current stack is healthy;
2. create and retain a validated logical PostgreSQL backup with `make dev-backup BACKUP=...`;
3. retain the application/source revision matching that backup when rollback may be required.

A container image rebuild is not a database backup.

## Forward upgrade

Supported order:

1. stop or replace application containers through normal Compose reconciliation;
2. prepare the local PostgreSQL credential;
3. run the ordered `napms-migrate` registry;
4. run the idempotent local seed;
5. start API;
6. wait for API readiness;
7. start Web/nginx;
8. run the restart-safe authenticated startup probe.

`make dev-up` preserves this ordering through Compose dependencies.

## Migration invariants

The migration runner:

- acquires a PostgreSQL advisory lock;
- applies the repository's single ordered migration registry;
- applies each pending migration transactionally;
- records `migration_id`, SHA-256 checksum and `applied_at` in `napms_runtime.schema_migrations`;
- skips an applied migration only when its stored checksum matches the current file;
- fails closed if an applied migration file's checksum changes.

Repeated migration against an already-current database is a no-op.

## Failure handling

If migration or startup fails:

- do not edit `schema_migrations` manually to force progress;
- do not continue with a partially incompatible application build;
- inspect logs and preserve the failing database until diagnosis is complete;
- when rollback is required, restore the validated pre-upgrade backup into a clean PostgreSQL volume and run the application revision that matches that database state.

A backup restored under the current application may receive forward migrations during startup. A true rollback uses the matching earlier application revision and database backup together.

## Downgrade boundary

NAPMS provides no reverse/down migration contract and does not guarantee an older application can run against a database already migrated by a newer version.

The supported rollback mechanism is logical backup restoration, not schema reversal.

## Verification

The Docker/local-runtime gate verifies migration replay/idempotency, preservation of durable state and normal runtime health after restore/upgrade operations.
