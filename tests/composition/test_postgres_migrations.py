import pytest

from napms.composition.postgres_migrations import (
    MIGRATIONS,
    MigrationChecksumMismatch,
    MigrationError,
    apply_postgres_migrations,
)


class Result:
    def __init__(self, row=None):
        self.row = row

    def fetchone(self):
        return self.row


class FakeConnection:
    def __init__(self):
        self.applied = {}
        self.commits = 0
        self.rollbacks = 0
        self.statements = []

    def execute(self, sql, params=None):
        self.statements.append((sql, params))
        if "SELECT checksum_sha256" in sql:
            migration_id = params[0]
            checksum = self.applied.get(migration_id)
            return Result((checksum,) if checksum is not None else None)
        if "INSERT INTO napms_runtime.schema_migrations" in sql:
            migration_id, checksum = params
            self.applied[migration_id] = checksum
        return Result()

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def test_migration_registry_has_stable_unique_ids():
    ids = tuple(item.migration_id for item in MIGRATIONS)

    assert ids == (
        "access-policy/0001",
        "access-policy/0002",
        "access-policy/0003",
        "application-catalogue/0002",
        "authority-management/0001",
        "application-catalogue/0001",
        "resource-catalogue/0001",
    )
    assert len(ids) == len(set(ids))


def test_migration_runner_applies_once_then_is_idempotent():
    connection = FakeConnection()
    migration = MIGRATIONS[0]

    first = apply_postgres_migrations(connection, (migration,))
    second = apply_postgres_migrations(connection, (migration,))

    assert first == (migration.migration_id,)
    assert second == ()
    assert connection.applied[migration.migration_id] == migration.checksum()


def test_migration_runner_fails_on_applied_checksum_drift():
    connection = FakeConnection()
    migration = MIGRATIONS[0]
    connection.applied[migration.migration_id] = "different-checksum"

    with pytest.raises(MigrationChecksumMismatch):
        apply_postgres_migrations(connection, (migration,))

    assert connection.rollbacks == 1


def test_duplicate_migration_ids_fail_before_database_work():
    connection = FakeConnection()
    migration = MIGRATIONS[0]

    with pytest.raises(MigrationError):
        apply_postgres_migrations(connection, (migration, migration))

    assert connection.statements == []
