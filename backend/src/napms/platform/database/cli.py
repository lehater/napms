from __future__ import annotations

import os

import psycopg

from napms.platform.database.migration import migrate


def run() -> None:
    dsn = os.environ.get("NAPMS_DATABASE_DSN", "").strip()
    if not dsn:
        raise SystemExit("NAPMS_DATABASE_DSN is required")
    with psycopg.connect(dsn) as connection:
        migrate(connection)
