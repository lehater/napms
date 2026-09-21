from __future__ import annotations

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


def migrate(connection: Connection[Any]) -> None:
    connection.execute("SELECT pg_advisory_xact_lock(%s)", (_ADVISORY_LOCK,))
    migrate_resource_catalogue(connection)
    migrate_communication_catalogue(connection)
    migrate_deployment(connection)
    migrate_business_connectivity(connection)
    migrate_access_policy(connection)
    sql = (
        files("napms.platform.database")
        .joinpath("migrations/001_idempotency.sql")
        .read_text(encoding="utf-8")
    )
    connection.execute(sql)
