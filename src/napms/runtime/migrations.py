import hashlib
from dataclasses import dataclass
from importlib.resources import files
from typing import Iterable

import psycopg

from napms.composition.config import load_application_config


_MIGRATION_LOCK_ID = 711_011_001


class MigrationError(RuntimeError):
    """Base migration runner failure."""


class MigrationChecksumMismatch(MigrationError):
    """An already-applied migration file no longer matches its recorded checksum."""


@dataclass(frozen=True, slots=True)
class Migration:
    migration_id: str
    package: str
    resource_path: str

    def read_sql(self) -> str:
        return (
            files(self.package)
            .joinpath(self.resource_path)
            .read_text(encoding="utf-8")
        )

    def checksum(self) -> str:
        return hashlib.sha256(self.read_sql().encode("utf-8")).hexdigest()


MIGRATIONS: tuple[Migration, ...] = (
    Migration(
        "access-policy/0001",
        "napms.access_policy.adapters.postgres",
        "migrations/0001_access_rules.sql",
    ),
    Migration(
        "access-policy/0002",
        "napms.access_policy.adapters.postgres",
        "migrations/0002_rule_state_transitions.sql",
    ),
    Migration(
        "access-policy/0003",
        "napms.access_policy.adapters.postgres",
        "migrations/0003_effective_windows.sql",
    ),
    Migration(
        "authority-management/0001",
        "napms.authority_management.adapters.postgres",
        "migrations/0001_authority_assignments.sql",
    ),
    Migration(
        "application-catalogue/0001",
        "napms.application_catalogue.adapters.postgres",
        "migrations/0001_application_catalogue.sql",
    ),
    Migration(
        "resource-catalogue/0001",
        "napms.resource_catalogue.adapters.postgres",
        "migrations/0001_resource_catalogue.sql",
    ),
)


def _ensure_unique_ids(migrations: Iterable[Migration]) -> tuple[Migration, ...]:
    values = tuple(migrations)
    ids = tuple(item.migration_id for item in values)
    if len(ids) != len(set(ids)):
        raise MigrationError("migration ids must be unique")
    return values


def apply_migrations(connection, migrations: Iterable[Migration] = MIGRATIONS) -> tuple[str, ...]:
    ordered = _ensure_unique_ids(migrations)
    connection.execute("SELECT pg_advisory_lock(%s)", (_MIGRATION_LOCK_ID,))
    try:
        connection.execute("CREATE SCHEMA IF NOT EXISTS napms_runtime")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS napms_runtime.schema_migrations (
                migration_id text PRIMARY KEY,
                checksum_sha256 text NOT NULL,
                applied_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
        connection.commit()

        applied: list[str] = []
        for migration in ordered:
            checksum = migration.checksum()
            existing = connection.execute(
                """
                SELECT checksum_sha256
                FROM napms_runtime.schema_migrations
                WHERE migration_id = %s
                """,
                (migration.migration_id,),
            ).fetchone()

            if existing is not None:
                if existing[0] != checksum:
                    raise MigrationChecksumMismatch(
                        f"checksum mismatch for applied migration {migration.migration_id}"
                    )
                continue

            connection.execute(migration.read_sql())
            connection.execute(
                """
                INSERT INTO napms_runtime.schema_migrations (
                    migration_id,
                    checksum_sha256
                )
                VALUES (%s, %s)
                """,
                (migration.migration_id, checksum),
            )
            connection.commit()
            applied.append(migration.migration_id)

        return tuple(applied)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.execute("SELECT pg_advisory_unlock(%s)", (_MIGRATION_LOCK_ID,))


def run() -> None:
    config = load_application_config()
    with psycopg.connect(config.postgres.dsn) as connection:
        applied = apply_migrations(connection)
    print(f"NAPMS migrations applied: {len(applied)}")
