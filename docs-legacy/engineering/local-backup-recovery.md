# Local PostgreSQL backup and recovery

Status: `accepted I24 local recovery contract`.

Date: 2026-09-10.

## Purpose

Define the supported logical backup and clean-volume recovery procedure for the local Docker Compose deployment.

This contract protects durable PostgreSQL state only. It is not a full machine, container-image or external-provider snapshot.

## Backup

With the local stack running:

```bash
make dev-backup BACKUP=backups/napms.napms.dump
```

The command:
- runs PostgreSQL `pg_dump` in custom archive format;
- excludes ownership/ACL portability details;
- writes to a temporary host file first;
- validates the resulting archive with PostgreSQL `pg_restore --list`;
- atomically replaces the requested backup path only after validation succeeds.

The default repository ignore rules exclude `backups/` and `*.napms.dump` so local backup archives are not accidentally committed.

## Restore

Restore replaces the entire local PostgreSQL named volume. It is therefore explicit and destructive:

```bash
make dev-restore BACKUP=backups/napms.napms.dump CONFIRM_RESET=yes
```

The restore tool validates the archive before volume deletion. Without the explicit confirmation the operation fails without changing the volume.

After validation and confirmation it:
1. stops the local stack and removes the PostgreSQL volume;
2. creates a fresh password-authenticated PostgreSQL volume;
3. restores the custom-format archive with `pg_restore`;
4. starts the normal restart-safe local runtime;
5. runs the PostgreSQL configured-password/wrong-password verification.

The restore path intentionally uses normal migrations/startup after archive restoration. An already-current restored database should therefore report no pending migrations, while a future application version may apply forward migrations according to the normal migration contract.

## Recovery boundary

Included:
- all durable PostgreSQL schemas and rows owned by NAPMS contexts;
- migration journal state stored in PostgreSQL;
- durable catalogue/resource/authority/policy/decision/evidence/placement state present in the database.

Not included:
- generated local UI or database plaintext credentials;
- in-memory Web sessions;
- the current in-memory Network Environment Operations operation repository;
- external device/provider state;
- container images, Docker configuration or host files outside PostgreSQL;
- logs that are not persisted in PostgreSQL.

A successful PostgreSQL restore therefore proves recovery of NAPMS durable database truth, not recovery of ephemeral process state or external systems.

## Verification evidence

The Docker local-runtime gate executes an end-to-end recovery proof:
1. create durable Access Rule state through the fresh product journey;
2. record the durable Access Rule count;
3. create and validate a logical backup;
4. replace the PostgreSQL volume;
5. restore the archive;
6. start NAPMS through the restart-safe startup helper;
7. confirm the durable Access Rule count matches the pre-backup value;
8. confirm password-authenticated PostgreSQL remains enforced.

This is the accepted first local recovery proof. It does not claim point-in-time recovery, physical replication or enterprise backup retention policy.
