from importlib.resources import files
from typing import Any

from psycopg import Connection


def migrate(connection: Connection[Any]) -> None:
    sql = (
        files("napms.contexts.resource_catalogue.infrastructure.persistence.postgres")
        .joinpath("migrations/001_resource_catalogue.sql")
        .read_text(encoding="utf-8")
    )
    connection.execute(sql)
