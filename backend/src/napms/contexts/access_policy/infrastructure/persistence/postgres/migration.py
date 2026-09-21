from importlib.resources import files
from typing import Any

from psycopg import Connection


def migrate(connection: Connection[Any]) -> None:
    sql = (
        files("napms.contexts.access_policy.infrastructure.persistence.postgres")
        .joinpath("migrations/001_access_policy.sql")
        .read_text(encoding="utf-8")
    )
    connection.execute(sql)
