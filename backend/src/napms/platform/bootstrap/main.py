from __future__ import annotations

import os

import psycopg
import uvicorn

from napms.platform.composition import RuntimeConfig, build_app
from napms.platform.database.migration import verify


def run() -> None:
    config = RuntimeConfig.from_environment()
    with psycopg.connect(config.database_dsn) as connection:
        verify(connection)
    uvicorn.run(
        build_app(config),
        host=os.environ.get("NAPMS_HTTP_HOST", "127.0.0.1"),
        port=int(os.environ.get("NAPMS_HTTP_PORT", "8000")),
    )
