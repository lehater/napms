# Local PostgreSQL backup and recovery

## Purpose

Define the supported logical backup and clean-volume recovery procedure for the local Docker Compose deployment.

This contract protects durable PostgreSQL state only. It is not a full machine, container-image or external-system snapshot.

## Backup

With the local stack running:

```bash
make dev-backup BACKUP=backups/napms.napms.dump
```

The command:

- runs PostgreSQL `pg_dump` in custom archive format;
- excludes ownership/ACL portability details;
- writes to a temporary host file first;
- validates the archive with `pg_restore --list`;
- atomically replaces the requested backup path only after validation succeeds.

Repository ignore rules exclude `backups/` and `*.napms.dump`.

## Restore

Restore replaces the local PostgreSQL named volume and therefore requires explicit destructive confirmation:

```bash
make dev-restore BACKUP=backups/napms.napms.dump CONFIRM_RESET=yes
```

The restore tool validates the archive before deleting the volume. After validation and confirmation it:

1. stops the local stack and removes the PostgreSQL volume;
2. creates a clean password-authenticated PostgreSQL volume;
3. restores the archive with `pg_restore`;
4. starts the normal local runtime;
5. runs configured-password and wrong-password database verification.

Normal startup migrations run after restoration. An already-current database has no pending migrations; an older compatible backup may be advanced by the current forward migration registry.

## Recovery boundary

Included:

- durable PostgreSQL schemas and rows owned by NAPMS contexts/modules;
- migration journal state in PostgreSQL;
- all durable application state present in the database.

Not included:

- generated plaintext local credentials;
- in-memory Web sessions;
- in-memory operation state;
- external device/provider state;
- container images or host files outside PostgreSQL;
- logs not persisted in PostgreSQL.

Successful restore proves recovery of NAPMS durable database truth, not ephemeral process state or external systems.

## Verification

The local Docker gate verifies backup/restore by preserving durable database state across logical dump, clean-volume replacement, restore and normal startup, then checking database authentication and expected durable-state equivalence.

The contract does not claim point-in-time recovery, physical replication or enterprise retention policy.
