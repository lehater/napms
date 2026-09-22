from importlib.resources import files
from typing import Any

from psycopg import Connection


def migrate(connection: Connection[Any]) -> None:
    sql = (
        files("napms.contexts.business_connectivity.infrastructure.persistence.postgres")
        .joinpath("migrations/001_business_connectivity.sql")
        .read_text(encoding="utf-8")
    )
    connection.execute(sql)
