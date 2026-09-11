import hashlib
from dataclasses import dataclass
from importlib.resources import files
from typing import Iterable

import psycopg

from napms.composition.config import ApplicationConfig


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
        "napms.contexts.authority_management.infrastructure.persistence.postgres",
        "migrations/0001_authority_assignments.sql",
    ),
    Migration(
        "application-catalogue/0001",
        "napms.contexts.application_catalogue.infrastructure.persistence.postgres",
        "migrations/0001_application_catalogue.sql",
    ),
    Migration(
        "application-catalogue/0002",
        "napms.contexts.application_catalogue.infrastructure.persistence.postgres",
        "migrations/0002_display_metadata.sql",
    ),
    Migration(
        "application-catalogue/0003",
        "napms.contexts.application_catalogue.infrastructure.persistence.postgres",
        "migrations/0003_catalogue_hierarchy.sql",
    ),
    Migration(
        "application-catalogue/0004",
        "napms.contexts.application_catalogue.infrastructure.persistence.postgres",
        "migrations/0004_curation_write_support.sql",
    ),
    Migration(
        "application-catalogue/0005",
        "napms.contexts.application_catalogue.infrastructure.persistence.postgres",
        "migrations/0005_application_catalogue_target.sql",
    ),
    Migration(
        "resource-catalogue/0001",
        "napms.contexts.resource_catalogue.infrastructure.persistence.postgres",
        "migrations/0001_resource_catalogue.sql",
    ),
    Migration(
        "resource-catalogue/0002",
        "napms.contexts.resource_catalogue.infrastructure.persistence.postgres",
        "migrations/0002_resource_scope_affiliations.sql",
    ),
    Migration(
        "resource-catalogue/0003",
        "napms.contexts.resource_catalogue.infrastructure.persistence.postgres",
        "migrations/0003_curation_write_support.sql",
    ),
    Migration(
        "connectivity-requirements/0001",
        "napms.contexts.connectivity_requirements.infrastructure.persistence.postgres",
        "migrations/0001_connectivity_requirements.sql",
    ),
    Migration(
        "connectivity-decision/0001",
        "napms.contexts.connectivity_decision.infrastructure.persistence.postgres",
        "migrations/0001_connectivity_decisions.sql",
    ),
    Migration(
        "technical-access-evidence/0001",
        "napms.contexts.technical_access_evidence.infrastructure.persistence.postgres",
        "migrations/0001_evidence_sets.sql",
    ),
    Migration(
        "network-enforcement-placement/0001",
        "napms.contexts.network_enforcement_placement.infrastructure.persistence.postgres",
        "migrations/0001_knowledge_captures.sql",
    ),
)


def _ordered_unique(migrations: Iterable[Migration]) -> tuple[Migration, ...]:
    values = tuple(migrations)
    ids = tuple(item.migration_id for item in values)
    if len(ids) != len(set(ids)):
        raise MigrationError("migration ids must be unique")
    return values


def apply_postgres_migrations(
    connection,
    migrations: Iterable[Migration] = MIGRATIONS,
) -> tuple[str, ...]:
    ordered = _ordered_unique(migrations)
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


def apply_greenfield_migrations(config: ApplicationConfig) -> tuple[str, ...]:
    with psycopg.connect(config.postgres.dsn) as connection:
        return apply_postgres_migrations(connection)
