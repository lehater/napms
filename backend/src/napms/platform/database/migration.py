from __future__ import annotations

from dataclasses import dataclass
import hashlib
from importlib.resources import files
from typing import Any

from psycopg import Connection

from napms.contexts.access_policy.infrastructure.persistence.postgres.migration import (
    migrate as migrate_access_policy,
)
from napms.contexts.application_communication_catalogue.infrastructure.persistence.postgres.migration import (
    migrate as migrate_communication_catalogue,
)
from napms.contexts.application_deployment.infrastructure.persistence.postgres.migration import (
    migrate as migrate_deployment,
)
from napms.contexts.business_connectivity.infrastructure.persistence.postgres.migration import (
    migrate as migrate_business_connectivity,
)
from napms.contexts.resource_catalogue.infrastructure.persistence.postgres.migration import (
    migrate as migrate_resource_catalogue,
)

_ADVISORY_LOCK = 5_241_771


@dataclass(frozen=True)
class Migration:
    migration_id: str
    checksum: str


def migrate(connection: Connection[Any]) -> None:
    connection.execute("SELECT pg_advisory_xact_lock(%s)", (_ADVISORY_LOCK,))
    _ensure_metadata(connection)
    steps = (
        ("resource-catalogue/001", migrate_resource_catalogue),
        ("communication-catalogue/001", migrate_communication_catalogue),
        ("deployment/001", migrate_deployment),
        ("business-connectivity/001", migrate_business_connectivity),
        ("access-policy/001", migrate_access_policy),
    )
    for migration_id, step in steps:
        step(connection)
        _record(connection, migration_id, _module_checksum(migration_id))
    sql = (
        files("napms.platform.database")
        .joinpath("migrations/001_idempotency.sql")
        .read_text(encoding="utf-8")
    )
    connection.execute(sql)
    _record(connection, "application-edge/001", _checksum(sql))


def verify(connection: Connection[Any]) -> None:
    _ensure_metadata(connection)
    expected = {
        migration_id: _module_checksum(migration_id)
        for migration_id in (
            "resource-catalogue/001",
            "communication-catalogue/001",
            "deployment/001",
            "business-connectivity/001",
            "access-policy/001",
        )
    }
    sql = (
        files("napms.platform.database")
        .joinpath("migrations/001_idempotency.sql")
        .read_text(encoding="utf-8")
    )
    expected["application-edge/001"] = _checksum(sql)
    rows = connection.execute(
        "SELECT migration_id, checksum FROM application_edge.schema_migration"
    ).fetchall()
    actual = {row[0]: row[1] for row in rows}
    if actual != expected:
        raise RuntimeError("database schema migration set/checksum mismatch")


def _ensure_metadata(connection: Connection[Any]) -> None:
    connection.execute("CREATE SCHEMA IF NOT EXISTS application_edge")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS application_edge.schema_migration (
            migration_id text PRIMARY KEY,
            checksum text NOT NULL,
            applied_at timestamptz NOT NULL DEFAULT transaction_timestamp()
        )
        """
    )


def _record(connection: Connection[Any], migration_id: str, checksum: str) -> None:
    row = connection.execute(
        """
        INSERT INTO application_edge.schema_migration (migration_id, checksum)
        VALUES (%s, %s)
        ON CONFLICT (migration_id) DO UPDATE SET migration_id = EXCLUDED.migration_id
        RETURNING checksum
        """,
        (migration_id, checksum),
    ).fetchone()
    assert row is not None
    if row[0] != checksum:
        raise RuntimeError(f"immutable migration checksum mismatch: {migration_id}")


def _module_checksum(migration_id: str) -> str:
    package, filename = {
        "resource-catalogue/001": (
            "napms.contexts.resource_catalogue.infrastructure.persistence.postgres",
            "migrations/001_resource_catalogue.sql",
        ),
        "communication-catalogue/001": (
            "napms.contexts.application_communication_catalogue.infrastructure.persistence.postgres",
            "migrations/001_application_communication_catalogue.sql",
        ),
        "deployment/001": (
            "napms.contexts.application_deployment.infrastructure.persistence.postgres",
            "migrations/001_application_deployment.sql",
        ),
        "business-connectivity/001": (
            "napms.contexts.business_connectivity.infrastructure.persistence.postgres",
            "migrations/001_business_connectivity.sql",
        ),
        "access-policy/001": (
            "napms.contexts.access_policy.infrastructure.persistence.postgres",
            "migrations/001_access_policy.sql",
        ),
    }[migration_id]
    return _checksum(files(package).joinpath(filename).read_text(encoding="utf-8"))


def _checksum(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()
