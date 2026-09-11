"""Compatibility facade; migration entrypoint lives in napms.bootstrap.migrations."""

from napms.bootstrap.migrations import run

__all__ = ["run"]
